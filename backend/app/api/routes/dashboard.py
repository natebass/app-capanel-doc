"""Dashboard endpoints.

Both endpoints read from very wide assessment tables (100+ columns), so every
query here projects only the columns it needs instead of hydrating whole ORM
rows, and the student group lookup tables — small, static reference data — are
resolved in SQL so a freshly imported group is picked up immediately.  Only the
group *display names* are cached in process, where a stale entry is cosmetic.
"""

import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy import ColumnElement, case, func
from sqlalchemy.orm import load_only
from sqlmodel import Session, col, or_, select

from app.api.deps import SessionDep
from app.model.assessments import (
    CaasppStudentGroup,
    CastResult,
    ElpacStudentGroup,
    IaElpacResult,
    SbResult,
)
from app.model.dashboard import (
    DashboardSummaryResponse,
    EquityGroupSummary,
    EquityReportResponse,
    IndicatorSummary,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

STATEWIDE_CDS = "00000000000000"
ALL_STUDENTS_GROUPS = {"ALL", "1"}
ALL_STUDENTS_LABELS = ("all student", "all students")
DEFAULT_GRADE = "13"
CAST_TEST_ID = "3"
ELPAC_INITIAL_TEST_ID = "elpac_initial"

# Assessment reference data changes only when state data is re-imported, so the
# responses are safe to cache for a few minutes in the browser and any proxy.
RESPONSE_MAX_AGE_SECONDS = 300
_LOOKUP_CACHE_TTL_SECONDS = 600.0

# The result tables carry 100+ columns each; the summary only reads these, so
# every query defers the rest instead of hydrating whole rows.
_SB_SUMMARY_COLUMNS: tuple[Any, ...] = (
    SbResult.test_id,
    SbResult.test_type,
    SbResult.grade,
    SbResult.total_students_enrolled,
    SbResult.total_students_tested,
    SbResult.mean_scale_score,
    SbResult.percentage_standard_met_and_above,
    SbResult.percentage_standard_not_met,
    SbResult.percentage_standard_nearly_met,
    SbResult.percentage_standard_met,
    SbResult.percentage_standard_exceeded,
)
_CAST_SUMMARY_COLUMNS: tuple[Any, ...] = (
    CastResult.grade,
    CastResult.total_students_enrolled,
    CastResult.total_students_tested,
    CastResult.mean_scale_score,
    CastResult.percentage_standard_met_and_above,
    CastResult.percentage_standard_not_met,
    CastResult.percentage_standard_nearly_met,
    CastResult.percentage_standard_met,
    CastResult.percentage_standard_exceeded,
)
_ELPAC_SUMMARY_COLUMNS: tuple[Any, ...] = (
    IaElpacResult.grade,
    IaElpacResult.total_students_enrolled,
    IaElpacResult.total_students_tested,
    IaElpacResult.overall_mean_scale_score,
    IaElpacResult.novice_el_perf_lvl_pcnt,
    IaElpacResult.intermediate_el_perf_lvl_pcnt,
    IaElpacResult.ifep_perf_lvl_pcnt,
)


@dataclass(frozen=True, slots=True)
class _StudentGroupNames:
    """Cached display names for the CAASPP and ELPAC student group lookups.

    Only names live here.  Which student group ids count as "All Students" is
    resolved in SQL on every request (see `_caaspp_group_filter`), because a
    stale id set would silently drop indicators from the summary, whereas a
    stale name merely falls back to "Group <id>".
    """

    expires_at: float
    caaspp: Mapping[str, str]
    elpac: Mapping[str, str]


_names_lock = threading.Lock()
_names_cache: _StudentGroupNames | None = None


def reset_student_group_cache() -> None:
    """Drop the cached group display names (used after importing or seeding)."""
    global _names_cache
    with _names_lock:
        _names_cache = None


def _load_student_group_names(session: Session) -> _StudentGroupNames:
    caaspp: dict[str, str] = {}
    for caaspp_group in session.exec(select(CaasppStudentGroup)).all():
        group_id = caaspp_group.demographic_id
        caaspp[group_id] = (
            caaspp_group.student_group or caaspp_group.demographic_name or group_id
        )

    elpac: dict[str, str] = {}
    for elpac_group in session.exec(select(ElpacStudentGroup)).all():
        group_id = elpac_group.student_group_id
        elpac[group_id] = elpac_group.student_group_name or group_id

    return _StudentGroupNames(
        expires_at=time.monotonic() + _LOOKUP_CACHE_TTL_SECONDS,
        caaspp=caaspp,
        elpac=elpac,
    )


def _student_group_names(session: Session) -> _StudentGroupNames:
    global _names_cache
    cached = _names_cache
    if cached is not None and cached.expires_at > time.monotonic():
        return cached

    with _names_lock:
        cached = _names_cache
        if cached is not None and cached.expires_at > time.monotonic():
            return cached
        names = _load_student_group_names(session)
        _names_cache = names
        return names


def _caaspp_group_filter(group_column: Any, student_group: str) -> ColumnElement[bool]:
    """Restrict to one CAASPP student group, resolving "All Students" in SQL."""
    normalized_group = _normalize_student_group(student_group)
    if normalized_group != "ALL":
        return group_column == normalized_group

    all_students = (
        select(CaasppStudentGroup.demographic_id)
        .where(
            or_(
                func.lower(func.coalesce(CaasppStudentGroup.student_group, "")).in_(
                    ALL_STUDENTS_LABELS
                ),
                func.lower(func.coalesce(CaasppStudentGroup.demographic_name, "")).in_(
                    ALL_STUDENTS_LABELS
                ),
            )
        )
        .scalar_subquery()
    )
    return or_(group_column == "1", group_column.in_(all_students))


def _elpac_group_filter(group_column: Any, student_group: str) -> ColumnElement[bool]:
    """Restrict to one ELPAC student group, resolving "All Students" in SQL."""
    normalized_group = _normalize_student_group(student_group)
    if normalized_group != "ALL":
        return group_column == normalized_group

    all_students = (
        select(ElpacStudentGroup.student_group_id)
        .where(
            func.lower(func.coalesce(ElpacStudentGroup.student_group_name, "")).in_(
                ALL_STUDENTS_LABELS
            )
        )
        .scalar_subquery()
    )
    return or_(group_column == "1", group_column.in_(all_students))


def _normalize_cds(cds: str) -> str:
    normalized_cds = cds.strip()
    return normalized_cds or STATEWIDE_CDS


def _normalize_student_group(student_group: str) -> str:
    normalized_group = student_group.strip()
    return (
        "ALL" if normalized_group.upper() in ALL_STUDENTS_GROUPS else normalized_group
    )


def _stringify_number(value: Decimal | int | None) -> str | None:
    return None if value is None else str(value)


def _float_or_zero(value: Decimal | None) -> float:
    return 0.0 if value is None else float(value)


def _cds_filter(column: Any, cds_code: str) -> ColumnElement[bool]:
    """Match one CDS code, or statewide rows including orphaned NULL ones."""
    if cds_code == STATEWIDE_CDS:
        return or_(column == cds_code, column.is_(None))
    return column == cds_code


def _grade(value: str | None) -> str:
    return DEFAULT_GRADE if value is None else str(value)


def _parse_year(reporting_year: str) -> int:
    try:
        return int(reporting_year)
    except ValueError:
        raise HTTPException(
            status_code=422, detail="reportingYear must be a four digit year"
        )


def _caaspp_levels(
    not_met: Decimal | None,
    nearly_met: Decimal | None,
    met: Decimal | None,
    exceeded: Decimal | None,
) -> dict[str, float]:
    return {
        "Standard Not Met (Level 1)": _float_or_zero(not_met),
        "Standard Nearly Met (Level 2)": _float_or_zero(nearly_met),
        "Standard Met (Level 3)": _float_or_zero(met),
        "Standard Exceeded (Level 4)": _float_or_zero(exceeded),
    }


def _set_cache_headers(response: Response) -> None:
    response.headers["Cache-Control"] = (
        f"public, max-age={RESPONSE_MAX_AGE_SECONDS}, "
        f"stale-while-revalidate={RESPONSE_MAX_AGE_SECONDS}"
    )


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    session: SessionDep,
    response: Response,
    cds: str,
    reporting_year: str = Query("2025", alias="reportingYear"),
    student_group: str = Query("ALL", alias="studentGroup"),
) -> Any:
    """
    Get all test summaries for a CDS code within a specific reporting year and student group.
    """
    cds_code = _normalize_cds(cds)
    test_year = _parse_year(reporting_year)

    indicators: list[IndicatorSummary] = []

    # 1. Smarter Balanced — ELA (test_id 1) and Math (test_id 2).
    sb_rows = session.exec(
        select(SbResult)
        .options(load_only(*_SB_SUMMARY_COLUMNS))
        .where(
            _cds_filter(SbResult.cds_code, cds_code),
            SbResult.test_year == test_year,
            _caaspp_group_filter(col(SbResult.student_group_id), student_group),
        )
        .order_by(col(SbResult.test_id), col(SbResult.grade))
    ).all()
    for sb_row in sb_rows:
        indicators.append(
            IndicatorSummary(
                test_id=str(sb_row.test_id),
                test_type=str(sb_row.test_type) if sb_row.test_type else "SB",
                grade=_grade(sb_row.grade),
                students_enrolled=str(sb_row.total_students_enrolled or 0),
                students_tested=str(sb_row.total_students_tested or 0),
                overall_mean_scale_score=_stringify_number(sb_row.mean_scale_score),
                overall_met_and_above_pct=_stringify_number(
                    sb_row.percentage_standard_met_and_above
                ),
                levels=_caaspp_levels(
                    sb_row.percentage_standard_not_met,
                    sb_row.percentage_standard_nearly_met,
                    sb_row.percentage_standard_met,
                    sb_row.percentage_standard_exceeded,
                ),
            )
        )

    # 2. Science (CAST). The dashboard addresses CAST as test 3 regardless of the
    # per-row test id, so the summary and the equity report stay in step.
    cast_rows = session.exec(
        select(CastResult)
        .options(load_only(*_CAST_SUMMARY_COLUMNS))
        .where(
            _cds_filter(CastResult.cds_code, cds_code),
            CastResult.test_year == test_year,
            _caaspp_group_filter(col(CastResult.student_group_id), student_group),
        )
        .order_by(col(CastResult.grade))
    ).all()
    for cast_row in cast_rows:
        indicators.append(
            IndicatorSummary(
                test_id=CAST_TEST_ID,
                test_type="CAST",
                grade=_grade(cast_row.grade),
                students_enrolled=str(cast_row.total_students_enrolled or 0),
                students_tested=str(cast_row.total_students_tested or 0),
                overall_mean_scale_score=_stringify_number(cast_row.mean_scale_score),
                overall_met_and_above_pct=_stringify_number(
                    cast_row.percentage_standard_met_and_above
                ),
                levels=_caaspp_levels(
                    cast_row.percentage_standard_not_met,
                    cast_row.percentage_standard_nearly_met,
                    cast_row.percentage_standard_met,
                    cast_row.percentage_standard_exceeded,
                ),
            )
        )

    # 3. Initial ELPAC.
    elpac_rows = session.exec(
        select(IaElpacResult)
        .options(load_only(*_ELPAC_SUMMARY_COLUMNS))
        .where(
            _cds_filter(IaElpacResult.cds_code, cds_code),
            IaElpacResult.test_year == test_year,
            _elpac_group_filter(col(IaElpacResult.student_group_id), student_group),
        )
        .order_by(col(IaElpacResult.grade))
    ).all()
    for elpac_row in elpac_rows:
        indicators.append(
            IndicatorSummary(
                test_id=ELPAC_INITIAL_TEST_ID,
                test_type="ELPAC",
                grade=_grade(elpac_row.grade),
                students_enrolled=str(elpac_row.total_students_enrolled or 0),
                students_tested=str(elpac_row.total_students_tested or 0),
                overall_mean_scale_score=_stringify_number(
                    elpac_row.overall_mean_scale_score
                ),
                overall_met_and_above_pct=None,
                levels={
                    "Novice English Learner": _float_or_zero(
                        elpac_row.novice_el_perf_lvl_pcnt
                    ),
                    "Intermediate English Learner": _float_or_zero(
                        elpac_row.intermediate_el_perf_lvl_pcnt
                    ),
                    "Initial Fluent English Proficient (IFEP)": _float_or_zero(
                        elpac_row.ifep_perf_lvl_pcnt
                    ),
                },
            )
        )

    _set_cache_headers(response)
    return {"cds": cds_code, "test_year": reporting_year, "indicators": indicators}


