"""Read rows of a California School Dashboard indicator file.

Unlike the research files, which need a layout per test because the column
names and the band vocabulary differ, every Dashboard indicator file shares
one envelope.  So there is one parser, matching columns by name -- case
insensitively, because the chronic absenteeism file spells ``changeLevel``
with a capital L while every other file uses ``changelevel``.

Columns outside the envelope are kept verbatim in ``source_extras`` rather
than dropped: the College/Career file carries two dozen ``curr_prep_*``
pathway columns and the English Learner Progress file a dozen
``currprogressed*`` ones, all of them meaningful but none of them shared.

Blank is preserved as ``None``.  The Dashboard files have no suppression
marker -- the state simply omits a figure it will not report -- so unlike
:mod:`app.ingest.parser` there is no ``*`` to distinguish, and a blank is
never a zero.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

from app.ingest.parser import EntityRecord, ParseError, entity_level_for, parent_cds_for
from app.model.dashboard import DEFAULT_VARIANT
from app.model.reference import EntityLevel

# Canonical field -> the header spellings that mean it, lower-cased.
_COLUMNS: dict[str, tuple[str, ...]] = {
    "cds_code": ("cds",),
    "rtype": ("rtype",),
    "school_name": ("schoolname",),
    "district_name": ("districtname",),
    "county_name": ("countyname",),
    "charter_flag": ("charter_flag",),
    "coe_flag": ("coe_flag",),
    "dass_flag": ("dass_flag",),
    "school_type": ("type",),
    "student_group_code": ("studentgroup",),
    "curr_numerator": ("currnumer",),
    "curr_denominator": ("currdenom",),
    "prior_numerator": ("priornumer",),
    "prior_denominator": ("priordenom",),
    "curr_status": ("currstatus",),
    "prior_status": ("priorstatus",),
    "change": ("change",),
    "status_level": ("statuslevel",),
    "change_level": ("changelevel",),
    "color": ("color",),
    "box": ("box",),
    "small_denominator": ("smalldenom",),
    "curr_nsize_met": ("currnsizemet",),
    "prior_nsize_met": ("priornsizemet",),
    "accountability_met": ("accountabilitymet",),
    "hs_cutpoints": ("hscutpoints",),
    "indicator_code": ("indicator",),
    "reporting_year": ("reportingyear",),
}

# Without these a file is not a Dashboard indicator file.  The indicator and
# the student group are not among them: the state only added an ``indicator``
# column in 2023, and the English Learner Progress files carried no
# ``studentgroup`` column before 2024 because every row is English learners.
# Both are supplied by the caller from the file name when absent.
REQUIRED_COLUMNS = ("cds", "rtype", "reportingyear")

# File name stem -> the indicator its rows belong to.  Order matters: the
# longest distinctive prefixes are tried first so ``dass1year...`` is not
# mistaken for something else.
INDICATOR_BY_STEM = {
    "dass1yeargraduationrate": "GRAD",
    "elpacpart": "ELPACPART",
    "ela": "ELA",
    "math": "MATH",
    "chronic": "CHRO",
    "susp": "SUSP",
    "grad": "GRAD",
    "elpi": "ELPI",
    "cci": "CCI",
    "science": "SCIENCE",
}

# Indicators that report a single student group without naming it.  The
# English learner files are only ever about English learners, and the 2023
# participation file has no student group column at all.
IMPLIED_STUDENT_GROUP = {"ELPI": "EL", "ELPACPART": "EL"}

# Files whose rows describe a narrower population than the indicator's usual
# one, and so are stored under their own variant.
VARIANT_BY_STEM = {"dass1yeargraduationrate": "DASS1YR"}

# Participation files name their columns after the year: ``enrolled25`` and
# ``prate25`` for the current year, ``enrolled24`` for the prior one.  The
# names therefore change annually, so they are resolved from the reporting
# year rather than listed.
_YEAR_SUFFIXED = {
    "curr_denominator": "enrolled",
    "curr_numerator": "tested",
    "curr_status": "prate",
    "prior_denominator": "enrolled",
    "prior_numerator": "tested",
    "prior_status": "prate",
}


def variant_from_filename(name: str) -> str | None:
    """The variant a file's rows belong to, if it is a narrower population."""
    stem = name.rsplit("/", 1)[-1].lower()
    for prefix, variant in VARIANT_BY_STEM.items():
        if stem.startswith(prefix):
            return variant
    return None


def indicator_from_filename(name: str) -> str | None:
    """Read the indicator out of ``chronicdownload2019.txt``."""
    stem = name.rsplit("/", 1)[-1].lower()
    for prefix, indicator in INDICATOR_BY_STEM.items():
        if stem.startswith(prefix):
            return indicator
    return None


