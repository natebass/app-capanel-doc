from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Query
from sqlalchemy import case, func
from sqlmodel import or_, select

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
ALL_STUDENTS_LABELS = {"all students", "all student"}


def _normalize_cds(cds: str) -> str:
    normalized_cds = cds.strip()
    return normalized_cds or STATEWIDE_CDS


def _normalize_student_group(student_group: str) -> str:
    normalized_group = student_group.strip()
    return "ALL" if normalized_group.upper() in ALL_STUDENTS_GROUPS else normalized_group


def _stringify_number(value: Decimal | int | None) -> str | None:
    return None if value is None else str(value)


def _float_or_zero(value: Decimal | None) -> float:
    return 0.0 if value is None else float(value)


def _resolve_caaspp_student_group_ids(
    session: SessionDep, student_group: str
) -> list[str]:
    normalized_group = _normalize_student_group(student_group)
    if normalized_group != "ALL":
        return [normalized_group]

    rows = session.exec(
        select(CaasppStudentGroup.demographic_id).where(
            func.lower(func.coalesce(CaasppStudentGroup.student_group, "")).in_(
                ALL_STUDENTS_LABELS
            )
            | func.lower(func.coalesce(CaasppStudentGroup.demographic_name, "")).in_(
                ALL_STUDENTS_LABELS
            )
        )
    ).all()

    candidate_ids = {row for row in rows if row}
    candidate_ids.add("1")
    return sorted(candidate_ids)


