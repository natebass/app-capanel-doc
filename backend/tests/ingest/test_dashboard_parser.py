"""Reading rows of a Dashboard indicator file."""

from decimal import Decimal
from pathlib import Path

import pytest

from app.ingest.dashboard_parser import (
    DashboardLayoutError,
    DashboardRowParser,
    iter_rows,
)
from app.model.reference import EntityLevel

FIXTURES = Path(__file__).parent.parent / "fixtures" / "dashboard_files"


def read(name: str) -> tuple[list[str], list[list[str]]]:
    with (FIXTURES / name).open(encoding="utf-8", newline="") as handle:
        lines = list(handle)
    header = lines[0].rstrip("\r\n").split("\t")
    return header, list(iter_rows(iter(lines[1:])))


def parse_all(name: str):
    header, rows = read(name)
    parser = DashboardRowParser(header)
    return [parser.parse(row) for row in rows]


def test_a_file_that_is_not_a_dashboard_file_is_rejected() -> None:
    with pytest.raises(DashboardLayoutError, match="Not a Dashboard indicator file"):
        DashboardRowParser(["County Code", "District Code", "Test ID"])


def test_chronic_absenteeism_spells_change_level_with_a_capital_l() -> None:
    """The chronic file is the only one using ``changeLevel``."""
    header, _ = read("chronicdownload2099.txt")
    assert "changeLevel" in header
    assert "changelevel" not in header
    parsed = parse_all("chronicdownload2099.txt")
    assert any(row.result.change_level is not None for row in parsed)


def test_the_statewide_row_is_read_as_the_state_entity() -> None:
    parsed = parse_all("chronicdownload2099.txt")
    state = next(row for row in parsed if row.result.cds_code == "00000000000000")
    assert state.entity is not None
    assert state.entity.entity_level is EntityLevel.STATE
    assert state.entity.parent_cds_code is None
    assert state.result.indicator_code == "CHRO"
    assert state.result.reporting_year == 2099


def test_suspension_takes_its_variant_from_the_school_type() -> None:
    parsed = parse_all("suspdownload2099.txt")
    variants = {row.result.variant for row in parsed}
    assert variants <= {"ED", "HD", "UD", "ES", "MS", "HS"}
    assert {"ES", "HS", "UD"} <= variants


def test_academic_files_take_their_variant_from_the_high_school_flag() -> None:
    parsed = parse_all("eladownload2099.txt")
    assert {row.result.variant for row in parsed} == {"ALL", "HS"}


def test_indicators_without_a_variant_use_the_default() -> None:
    for name in ("graddownload2099.txt", "elpidownload2099.txt"):
        assert {row.result.variant for row in parse_all(name)} == {"ALL"}


def test_a_blank_figure_is_none_rather_than_zero() -> None:
    parsed = parse_all("chronicdownload2099.txt")
    blanks = [row for row in parsed if row.result.status_level is None]
    assert blanks, "expected at least one row the state does not rate"
    assert all(row.result.color is None for row in blanks)


def test_a_zero_level_is_read_as_no_level() -> None:
    """The files write 0 where a level does not apply, not where it is zero."""
    parsed = parse_all("suspdownload2099.txt")
    assert all(row.result.status_level != 0 and row.result.color != 0 for row in parsed)


def test_columns_outside_the_envelope_are_kept_as_extras() -> None:
    parsed = parse_all("ccidownload2099.txt")
    extras = [row.result.source_extras for row in parsed if row.result.source_extras]
    assert extras, "the college/career file has pathway columns to keep"
    assert any(key.startswith("curr_prep") for key in extras[0])


def test_the_envelope_itself_never_leaks_into_extras() -> None:
    for name in ("chronicdownload2099.txt", "suspdownload2099.txt"):
        for row in parse_all(name):
            assert not {"cds", "color", "statuslevel"} & row.result.source_extras.keys()


def test_an_entity_is_emitted_only_once_per_file() -> None:
    parsed = parse_all("chronicdownload2099.txt")
    emitted = [row.entity.cds_code for row in parsed if row.entity is not None]
    assert len(emitted) == len(set(emitted))


def test_a_school_row_derives_its_district_parent() -> None:
    parsed = parse_all("chronicdownload2099.txt")
    school = next(
        row
        for row in parsed
        if row.entity is not None and row.entity.entity_level is EntityLevel.SCHOOL
    )
    assert school.entity is not None
    assert school.entity.parent_cds_code == school.result.cds_code[:7] + "0000000"


def test_dashboard_entities_carry_no_test_years() -> None:
    """The Dashboard is not an administration of a test."""
    for row in parse_all("graddownload2099.txt"):
        if row.entity is not None:
            assert row.entity.first_test_year is None
            assert row.entity.last_test_year is None


def test_figures_are_read_as_decimals() -> None:
    parsed = parse_all("chronicdownload2099.txt")
    state = next(row for row in parsed if row.result.cds_code == "00000000000000")
    assert isinstance(state.result.curr_status, Decimal)
    assert state.result.curr_denominator is not None
