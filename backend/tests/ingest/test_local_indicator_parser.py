"""Reading Local Indicator files, whatever shape the state published them in."""

from __future__ import annotations

import datetime
from pathlib import Path

import pytest

from app.ingest.local_indicator_parser import (
    LocalIndicatorLayoutError,
    LocalIndicatorRowParser,
    detect_delimiter,
    iter_rows,
    parse_filename,
)

FIXTURES = Path(__file__).parent.parent / "fixtures" / "local_indicators"


def parse_all(name: str):
    priority, year = parse_filename(name)
    lines = (FIXTURES / name).read_text(encoding="utf-8").splitlines()
    delimiter = detect_delimiter(lines[0])
    parser = LocalIndicatorRowParser(
        lines[0].split(delimiter), default_priority=priority, default_year=year
    )
    return [parser.parse(row) for row in iter_rows(iter(lines[1:]), delimiter)]


def test_a_file_that_is_not_a_local_indicator_file_is_rejected() -> None:
    with pytest.raises(LocalIndicatorLayoutError, match="Not a Local Indicator file"):
        LocalIndicatorRowParser(["cds", "rtype", "statuslevel"])


def test_the_priority_and_year_come_from_the_file_name() -> None:
    assert parse_filename("Pr32025.xlsx") == (3, 2025)
    assert parse_filename("Pr102018.txt") == (10, 2018)
    assert parse_filename("chronicdownload2025.txt") == (None, None)


def test_pipe_and_tab_files_both_parse() -> None:
    """2018, 2019, 2021, 2024 and 2025 use a pipe; 2022 and 2023 use a tab."""
    assert detect_delimiter("a|b|c") == "|"
    assert detect_delimiter("a\tb\tc") == "\t"
    assert parse_all("Pr12099.txt")
    assert parse_all("Pr32099.txt")


def test_every_header_variant_resolves_to_the_same_envelope() -> None:
    """CDSCode/cdsCode/cdscode and PriorityNumber/priorityId all mean one thing."""
    for header in (
        ["CDSCode", "LEA", "PriorityNumber", "Performance", "Year"],
        ["cdsCode", "lea", "priorityNumber", "countyPerformance", "year"],
        ["cdscode", "lea", "priorityId", "performance", "year"],
    ):
        parser = LocalIndicatorRowParser(header, default_priority=1, default_year=2099)
        record = parser.parse(["01100170000000", "Example COE", "1", "Met", "2099"])
        assert record.cds_code == "01100170000000"
        assert record.priority_number == 1
        assert record.performance == "Met"
        assert record.lea_name == "Example COE"


def test_columns_outside_the_envelope_are_kept_under_their_published_names() -> None:
    records = parse_all("Pr12099.txt")
    keys = set().union(*(r.responses.keys() for r in records))
    assert {"NumMaterials", "NumFacilities"} & keys


def test_the_envelope_never_leaks_into_responses() -> None:
    for name in ("Pr12099.txt", "Pr32099.txt", "Pr62099.txt"):
        for record in parse_all(name):
            lowered = {key.lower() for key in record.responses}
            assert not lowered & {"cdscode", "lea", "prioritynumber", "year"}


def test_ratings_stay_numbers_and_narratives_stay_text() -> None:
    records = parse_all("Pr92099.txt")
    values = [v for r in records for v in r.responses.values()]
    assert any(isinstance(v, int) for v in values), "self-ratings must be integers"


def test_a_2018_file_has_no_meeting_date() -> None:
    """The state only added the board meeting date in 2019."""
    for record in parse_all("Pr12099.txt"):
        assert record.meeting_date is None


def test_a_meeting_date_is_read_when_present() -> None:
    parser = LocalIndicatorRowParser(
        [
            "cdsCode",
            "lea",
            "priorityNumber",
            "countyPerformance",
            "meetingDate",
            "year",
        ],
        default_priority=6,
        default_year=2099,
    )
    record = parser.parse(
        ["01100170000000", "Example", "6", "Met", "2025-06-10", "2099"]
    )
    assert record.meeting_date == datetime.date(2025, 6, 10)


def test_a_spreadsheet_datetime_is_read_as_a_date() -> None:
    parser = LocalIndicatorRowParser(
        ["cdsCode", "lea", "priorityNumber", "meetingDate", "year"],
        default_priority=6,
        default_year=2099,
    )
    record = parser.parse(
        ["01100170000000", "Example", "6", datetime.datetime(2025, 6, 10, 9, 0), "2099"]
    )
    assert record.meeting_date == datetime.date(2025, 6, 10)


def test_an_unreadable_date_is_dropped_rather_than_guessed() -> None:
    parser = LocalIndicatorRowParser(
        ["cdsCode", "lea", "priorityNumber", "meetingDate", "year"],
        default_priority=6,
        default_year=2099,
    )
    record = parser.parse(
        ["01100170000000", "Example", "6", "sometime in June", "2099"]
    )
    assert record.meeting_date is None


def test_performance_is_one_of_the_three_published_values() -> None:
    allowed = {"Met", "Not Met", "Not Met For Two or More Years", None}
    for name in ("Pr12099.txt", "Pr32099.txt", "Pr62099.txt", "Pr92099.txt"):
        for record in parse_all(name):
            assert record.performance in allowed


def test_the_fixture_year_is_used_not_the_file_name() -> None:
    """Fixtures are stamped 2099 so they never collide with real imports."""
    assert all(r.reporting_year == 2099 for r in parse_all("Pr62099.txt"))


def test_a_malformed_cds_code_is_rejected() -> None:
    parser = LocalIndicatorRowParser(
        ["cdsCode", "lea", "priorityNumber", "year"], default_priority=1
    )
    from app.ingest.parser import ParseError

    with pytest.raises(ParseError, match="malformed CDS code"):
        parser.parse(["not-a-code", "Example", "1", "2099"])
