"""Row parsing: suppression, band direction, codes and entity derivation."""

from decimal import Decimal
from pathlib import Path

from app.ingest.layouts import resolve_layout
from app.ingest.parser import (
    RowParser,
    build_cds_code,
    entity_level_for,
    iter_rows,
    normalize_grade,
    parent_cds_for,
    parse_decimal,
    parse_int,
)
from app.ingest.sources import FILE_ENCODING
from app.model.reference import CharterFunding, EntityLevel

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "research_files"
SB_FIXTURE = FIXTURES / "sb_ca2016_all_csv_ela_v1.txt"


def parsed_rows() -> list:
    lines = SB_FIXTURE.read_text(encoding=FILE_ENCODING).splitlines()
    header = [column.strip() for column in lines[0].split("^")]
    layout = resolve_layout(SB_FIXTURE.name, header)
    parser = RowParser(layout, header)
    return [parser.parse(row) for row in iter_rows(iter(lines[1:]), "^")]


def test_missing_values_are_read_as_nothing() -> None:
    assert parse_int("") is None
    assert parse_int("*") is None
    assert parse_int("1234") == 1234
    assert parse_decimal("") is None
    assert parse_decimal("*") is None
    assert parse_decimal("22.29") == Decimal("22.29")


def test_grades_are_padded_to_the_two_characters_the_layouts_use() -> None:
    assert normalize_grade("3") == "03"
    assert normalize_grade("11") == "11"
    assert normalize_grade("13") == "13"
    assert normalize_grade("kn") == "KN"
    assert normalize_grade("") == "13"


def test_cds_codes_and_levels_come_from_the_code_parts() -> None:
    assert build_cds_code("58", "99999", "9900001") == "58999999900001"
    assert entity_level_for("00", "00000", "0000000") is EntityLevel.STATE
    assert entity_level_for("58", "00000", "0000000") is EntityLevel.COUNTY
    assert entity_level_for("58", "99999", "0000000") is EntityLevel.DISTRICT
    assert entity_level_for("58", "99999", "9900001") is EntityLevel.SCHOOL
    assert parent_cds_for(EntityLevel.SCHOOL, "58", "99999") == "58999990000000"
    assert parent_cds_for(EntityLevel.DISTRICT, "58", "99999") == "58000000000000"
    assert parent_cds_for(EntityLevel.STATE, "00", "00000") is None


def test_levels_are_stored_lowest_first() -> None:
    """The file prints exceeded first; level 1 must be "standard not met"."""
    statewide = parsed_rows()[0].result
    assert statewide.level_pcts == [
        Decimal("30.00"),  # Standard Not Met
        Decimal("25.00"),  # Standard Nearly Met
        Decimal("25.00"),  # Standard Met
        Decimal("20.00"),  # Standard Exceeded
    ]
    assert statewide.met_or_above_pct == Decimal("45.00")


def test_area_bands_are_stored_lowest_first() -> None:
    """Areas print above/near/below standard; below must land in band 1."""
    subscore = parsed_rows()[0].subscores[0]
    assert subscore.subscore_code == "AREA_1"
    assert subscore.band_pcts == [
        Decimal("30.00"),  # Below Standard
        Decimal("50.00"),  # Near Standard
        Decimal("20.00"),  # Above Standard
    ]


def test_a_cross_grade_aggregate_has_no_mean_scale_score() -> None:
    rows = parsed_rows()
    assert rows[0].result.grade == "13"
    assert rows[0].result.mean_scale_score is None
    assert rows[0].result.suppressed is False
    assert rows[1].result.grade == "03"
    assert rows[1].result.mean_scale_score == Decimal("2432.5")


def test_a_withheld_row_is_flagged_and_left_empty() -> None:
    suppressed = parsed_rows()[-1].result
    assert suppressed.student_group_id == 160
    assert suppressed.suppressed is True
    assert suppressed.students_tested is None
    assert all(value is None for value in suppressed.level_pcts)


def test_charter_schools_are_identified_by_their_type_id() -> None:
    entities = {
        parsed.entity.cds_code: parsed.entity
        for parsed in parsed_rows()
        if parsed.entity is not None
    }
    charter = entities["58999999900002"]
    assert charter.is_charter is True
    assert charter.charter_funding is CharterFunding.DIRECT
    assert charter.school_name == "Fixture Charter"
    assert entities["58999999900001"].is_charter is False
    assert entities["58000000000000"].display_name == "Yuba"


def test_an_entity_is_emitted_once_per_file() -> None:
    """Names repeat on every row; only the first occurrence carries an entity."""
    rows = parsed_rows()
    seen = [parsed.entity.cds_code for parsed in rows if parsed.entity is not None]
    assert len(seen) == len(set(seen))
    assert rows[1].entity is None  # second statewide row
