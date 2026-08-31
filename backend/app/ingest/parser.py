"""Turn research file rows into database records.

The state encodes two different kinds of "no value" and they mean different
things, so both survive the trip into the database:

An asterisk means the figure exists but is withheld, because the group is too
small to report without identifying students; the row is flagged
``suppressed``.  An empty field means the figure does not apply -- most often
the mean scale score on an "all grades" row, which the state deliberately
leaves blank because scale scores are not comparable between grades.

Both land as ``NULL``; only the first sets the flag.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from app.ingest.layouts import BandColumns, ResearchFileLayout
from app.ingest.reference_data import COUNTY_NAMES
from app.model.reference import CharterFunding, EntityLevel, MetOrAboveSource

SUPPRESSED = "*"
STATE_CDS = "00" + "0" * 12

# Type IDs that mark a charter school in both programs' entity conventions.
_CHARTER_TYPE_IDS = {9: CharterFunding.DIRECT, 10: CharterFunding.LOCAL}


class ParseError(ValueError):
    """Raised when a row cannot be interpreted with the resolved layout."""


@dataclass(slots=True)
class EntityRecord:
    """An entity discovered while reading a research file."""

    cds_code: str
    county_code: str
    district_code: str
    school_code: str
    entity_level: EntityLevel
    type_id: int
    is_charter: bool
    charter_funding: CharterFunding | None
    county_name: str | None
    district_name: str | None
    school_name: str | None
    zip_code: str | None
    display_name: str
    parent_cds_code: str | None
    # None when the entity was discovered somewhere other than a test
    # administration -- a Dashboard indicator file, for instance.
    first_test_year: int | None
    last_test_year: int | None


@dataclass(slots=True)
class ResultRecord:
    """One overall result cell, ready for :class:`AssessmentResult`."""

    cds_code: str
    test_year: int
    test_id: int
    student_group_id: int
    grade: str
    students_enrolled: int | None
    students_tested: int | None
    students_tested_with_scores: int | None
    mean_scale_score: Decimal | None
    level_counts: list[int | None]
    level_pcts: list[Decimal | None]
    met_or_above_count: int | None
    met_or_above_pct: Decimal | None
    met_or_above_source: MetOrAboveSource | None
    overall_total: int | None
    suppressed: bool


@dataclass(slots=True)
class SubscoreRecord:
    """One area, domain or composite breakdown."""

    cds_code: str
    test_year: int
    test_id: int
    student_group_id: int
    grade: str
    subscore_code: str
    mean_scale_score: Decimal | None
    band_counts: list[int | None]
    band_pcts: list[Decimal | None]
    subscore_total: int | None


@dataclass(slots=True)
class ParsedRows:
    """Everything one research file row contributes to the database."""

    result: ResultRecord
    subscores: list[SubscoreRecord] = field(default_factory=list)
    entity: EntityRecord | None = None


def _clean(raw: str) -> str:
    return raw.strip()


def _is_missing(raw: str) -> bool:
    return raw == "" or raw == SUPPRESSED


def parse_int(raw: str) -> int | None:
    """Read an integer, treating suppressed and empty values as missing."""
    value = _clean(raw)
    if _is_missing(value):
        return None
    try:
        return int(float(value)) if "." in value else int(value)
    except ValueError:
        return None


def parse_decimal(raw: str) -> Decimal | None:
    """Read a decimal, treating suppressed and empty values as missing."""
    value = _clean(raw)
    if _is_missing(value):
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def normalize_grade(raw: str) -> str:
    """Normalise a grade code to the two characters used in the layouts."""
    value = _clean(raw).upper()
    if not value:
        return "13"
    return value.zfill(2) if value.isdigit() else value[:2]


def build_cds_code(county: str, district: str, school: str) -> str:
    """Assemble the 14-character CDS code from its three parts."""
    return (
        f"{_clean(county).zfill(2)}{_clean(district).zfill(5)}{_clean(school).zfill(7)}"
    )


def entity_level_for(county: str, district: str, school: str) -> EntityLevel:
    """Derive the reporting level from the code parts.

    The programs number their ``Type ID`` values differently -- CAASPP uses
    07 for a school where ELPAC uses 01 -- so the codes, which agree, are the
    reliable signal.
    """
    if school.strip("0"):
        return EntityLevel.SCHOOL
    if district.strip("0"):
        return EntityLevel.DISTRICT
    if county.strip("0"):
        return EntityLevel.COUNTY
    return EntityLevel.STATE


def parent_cds_for(level: EntityLevel, county: str, district: str) -> str | None:
    """The CDS code of the entity one level up, or ``None`` for the state."""
    match level:
        case EntityLevel.SCHOOL:
            return build_cds_code(county, district, "0")
        case EntityLevel.DISTRICT:
            return build_cds_code(county, "0", "0")
        case EntityLevel.COUNTY:
            return STATE_CDS
        case _:
            return None


class RowParser:
    """Reads rows of one research file using a resolved layout."""

    def __init__(self, layout: ResearchFileLayout, header: Sequence[str]) -> None:
        self.layout = layout
        self.index = {name: position for position, name in enumerate(header)}
        missing = [name for name in layout.required_columns if name not in self.index]
        if missing:
            raise ParseError(
                f"Layout {layout.key!r} expects columns that the file does not "
                f"have: {', '.join(missing)}"
            )
        # An entity's names repeat on every one of its rows, so each CDS code
        # is turned into an entity record only the first time it is seen.
        self._seen_entities: set[str] = set()
        self._level_positions = self._band_positions(layout.levels)
        self._met_position = (
            self._band_positions((layout.met_or_above,))[0]
            if layout.met_or_above is not None
            else None
        )
        self._subscore_positions = [
            (
                subscore.code,
                self._band_positions(subscore.bands),
                self._optional(subscore.total),
                self._optional(subscore.mean_scale_score),
            )
            for subscore in layout.subscores
            # A layout may describe columns a particular year's file omits.
            if all(
                (band.pct is None or band.pct in self.index)
                and (band.count is None or band.count in self.index)
                for band in subscore.bands
            )
        ]

    def _optional(self, name: str | None) -> int | None:
        return self.index.get(name) if name else None

    def _band_positions(
        self, bands: Sequence[BandColumns]
    ) -> list[tuple[int | None, int | None]]:
        return [
            (self._optional(band.pct), self._optional(band.count)) for band in bands
        ]

    def _value(self, row: Sequence[str], position: int | None) -> str:
        if position is None or position >= len(row):
            return ""
        return row[position]

    def parse(
        self, row: Sequence[str], *, default_year: int | None = None
    ) -> ParsedRows:
        """Convert one row into its result, subscore and entity records."""
        layout = self.layout
        county = _clean(self._value(row, self.index[layout.county_code])).zfill(2)
        district = _clean(self._value(row, self.index[layout.district_code])).zfill(5)
        school = _clean(self._value(row, self.index[layout.school_code])).zfill(7)
        cds_code = f"{county}{district}{school}"

        test_year = parse_int(self._value(row, self.index[layout.test_year]))
        if test_year is None:
            test_year = default_year
        if test_year is None:
            raise ParseError("Row has no test year and none was supplied")

        test_id = parse_int(self._value(row, self.index[layout.test_id]))
        if test_id is None:
            raise ParseError("Row has no test id")

        student_group_id = parse_int(
            self._value(row, self.index[layout.student_group_id])
        )
        if student_group_id is None:
            raise ParseError("Row has no student group id")

        grade = normalize_grade(self._value(row, self.index[layout.grade]))
        type_id = parse_int(self._value(row, self.index[layout.type_id])) or 0

        suppressed = False
        level_counts: list[int | None] = []
        level_pcts: list[Decimal | None] = []
        for pct_position, count_position in self._level_positions:
            pct_raw = self._value(row, pct_position)
            count_raw = self._value(row, count_position)
            suppressed = suppressed or pct_raw.strip() == SUPPRESSED
            level_pcts.append(parse_decimal(pct_raw))
            level_counts.append(parse_int(count_raw))

        met_count: int | None = None
        met_pct: Decimal | None = None
        met_source: MetOrAboveSource | None = None
        if self._met_position is not None:
            pct_position, count_position = self._met_position
            met_pct = parse_decimal(self._value(row, pct_position))
            met_count = parse_int(self._value(row, count_position))
            if met_pct is not None or met_count is not None:
                met_source = MetOrAboveSource.PUBLISHED

        mean_raw = (
            self._value(row, self.index[layout.mean_scale_score])
            if layout.mean_scale_score and layout.mean_scale_score in self.index
            else ""
        )
        suppressed = suppressed or mean_raw.strip() == SUPPRESSED

        result = ResultRecord(
            cds_code=cds_code,
            test_year=test_year,
            test_id=test_id,
            student_group_id=student_group_id,
            grade=grade,
            students_enrolled=parse_int(
                self._value(row, self.index[layout.students_enrolled])
            ),
            students_tested=parse_int(
                self._value(row, self.index[layout.students_tested])
            ),
            students_tested_with_scores=parse_int(
                self._value(row, self._optional(layout.students_tested_with_scores))
            ),
            mean_scale_score=parse_decimal(mean_raw),
            level_counts=level_counts,
            level_pcts=level_pcts,
            met_or_above_count=met_count,
            met_or_above_pct=met_pct,
            met_or_above_source=met_source,
            overall_total=parse_int(
                self._value(row, self._optional(layout.overall_total))
            ),
            suppressed=suppressed,
        )

        subscores: list[SubscoreRecord] = []
        for (
            code,
            band_positions,
            total_position,
            mean_position,
        ) in self._subscore_positions:
            counts: list[int | None] = []
            pcts: list[Decimal | None] = []
            for pct_position, count_position in band_positions:
                pcts.append(parse_decimal(self._value(row, pct_position)))
                counts.append(parse_int(self._value(row, count_position)))
            total = parse_int(self._value(row, total_position))
            mean = parse_decimal(self._value(row, mean_position))
            # Mathematics carries an unused fourth area whose columns are all
            # zero; skipping empty breakdowns keeps those rows out entirely.
            if not total and mean is None and not any(c for c in counts):
                continue
            subscores.append(
                SubscoreRecord(
                    cds_code=cds_code,
                    test_year=test_year,
                    test_id=test_id,
                    student_group_id=student_group_id,
                    grade=grade,
                    subscore_code=code,
                    mean_scale_score=mean,
                    band_counts=counts,
                    band_pcts=pcts,
                    subscore_total=total,
                )
            )

        entity: EntityRecord | None = None
        if cds_code not in self._seen_entities:
            self._seen_entities.add(cds_code)
            entity = self._entity(
                row, county, district, school, cds_code, type_id, test_year
            )

        return ParsedRows(result=result, subscores=subscores, entity=entity)

    def _entity(
        self,
        row: Sequence[str],
        county: str,
        district: str,
        school: str,
        cds_code: str,
        type_id: int,
        test_year: int,
    ) -> EntityRecord:
        layout = self.layout
        level = entity_level_for(county, district, school)
        district_name = (
            _clean(self._value(row, self._optional(layout.district_name))) or None
        )
        school_name = (
            _clean(self._value(row, self._optional(layout.school_name))) or None
        )
        county_name = (
            _clean(self._value(row, self._optional(layout.county_name))) or None
        )
        county_name = county_name or COUNTY_NAMES.get(county)
        zip_code = _clean(self._value(row, self._optional(layout.zip_code))) or None

        match level:
            case EntityLevel.SCHOOL:
                display_name = school_name or district_name or cds_code
            case EntityLevel.DISTRICT:
                display_name = district_name or cds_code
            case EntityLevel.COUNTY:
                display_name = county_name or cds_code
            case _:
                display_name = COUNTY_NAMES["00"]

        return EntityRecord(
            cds_code=cds_code,
            county_code=county,
            district_code=district,
            school_code=school,
            entity_level=level,
            type_id=type_id,
            is_charter=type_id in _CHARTER_TYPE_IDS,
            charter_funding=_CHARTER_TYPE_IDS.get(type_id),
            county_name=county_name,
            district_name=district_name,
            school_name=school_name,
            zip_code=zip_code,
            display_name=display_name,
            parent_cds_code=parent_cds_for(level, county, district),
            first_test_year=test_year,
            last_test_year=test_year,
        )


def iter_rows(lines: Iterator[str], delimiter: str) -> Iterator[list[str]]:
    """Split already-decoded lines on the file's delimiter.

    Research files use a caret or, for administrations through 2018-19, a
    comma.  Neither is ever quoted, so a plain split is both correct and
    considerably faster than the ``csv`` module.
    """
    for line in lines:
        stripped = line.rstrip("\r\n")
        if stripped:
            yield stripped.split(delimiter)
