"""In-process cache of the assessment reference tables.

The reference tables are small -- a few hundred rows in total -- and only
change when the importer runs, so every request loading them from PostgreSQL
would be wasted work.  They are cached for a few minutes and can be dropped
immediately after an import.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from sqlmodel import Session, col, select

from app.model.reference import (
    Assessment,
    AssessmentYear,
    GradeLevel,
    PerformanceLevel,
    PerformanceLevelScheme,
    Program,
    StudentGroup,
    SubscoreDefinition,
)
from app.model.reports import (
    GradePublic,
    LevelPublic,
    LevelSchemePublic,
    StudentGroupPublic,
    SubscorePublic,
)

CACHE_TTL_SECONDS = 300.0


@dataclass(frozen=True, slots=True)
class ReferenceData:
    """A snapshot of every reference table."""

    expires_at: float
    assessments: Mapping[int, Assessment]
    assessment_years: Mapping[tuple[int, int], AssessmentYear]
    schemes: Mapping[str, LevelSchemePublic]
    subscores: Mapping[tuple[int, int], tuple[SubscorePublic, ...]]
    student_groups: Mapping[tuple[Program, int], StudentGroupPublic]
    grades: Mapping[str, GradePublic]

    def assessment(self, test_id: int) -> Assessment | None:
        return self.assessments.get(test_id)

    def scheme_for(self, test_id: int, test_year: int) -> LevelSchemePublic | None:
        year_row = self.assessment_years.get((test_id, test_year))
        return self.schemes.get(year_row.level_scheme_code) if year_row else None

    def subscores_for(self, test_id: int, test_year: int) -> tuple[SubscorePublic, ...]:
        return self.subscores.get((test_id, test_year), ())

    def group_name(self, program: Program, student_group_id: int) -> str:
        group = self.student_groups.get((program, student_group_id))
        return group.name if group else f"Student group {student_group_id}"

    def groups_for(self, program: Program) -> list[StudentGroupPublic]:
        return sorted(
            (g for g in self.student_groups.values() if g.program == program),
            key=lambda g: g.sort_order,
        )


_lock = threading.Lock()
_cache: ReferenceData | None = None


def reset_reference_cache() -> None:
    """Drop the cached snapshot; called after an import changes the tables."""
    global _cache
    with _lock:
        _cache = None


def _load(session: Session) -> ReferenceData:
    levels: dict[str, list[LevelPublic]] = {}
    for level in session.exec(
        select(PerformanceLevel).order_by(
            col(PerformanceLevel.scheme_code), col(PerformanceLevel.level_number)
        )
    ).all():
        levels.setdefault(level.scheme_code, []).append(
            LevelPublic(
                level_number=level.level_number,
                name=level.name,
                short_name=level.short_name,
                description=level.description,
            )
        )

    schemes = {
        scheme.code: LevelSchemePublic(
            code=scheme.code,
            name=scheme.name,
            level_count=scheme.level_count,
            proficient_from_level=scheme.proficient_from_level,
            description=scheme.description,
            levels=levels.get(scheme.code, []),
        )
        for scheme in session.exec(select(PerformanceLevelScheme)).all()
    }

    subscores: dict[tuple[int, int], list[SubscorePublic]] = {}
    for definition in session.exec(
        select(SubscoreDefinition).order_by(col(SubscoreDefinition.sort_order))
    ).all():
        scheme = schemes.get(definition.band_scheme_code)
        if scheme is None:
            continue
        subscores.setdefault((definition.test_id, definition.test_year), []).append(
            SubscorePublic(
                code=definition.code,
                kind=definition.kind,
                name=definition.name,
                reports_mean_scale_score=definition.reports_mean_scale_score,
                band_scheme=scheme,
                sort_order=definition.sort_order,
            )
        )

    return ReferenceData(
        expires_at=time.monotonic() + CACHE_TTL_SECONDS,
        assessments={
            assessment.test_id: assessment
            for assessment in session.exec(select(Assessment)).all()
        },
        assessment_years={
            (row.test_id, row.test_year): row
            for row in session.exec(select(AssessmentYear)).all()
        },
        schemes=schemes,
        subscores={key: tuple(value) for key, value in subscores.items()},
        student_groups={
            (group.program, group.student_group_id): StudentGroupPublic.model_validate(
                group
            )
            for group in session.exec(select(StudentGroup)).all()
        },
        grades={
            grade.code: GradePublic.model_validate(grade)
            for grade in session.exec(
                select(GradeLevel).order_by(col(GradeLevel.sort_order))
            ).all()
        },
    )


def reference_data(session: Session) -> ReferenceData:
    """Return the cached reference snapshot, reloading it when stale."""
    global _cache
    cached = _cache
    if cached is not None and cached.expires_at > time.monotonic():
        return cached
    with _lock:
        cached = _cache
        if cached is not None and cached.expires_at > time.monotonic():
            return cached
        _cache = _load(session)
        return _cache


def sorted_assessments(
    data: ReferenceData, test_ids: Sequence[int]
) -> list[Assessment]:
    """Order a set of test ids the way the state's menus present them."""
    found = [
        data.assessments[test_id] for test_id in test_ids if test_id in data.assessments
    ]
    return sorted(found, key=lambda assessment: assessment.sort_order)
