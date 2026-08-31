"""Reading the Census Day enrolment files."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.ingest.enrollment_loader import (
    EnrollmentRowParser,
    enrollment_file_names,
    year_from_filename,
)
from app.ingest.parser import ParseError

# The 2018-20 and 2022-25 shape.
HEADER = [
    "cds",
    "rtype",
    "schoolname",
    "districtname",
    "countyname",
    "studentgroup",
    "totalenrollment",
    "subgrouptotal",
    "rate",
    "reportingyear",
]
# 2021 reordered the columns and capitalised every heading.
HEADER_2021 = [
    "CDS",
    "RType",
    "Studentgroup",
    "SchoolName",
    "DistrictName",
    "CountyName",
    "TotalEnrollment",
    "SubGroupTotal",
    "rate",
    "ReportingYear",
]


def test_a_file_that_is_not_an_enrolment_file_is_rejected() -> None:
    with pytest.raises(ParseError, match="Not a Census Day enrolment file"):
        EnrollmentRowParser(["cds", "rtype", "color"])


def test_a_row_reads_every_field() -> None:
    parser = EnrollmentRowParser(HEADER)
    record = parser.parse(
        [
            "00000000000000",
            "X",
            "State",
            "State",
            "",
            "AA",
            "5806221",
            "281645",
            "4.9",
            "2025",
        ]
    )
    assert record.cds_code == "00000000000000"
    assert record.student_group_code == "AA"
    assert record.total_enrollment == 5806221
    assert record.subgroup_total == 281645
    assert record.rate == Decimal("4.9")


def test_the_2021_reordering_and_capitalisation_still_parse() -> None:
    """Columns are matched by name, so order and case do not matter."""
    parser = EnrollmentRowParser(HEADER_2021)
    record = parser.parse(
        [
            "00000000000000",
            "X",
            "AA",
            "State",
            "State",
            "",
            "6002523",
            "290000",
            "4.8",
            "2021",
        ]
    )
    assert record.student_group_code == "AA"
    assert record.total_enrollment == 6002523
    assert record.reporting_year == 2021


def test_a_blank_figure_is_none_rather_than_zero() -> None:
    parser = EnrollmentRowParser(HEADER)
    record = parser.parse(
        ["00000000000000", "X", "State", "State", "", "AA", "", "", "", "2025"]
    )
    assert record.total_enrollment is None
    assert record.subgroup_total is None
    assert record.rate is None


def test_a_malformed_cds_code_is_rejected() -> None:
    parser = EnrollmentRowParser(HEADER)
    with pytest.raises(ParseError, match="malformed CDS code"):
        parser.parse(["nope", "X", "S", "D", "", "AA", "1", "1", "1", "2025"])


def test_file_names_follow_the_published_convention() -> None:
    assert enrollment_file_names([2025]) == ["censusenrollratesdownload2025.txt"]
    assert year_from_filename("censusenrollratesdownload2021.txt") == 2021