def _weighted_met_and_above(
    met_and_above: Any, tested: Any
) -> tuple[ColumnElement[Any], ColumnElement[Any]]:
    """Students tested, and their tested-count-weighted met-and-above percentage."""
    scored_students = func.sum(
        case((met_and_above.is_not(None), func.coalesce(tested, 0)), else_=0)
    )
    weighted_pct = func.sum(
        func.coalesce(met_and_above, 0) * func.coalesce(tested, 0)
    ) / func.nullif(scored_students, 0)
    return func.sum(func.coalesce(tested, 0)), weighted_pct


@router.get("/equity", response_model=EquityReportResponse)
def get_equity_report(
    session: SessionDep,
    response: Response,
    cds: str,
    test_id: str = Query(..., alias="testId"),
    reporting_year: str = Query("2025", alias="reportingYear"),
) -> Any:
    """
    Get student group breakdown for a specific test and CDS code.
    """
    cds_code = _normalize_cds(cds)
    test_year = _parse_year(reporting_year)
    names_cache = _student_group_names(session)
    groups: list[EquityGroupSummary] = []

    if test_id == CAST_TEST_ID:
        # Science is reported from its own table, not from sb_results.
        tested, weighted_pct = _weighted_met_and_above(
            CastResult.percentage_standard_met_and_above,
            CastResult.total_students_tested,
        )
        rows = session.exec(
            select(
                CastResult.student_group_id,
                tested.label("students_tested"),
                weighted_pct.label("overall_met_and_above_pct"),
            )
            .where(
                _cds_filter(CastResult.cds_code, cds_code),
                CastResult.test_year == test_year,
            )
            .group_by(CastResult.student_group_id)
        ).all()
        names = names_cache.caaspp
    elif test_id == ELPAC_INITIAL_TEST_ID:
        # Initial ELPAC has no met-and-above measure; report tested counts only.
        rows = [
            (student_group_id, students_tested, None)
            for student_group_id, students_tested in session.exec(
                select(
                    IaElpacResult.student_group_id,
                    func.sum(
                        func.coalesce(IaElpacResult.total_students_tested, 0)
                    ).label("students_tested"),
                )
                .where(
                    _cds_filter(IaElpacResult.cds_code, cds_code),
                    IaElpacResult.test_year == test_year,
                )
                .group_by(IaElpacResult.student_group_id)
            ).all()
        ]
        names = names_cache.elpac
    elif test_id.isdigit():
        tested, weighted_pct = _weighted_met_and_above(
            SbResult.percentage_standard_met_and_above,
            SbResult.total_students_tested,
        )
        rows = session.exec(
            select(
                SbResult.student_group_id,
                tested.label("students_tested"),
                weighted_pct.label("overall_met_and_above_pct"),
            )
            .where(
                _cds_filter(SbResult.cds_code, cds_code),
                SbResult.test_id == int(test_id),
                SbResult.test_year == test_year,
            )
            .group_by(SbResult.student_group_id)
        ).all()
        names = names_cache.caaspp
    else:
        rows = []
        names = {}

    for student_group_id, students_tested, overall_met_and_above_pct in rows:
        groups.append(
            EquityGroupSummary(
                student_group=names.get(student_group_id)
                or f"Group {student_group_id}",
                overall_met_and_above_pct=_stringify_number(overall_met_and_above_pct),
                students_tested=str(students_tested or 0),
            )
        )

    groups.sort(key=lambda group: group.student_group)

    _set_cache_headers(response)
    return {
        "cds": cds_code,
        "test_id": test_id,
        "test_year": reporting_year,
        "groups": groups,
    }
