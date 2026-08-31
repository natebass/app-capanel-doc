"""Can we reproduce what the state published?

The projection is only allowed to estimate a colour for a year the state has
not released if it can reproduce the years it has.  These tests replay real
published rows -- one for every distinct combination of status band, change
band, variant and grid that appears in the 2024-25 files -- hide the levels
and the colour, and check that the rules put them back exactly.

If any of these fail, the projection must not ship.
"""

from __future__ import annotations

import csv
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pytest
from sqlmodel import Session

from app.ingest.dashboard_reference import seed_dashboard_reference
from app.service.dashboard_projection import (
    DashboardRules,
    is_small_denominator,
    variant_for,
)

FIXTURES = Path(__file__).parent.parent / "fixtures" / "dashboard_files"

FILES = {
    "chronicdownload2099.txt": "CHRO",
    "suspdownload2099.txt": "SUSP",
    "graddownload2099.txt": "GRAD",
    "elpidownload2099.txt": "ELPI",
    "ccidownload2099.txt": "CCI",
    "eladownload2099.txt": "ELA",
    "mathdownload2099.txt": "MATH",
    "sciencedownload2099.txt": "SCIENCE",
}


@pytest.fixture(scope="module")
def rules(db: Session) -> DashboardRules:
    seed_dashboard_reference(db)
    db.commit()
    return DashboardRules.load(db)


def _decimal(raw: str | None) -> Decimal | None:
    value = (raw or "").strip()
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _published(row: dict[str, str], *names: str) -> int | None:
    for name in names:
        value = (row.get(name) or "").strip()
        if value:
            return None if value == "0" else int(value)
    return None


def _rows(name: str):
    with (FIXTURES / name).open(encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle, delimiter="\t")


def _judge(rules: DashboardRules, indicator: str, row: dict[str, str]):
    variant = variant_for(
        indicator,
        school_type=row.get("type"),
        high_school_cutpoints=(row.get("hscutpoints") or "").strip().upper() == "Y",
    )
    small = (row.get("smalldenom") or "").strip().upper() == "Y"
    return variant, rules.judge(
        indicator,
        variant=variant,
        curr_status=_decimal(row.get("currstatus")),
        change=_decimal(row.get("change")),
        small_denominator=small,
    )


@pytest.mark.parametrize(("name", "indicator"), sorted(FILES.items()))
def test_every_published_level_and_colour_is_reproduced(
    rules: DashboardRules, name: str, indicator: str
) -> None:
    counts = Counter()
    failures = []
    for row in _rows(name):
        _, judged = _judge(rules, indicator, row)

        for label, got, want in (
            ("status", judged.status_level, _published(row, "statuslevel")),
            (
                "change",
                judged.change_level,
                _published(row, "changelevel", "changeLevel"),
            ),
            ("color", judged.color, _published(row, "color")),
        ):
            if want is None:
                continue
            # A data-error row carries a state override, not a grid result.
            if label == "color" and (row.get("dataerrorflag") or "").strip() == "Y":
                continue
            counts[label] += 1
            if got != want:
                failures.append(
                    (label, row.get("cds"), row.get("studentgroup"), want, got)
                )

    assert counts["status"], f"{name} exercised no status bands"
    assert not failures, (
        f"{indicator}: {len(failures)} of {sum(counts.values())} disagreed with "
        f"the state; first few: {failures[:5]}"
    )


def test_the_small_denominator_grid_never_uses_the_extreme_change_bands(
    rules: DashboardRules,
) -> None:
    """Chronic, suspension and college/career collapse to three bands."""
    seen = Counter()
    for name, indicator in FILES.items():
        if indicator not in {"CHRO", "SUSP", "CCI"}:
            continue
        for row in _rows(name):
            if (row.get("smalldenom") or "").strip().upper() != "Y":
                continue
            _, judged = _judge(rules, indicator, row)
            if judged.change_level is not None:
                seen[judged.change_level] += 1
    assert seen, "no small-denominator rows in the fixtures"
    assert set(seen) <= {2, 3, 4}


def test_graduation_keeps_five_change_bands_on_a_small_denominator(
    rules: DashboardRules,
) -> None:
    seen = Counter()
    for row in _rows("graddownload2099.txt"):
        if (row.get("smalldenom") or "").strip().upper() != "Y":
            continue
        _, judged = _judge(rules, "GRAD", row)
        if judged.change_level is not None:
            seen[judged.change_level] += 1
    assert seen, "no small-denominator graduation rows in the fixtures"
    assert set(seen) - {2, 3, 4}, "graduation should still reach the outer bands"


def test_a_missing_prior_year_yields_no_change_and_no_colour(
    rules: DashboardRules,
) -> None:
    judged = rules.judge("CHRO", curr_status=Decimal("12.0"), change=None)
    assert judged.status_level == 2
    assert judged.change_level is None
    assert judged.color is None


def test_change_is_derived_from_the_two_status_figures(
    rules: DashboardRules,
) -> None:
    """The state defines change as current minus prior."""
    explicit = rules.judge("CHRO", curr_status=Decimal("12.0"), change=Decimal("-2.0"))
    derived = rules.judge(
        "CHRO", curr_status=Decimal("12.0"), prior_status=Decimal("14.0")
    )
    assert derived == explicit


def test_the_graduation_grid_marks_one_combination_unavailable(
    rules: DashboardRules,
) -> None:
    """A school cannot be at the top rate and have declined significantly."""
    assert rules.color("GRAD", "ALL", 5, 1) is None
    assert rules.color("GRAD", "ALL", 5, 2) == 5


def test_suspension_variants_have_their_own_cut_points(
    rules: DashboardRules,
) -> None:
    """The same rate is High for an elementary school, Medium for a high school.

    Elementary suspension bands run 1.1-3.0 Medium and 3.1-6.0 High; the high
    school table stretches Medium out to 6.0.
    """
    elementary = rules.status_band("SUSP", "ES", Decimal("4.0"))
    high = rules.status_band("SUSP", "HS", Decimal("4.0"))
    assert elementary is not None and high is not None
    assert elementary.level == 2
    assert high.level == 3


def test_the_academic_indicators_split_at_grade_eleven(
    rules: DashboardRules,
) -> None:
    grades_three_to_eight = rules.status_band("ELA", "ALL", Decimal("20.0"))
    grade_eleven = rules.status_band("ELA", "HS", Decimal("20.0"))
    assert grades_three_to_eight is not None and grade_eleven is not None
    assert grades_three_to_eight.level == 4
    assert grade_eleven.level == 3


def test_chronic_absenteeism_is_judged_in_reverse(rules: DashboardRules) -> None:
    """A low absenteeism rate is the good outcome."""
    low = rules.status_band("CHRO", "ALL", Decimal("2.0"))
    high = rules.status_band("CHRO", "ALL", Decimal("30.0"))
    assert low is not None and high is not None
    assert low.level == 5
    assert high.level == 1


def test_variant_selection_matches_the_files() -> None:
    assert variant_for("SUSP", school_type="es") == "ES"
    assert variant_for("SUSP", school_type=None) == "ALL"
    assert variant_for("ELA", high_school_cutpoints=True) == "HS"
    assert variant_for("ELA", high_school_cutpoints=False) == "ALL"
    assert variant_for("GRAD", high_school_cutpoints=True) == "ALL"


def test_only_the_indicators_that_publish_the_flag_use_the_reduced_grid() -> None:
    assert is_small_denominator("CHRO", 149) is True
    assert is_small_denominator("CHRO", 150) is False
    assert is_small_denominator("ELA", 10) is False
    assert is_small_denominator("CHRO", None) is False