# Type IDs matching the convention the research files use, so an entity that
# arrives from either side is described the same way.
_TYPE_IDS = {
    EntityLevel.STATE: 4,
    EntityLevel.COUNTY: 5,
    EntityLevel.DISTRICT: 6,
    EntityLevel.SCHOOL: 7,
}

STATE_CDS = "00000000000000"


class DashboardLayoutError(RuntimeError):
    """Raised when a file is not a Dashboard indicator file."""


@dataclass(slots=True)
class DashboardResultRecord:
    """One indicator result row, ready to load."""

    cds_code: str
    reporting_year: int
    indicator_code: str
    student_group_code: str
    variant: str = DEFAULT_VARIANT

    curr_numerator: int | None = None
    curr_denominator: int | None = None
    prior_numerator: int | None = None
    prior_denominator: int | None = None
    curr_status: Decimal | None = None
    prior_status: Decimal | None = None
    change: Decimal | None = None

    status_level: int | None = None
    change_level: int | None = None
    color: int | None = None
    box: int | None = None

    curr_nsize_met: bool = False
    prior_nsize_met: bool = False
    accountability_met: bool = False
    small_denominator: bool = False
    charter_flag: bool = False
    coe_flag: bool = False
    dass_flag: bool = False

    is_projected: bool = False
    projection_basis: str | None = None
    source_extras: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DashboardParsedRow:
    """A result and, the first time its entity is seen, that entity."""

    result: DashboardResultRecord
    entity: EntityRecord | None = None


def _flag(raw: str | None) -> bool:
    return (raw or "").strip().upper() == "Y"


def _int(raw: str | None) -> int | None:
    value = (raw or "").strip()
    if not value:
        return None
    try:
        return int(float(value)) if "." in value else int(value)
    except ValueError:
        return None


def _decimal(raw: str | None) -> Decimal | None:
    value = (raw or "").strip()
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _level(raw: str | None) -> int | None:
    """Read a status, change or colour level, where 0 means "none"."""
    value = _int(raw)
    return None if value in (None, 0) else value


