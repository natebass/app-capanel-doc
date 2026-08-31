"""Reading and loading the Growth Model files."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.ingest.growth_loader import (
    GrowthRowParser,
    growth_file_names,
    year_from_filename,
)
from app.ingest.parser import ParseError

HEADER = [
    "cds",
    "subject",
    "rtype",
    "schoolname",
    "districtname",
    "countyname",
    "charter_flag",
    "coe_flag",
    "dass_flag",
    "studentgroup",
    "denom",
    "status",
    "estimate",
    "performancecategory",
    "numberimprove",
    "percentimprove",
    "reportingyear",
]


def row(**overrides) -> list[str]:
    values = {
        "cds": "01100170112607",
        "subject": "ELA",
        "rtype": "S",
        "schoolname": "Example",
        "districtname": "Example District",
        "countyname": "Alameda",
        "charter_flag": "Y",
        "coe_flag": "",
        "dass_flag": "",
        "studentgroup": "AA",
        "denom": "22",
        "status": "-12",
        "estimate": "WEIGHTED",
        "performancecategory": "2",
        "numberimprove": "17",
        "percentimprove": "77.3",
        "reportingyear": "2025",
    }
    values.update(overrides)
    return [values[name] for name in HEADER]


def parse(**overrides):
    return GrowthRowParser(HEADER).parse(row(**overrides))


def test_a_file_that_is_not_a_growth_file_is_rejected() -> None:
    with pytest.raises(ParseError, match="Not a Growth Model file"):
        GrowthRowParser(["cds", "rtype", "statuslevel"])


def test_a_row_reads_every_field() -> None:
    record = parse()
    assert record.cds_code == "01100170112607"
    assert record.subject == "ELA"
    assert record.student_group_code == "AA"
    assert record.denominator == 22
    assert record.growth == Decimal("-12")
    assert record.estimate_method == "WEIGHTED"
    assert record.performance_category == 2
    assert record.number_improved == 17
    assert record.percent_improved == Decimal("77.3")
    assert record.charter_flag is True


def test_category_zero_means_no_category_not_a_category() -> None:
    """The state writes 0 where it assigned none."""
    assert parse(performancecategory="0").performance_category is None
    assert parse(performancecategory="").performance_category is None
    assert parse(performancecategory="1").performance_category == 1


def test_both_subjects_are_accepted_and_nothing_else() -> None:
    assert parse(subject="MATH").subject == "MATH"
    assert parse(subject="ela").subject == "ELA"
    # Science has no growth: the science test is not taken in consecutive grades.
    with pytest.raises(ParseError, match="unexpected subject"):
        parse(subject="SCIENCE")


def test_a_missing_growth_figure_is_none_rather_than_zero() -> None:
    record = parse(status="", denom="", percentimprove="")
    assert record.growth is None
    assert record.denominator is None
    assert record.percent_improved is None


def test_the_estimate_method_is_normalised() -> None:
    assert parse(estimate="none").estimate_method == "NONE"
    assert parse(estimate="").estimate_method is None


def test_a_malformed_cds_code_is_rejected() -> None:
    with pytest.raises(ParseError, match="malformed CDS code"):
        parse(cds="123")


def test_the_year_falls_back_to_the_file_name() -> None:
    parser = GrowthRowParser(HEADER)
    record = parser.parse(row(reportingyear=""), default_year=2025)
    assert record.reporting_year == 2025


def test_file_names_follow_the_published_convention() -> None:
    assert growth_file_names([2025]) == ["growthmodeldownload2025.txt"]
    assert year_from_filename("growthmodeldownload2025.txt") == 2025