def _resolve_elpac_student_group_ids(
    session: SessionDep, student_group: str
) -> list[str]:
    normalized_group = _normalize_student_group(student_group)
    if normalized_group != "ALL":
        return [normalized_group]

    rows = session.exec(
        select(ElpacStudentGroup.student_group_id).where(
            func.lower(func.coalesce(ElpacStudentGroup.student_group_name, "")).in_(
                ALL_STUDENTS_LABELS
            )
        )
    ).all()

    candidate_ids = {row for row in rows if row}
    candidate_ids.add("1")
    return sorted(candidate_ids)


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    session: SessionDep,
    cds: str,
    reporting_year: str = Query("2025", alias="reportingYear"),
    student_group: str = Query("ALL", alias="studentGroup"),
) -> Any:
    """
    Get all test summaries for a CDS code within a specific reporting year and student group.
    """
    indicators = []

    # Standardize CDS code
    cds_code = _normalize_cds(cds)
    caaspp_student_group_ids = _resolve_caaspp_student_group_ids(session, student_group)
    elpac_student_group_ids = _resolve_elpac_student_group_ids(session, student_group)

    # 1. Fetch Smarter Balanced (ELA/Math)
    # Build the CDS filter condition
    # If Statewide, also include records where cds_code is NULL (orphaned statewide data)
    if cds_code == STATEWIDE_CDS:
        cds_filter = or_(SbResult.cds_code == cds_code, SbResult.cds_code == None)
    else:
        cds_filter = SbResult.cds_code == cds_code

    # ELA (testId = 1), Math (testId = 2)
    sb_results = session.exec(
        select(SbResult).where(
            cds_filter,
            SbResult.test_year == int(reporting_year),
            SbResult.student_group_id.in_(caaspp_student_group_ids),
        )
    ).all()
    for sb_row in sb_results:
        ind = IndicatorSummary(
            test_id=str(sb_row.test_id),
            test_type=str(sb_row.test_type) if sb_row.test_type else "SB",
            grade=str(sb_row.grade) if sb_row.grade is not None else "13",
            students_enrolled=str(sb_row.total_students_enrolled or 0),
            students_tested=str(sb_row.total_students_tested or 0),
            overall_mean_scale_score=_stringify_number(sb_row.mean_scale_score),
            overall_met_and_above_pct=_stringify_number(
                sb_row.percentage_standard_met_and_above
            ),
            levels={
                "Standard Not Met (Level 1)": _float_or_zero(
                    sb_row.percentage_standard_not_met
                ),
                "Standard Nearly Met (Level 2)": _float_or_zero(
                    sb_row.percentage_standard_nearly_met
                ),
                "Standard Met (Level 3)": _float_or_zero(sb_row.percentage_standard_met),
                "Standard Exceeded (Level 4)": _float_or_zero(
                    sb_row.percentage_standard_exceeded
                ),
            },
        )
        indicators.append(ind)

    # 2. Fetch Science (CAST) (usually testId = 3 or 4)
    if cds_code == STATEWIDE_CDS:
        cast_filter = or_(CastResult.cds_code == cds_code, CastResult.cds_code == None)
    else:
        cast_filter = CastResult.cds_code == cds_code

    cast_results = session.exec(
        select(CastResult).where(
            cast_filter,
            CastResult.test_year == int(reporting_year),
            CastResult.student_group_id.in_(caaspp_student_group_ids),
        )
    ).all()
    for cast_row in cast_results:
        ind = IndicatorSummary(
            test_id="3",  # Usually 3 or 4
            test_type="CAST",
            grade=str(cast_row.grade) if cast_row.grade is not None else "13",
            students_enrolled=str(cast_row.total_students_enrolled or 0),
            students_tested=str(cast_row.total_students_tested or 0),
            overall_mean_scale_score=_stringify_number(cast_row.mean_scale_score),
            overall_met_and_above_pct=_stringify_number(
                cast_row.percentage_standard_met_and_above
            ),
            levels={
                "Standard Not Met (Level 1)": _float_or_zero(
                    cast_row.percentage_standard_not_met
                ),
                "Standard Nearly Met (Level 2)": _float_or_zero(
                    cast_row.percentage_standard_nearly_met
                ),
                "Standard Met (Level 3)": _float_or_zero(cast_row.percentage_standard_met),
                "Standard Exceeded (Level 4)": _float_or_zero(
                    cast_row.percentage_standard_exceeded
                ),
            },
        )
        indicators.append(ind)

    # 3. Fetch Initial ELPAC
    if cds_code == STATEWIDE_CDS:
        elpac_filter = or_(IaElpacResult.cds_code == cds_code, IaElpacResult.cds_code == None)
    else:
        elpac_filter = IaElpacResult.cds_code == cds_code

    elpac_results = session.exec(
        select(IaElpacResult).where(
            elpac_filter,
            IaElpacResult.test_year == int(reporting_year),
            IaElpacResult.student_group_id.in_(elpac_student_group_ids),
        )
    ).all()
    for elpac_row in elpac_results:
        ind = IndicatorSummary(
            test_id="elpac_initial",
            test_type="ELPAC",
            grade=str(elpac_row.grade) if elpac_row.grade is not None else "13",
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
        indicators.append(ind)

    return {"cds": cds_code, "test_year": reporting_year, "indicators": indicators}


@router.get("/equity", response_model=EquityReportResponse)
def get_equity_report(
    session: SessionDep,
    cds: str,
    test_id: str = Query(..., alias="testId"),
    reporting_year: str = Query("2025", alias="reportingYear"),
) -> Any:
    """
    Get student group breakdown for a specific test and CDS code.
    """
    groups = []

    # Map student group IDs to names
    student_groups_map = {
        row.demographic_id: row.student_group or row.demographic_name or row.demographic_id
        for row in session.exec(select(CaasppStudentGroup)).all()
    }

    # Standardize CDS code
    cds_code = _normalize_cds(cds)

    # Build the CDS filter condition
    if cds_code == STATEWIDE_CDS:
        cds_filter = or_(SbResult.cds_code == cds_code, SbResult.cds_code == None)
    else:
        cds_filter = SbResult.cds_code == cds_code

    if test_id.isdigit():
        weighted_students = func.sum(
            case(
                (
                    SbResult.percentage_standard_met_and_above.is_not(None),
                    func.coalesce(SbResult.total_students_tested, 0),
                ),
                else_=0,
            )
        )
        weighted_pct = (
            func.sum(
                func.coalesce(SbResult.percentage_standard_met_and_above, 0)
                * func.coalesce(SbResult.total_students_tested, 0)
            )
            / func.nullif(weighted_students, 0)
        )

        aggregated_results = session.exec(
            select(
                SbResult.student_group_id,
                func.sum(func.coalesce(SbResult.total_students_tested, 0)).label(
                    "students_tested"
                ),
                weighted_pct.label("overall_met_and_above_pct"),
            ).where(
                cds_filter,
                SbResult.test_id == int(test_id),
                SbResult.test_year == int(reporting_year),
            ).group_by(SbResult.student_group_id)
        ).all()

        for student_group_id, students_tested, overall_met_and_above_pct in aggregated_results:
            group_name = (
                student_groups_map.get(student_group_id)
                or f"Group {student_group_id}"
            )
            groups.append(
                EquityGroupSummary(
                    student_group=group_name,
                    overall_met_and_above_pct=_stringify_number(
                        overall_met_and_above_pct
                    ),
                    students_tested=str(students_tested or 0),
                )
            )

    return {
        "cds": cds_code,
        "test_id": test_id,
        "test_year": reporting_year,
        "groups": groups,
    }
