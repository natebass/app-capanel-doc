"""Layout resolution against real and renamed research file names."""

from pathlib import Path

import pytest

from app.ingest.layouts import (
    LayoutError,
    resolve_layout,
    year_from_filename,
)
from app.ingest.sources import FILE_ENCODING

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "research_files"


def header_of(name: str) -> list[str]:
    line = (FIXTURES / name).read_text(encoding=FILE_ENCODING).splitlines()[0]
    return [column.strip() for column in line.split("^")]


def test_year_is_read_from_the_published_file_name() -> None:
    assert year_from_filename("sb_ca2025_all_csv_ela_v1.txt") == 2025
    assert year_from_filename("caa_ca2017_all_csv_v1.txt") == 2017
    assert year_from_filename("something_else.txt") is None


def test_smarter_balanced_file_resolves_to_the_smarter_balanced_layout() -> None:
    layout = resolve_layout(
        "sb_ca2016_all_csv_ela_v1.txt", header_of("sb_ca2016_all_csv_ela_v1.txt")
    )
    assert layout.key == "sb"
    assert layout.test_ids == (1, 2)


def test_a_renamed_file_still_resolves_from_its_columns() -> None:
    layout = resolve_layout(
        "exported-data.txt", header_of("caa_ca2017_all_csv_v1.txt"), test_year=2017
    )
    assert layout.key == "caa"


def test_the_spanish_assessment_layout_depends_on_the_year() -> None:
    """The CSA reported score ranges until 2023-24 and levels afterwards."""
    ranges_header = [
        "County Code",
        "District Code",
        "District Name",
        "School Code",
        "School Name",
        "Type ID",
        "Filler",
        "Test Year",
        "Test Type",
        "Test ID",
        "Student Group ID",
        "Grade",
        "Total Students Enrolled",
        "Total Students Tested",
        "Total Students Tested with Scores",
        "Mean Scale Score",
        "Percent Range 3",
        "Count Range 3",
        "Percent Range 2",
        "Count Range 2",
        "Percent Range 1",
        "Count Range 1",
        "Overall Total",
    ]
    assert (
        resolve_layout("csa_ca2024_all_csv_v1.txt", ranges_header).key == "csa_ranges"
    )


def test_an_unrecognisable_header_is_rejected() -> None:
    with pytest.raises(LayoutError):
        resolve_layout("mystery.txt", ["a", "b", "c"])