class DashboardRowParser:
    """Reads rows of one Dashboard indicator file."""

    def __init__(
        self,
        header: Sequence[str],
        *,
        default_indicator: str | None = None,
        default_student_group: str | None = None,
        default_variant: str | None = None,
        year_suffixed: bool = False,
        reporting_year: int | None = None,
    ) -> None:
        self.default_indicator = default_indicator
        self.default_variant = default_variant
        self.default_student_group = default_student_group or IMPLIED_STUDENT_GROUP.get(
            default_indicator or ""
        )
        # The DASS graduation file is published with a byte order mark, which
        # would otherwise make its first column unmatchable.
        self.header = [column.strip().lstrip("\ufeff") for column in header]
        lowered = [column.lower() for column in self.header]
        missing = [name for name in REQUIRED_COLUMNS if name not in lowered]
        if missing:
            raise DashboardLayoutError(
                "Not a Dashboard indicator file; missing "
                f"{', '.join(missing)}. First columns seen: {self.header[:10]}"
            )

        self._position: dict[str, int] = {}
        claimed: set[int] = set()
        for canonical, spellings in _COLUMNS.items():
            for spelling in spellings:
                if spelling in lowered:
                    index = lowered.index(spelling)
                    self._position[canonical] = index
                    claimed.add(index)
                    break
        # Anything the envelope does not claim travels as an extra.
        self._extras = [
            (index, self.header[index])
            for index in range(len(self.header))
            if index not in claimed
        ]
        if year_suffixed and reporting_year is not None:
            self._claim_year_suffixed(lowered, reporting_year, claimed)

        # Recompute the extras once the year-suffixed columns have been taken.
        self._extras = [
            (index, self.header[index])
            for index in range(len(self.header))
            if index not in claimed
        ]
        self._seen_entities: set[str] = set()

    def _claim_year_suffixed(
        self, lowered: list[str], reporting_year: int, claimed: set[int]
    ) -> None:
        """Map ``enrolled25`` / ``enrolled24`` onto current and prior."""
        current = f"{reporting_year % 100:02d}"
        prior = f"{(reporting_year - 1) % 100:02d}"
        for canonical, stem in _YEAR_SUFFIXED.items():
            is_prior = canonical.startswith("prior")
            candidates = [f"{stem}{prior if is_prior else current}"]
            # The first participation file, for 2019, named its columns
            # ``enrolled`` and ``prate`` outright and carried no prior year.
            if not is_prior:
                candidates.append(stem)
            for column in candidates:
                if column in lowered:
                    index = lowered.index(column)
                    self._position[canonical] = index
                    claimed.add(index)
                    break

    def _cell(self, row: Sequence[str], canonical: str) -> str | None:
        index = self._position.get(canonical)
        if index is None or index >= len(row):
            return None
        return row[index]

    def parse(
        self, row: Sequence[str], *, default_year: int | None = None
    ) -> DashboardParsedRow:
        cds_code = (self._cell(row, "cds_code") or "").strip()
        if len(cds_code) != 14 or not cds_code.isdigit():
            raise ParseError(f"malformed CDS code {cds_code!r}")

        year = _int(self._cell(row, "reporting_year")) or default_year
        if year is None:
            raise ParseError("no reporting year on the row or in the file name")

        indicator = (
            self._cell(row, "indicator_code") or ""
        ).strip().upper() or self.default_indicator
        if not indicator:
            raise ParseError("no indicator column and none derived from the file name")

        group = (
            self._cell(row, "student_group_code") or ""
        ).strip().upper() or self.default_student_group
        if not group:
            raise ParseError(
                "no student group column and none implied by the indicator"
            )

        # The variant selects which published five-by-five table applies.
        school_type = (self._cell(row, "school_type") or "").strip().upper()
        if indicator == "SUSP" and school_type:
            variant = school_type
        elif indicator in {"ELA", "MATH"} and _flag(self._cell(row, "hs_cutpoints")):
            variant = "HS"
        else:
            variant = self.default_variant or DEFAULT_VARIANT

        extras = {}
        for index, name in self._extras:
            if index < len(row):
                value = row[index].strip()
                if value:
                    extras[name] = value

        result = DashboardResultRecord(
            cds_code=cds_code,
            reporting_year=year,
            indicator_code=indicator,
            student_group_code=group,
            variant=variant,
            curr_numerator=_int(self._cell(row, "curr_numerator")),
            curr_denominator=_int(self._cell(row, "curr_denominator")),
            prior_numerator=_int(self._cell(row, "prior_numerator")),
            prior_denominator=_int(self._cell(row, "prior_denominator")),
            curr_status=_decimal(self._cell(row, "curr_status")),
            prior_status=_decimal(self._cell(row, "prior_status")),
            change=_decimal(self._cell(row, "change")),
            status_level=_level(self._cell(row, "status_level")),
            change_level=_level(self._cell(row, "change_level")),
            color=_level(self._cell(row, "color")),
            box=_level(self._cell(row, "box")),
            curr_nsize_met=_flag(self._cell(row, "curr_nsize_met")),
            prior_nsize_met=_flag(self._cell(row, "prior_nsize_met")),
            accountability_met=_flag(self._cell(row, "accountability_met")),
            small_denominator=_flag(self._cell(row, "small_denominator")),
            charter_flag=_flag(self._cell(row, "charter_flag")),
            coe_flag=_flag(self._cell(row, "coe_flag")),
            dass_flag=_flag(self._cell(row, "dass_flag")),
            source_extras=extras,
        )

        entity = None
        if cds_code not in self._seen_entities:
            self._seen_entities.add(cds_code)
            entity = self._entity(cds_code, row)
        return DashboardParsedRow(result=result, entity=entity)

    def _entity(self, cds_code: str, row: Sequence[str]) -> EntityRecord:
        county, district, school = cds_code[:2], cds_code[2:7], cds_code[7:]
        level = entity_level_for(county, district, school)
        school_name = (self._cell(row, "school_name") or "").strip() or None
        district_name = (self._cell(row, "district_name") or "").strip() or None
        county_name = (self._cell(row, "county_name") or "").strip() or None
        display = (
            school_name
            if level is EntityLevel.SCHOOL
            else district_name
            if level is EntityLevel.DISTRICT
            else county_name
        ) or cds_code
        return EntityRecord(
            cds_code=cds_code,
            county_code=county,
            district_code=district,
            school_code=school,
            entity_level=level,
            type_id=_TYPE_IDS[level],
            is_charter=_flag(self._cell(row, "charter_flag")),
            charter_funding=None,
            county_name=county_name,
            district_name=district_name,
            school_name=school_name,
            zip_code=None,
            display_name=display,
            parent_cds_code=parent_cds_for(level, county, district),
            # The Dashboard is not an administration of a test, so it must not
            # widen the years an entity is recorded as having tested in.
            first_test_year=None,
            last_test_year=None,
        )


def iter_rows(lines: Iterator[str], delimiter: str = "\t") -> Iterator[list[str]]:
    """Split a Dashboard file's lines.  The files are never quoted."""
    for line in lines:
        stripped = line.rstrip("\r\n")
        if stripped:
            yield stripped.split(delimiter)
