"""Declarative descriptions of the state's research file layouts.

Every research file is a delimited table with a header row, so a layout is
expressed as the *names* of the columns to read rather than their positions.
That keeps the importer working when the state adds a column mid-file -- which
it does -- and makes a mismatch fail loudly at load time instead of silently
shifting every value by one.

Two conventions have to be reconciled here:

* CAASPP files use spaced title case (``Student Group ID``) and carry a
  ``Test Type`` column; ELPAC files use compact camel case (``StudentGroupID``)
  and identify the test through ``TestID`` alone.
* Performance bands are printed in different directions.  Smarter Balanced
  areas run above/near/below standard while CAST domains run below/near/above.
  Each layout lists its bands lowest-first, and the importer stores them in
  that order, so downstream queries never have to know which file a row came
  from.

Sources: the fixed-length record definition pages at
``https://caaspp-elpac.ets.org/caaspp/ResearchFileFormat{SB,CAA,CAST,CAAS,CSA}``
and ``https://caaspp-elpac.ets.org/elpac/ResearchFileFormat{SA,IA,ALTSA,ALTIA}``,
each of which also publishes the caret-delimited column header for every field.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TypedDict

from app.model.reference import Program

# Spring year of the administration, parsed out of a research file name such as
# ``sb_ca2025_all_csv_ela_v1.txt``.
_YEAR_IN_NAME = re.compile(r"ca(\d{4})", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class BandColumns:
    """The percentage and count columns for one performance band."""

    pct: str | None
    count: str | None


@dataclass(frozen=True, slots=True)
class SubscoreColumns:
    """Where one area, domain or composite lives in a research file."""

    code: str
    bands: tuple[BandColumns, ...]
    total: str | None = None
    mean_scale_score: str | None = None


@dataclass(frozen=True, slots=True)
class ResearchFileLayout:
    """How to read one family of research files."""

    key: str
    program: Program
    test_type: str
    test_ids: tuple[int, ...]
    min_year: int = 2015
    max_year: int = 9999

    county_code: str = "County Code"
    district_code: str = "District Code"
    school_code: str = "School Code"
    type_id: str = "Type ID"
    test_year: str = "Test Year"
    test_id: str = "Test ID"
    student_group_id: str = "Student Group ID"
    grade: str = "Grade"

    county_name: str | None = None
    district_name: str | None = "District Name"
    school_name: str | None = "School Name"
    zip_code: str | None = None

    students_enrolled: str = "Total Students Enrolled"
    students_tested: str = "Total Students Tested"
    students_tested_with_scores: str = "Total Students Tested with Scores"
    mean_scale_score: str | None = "Mean Scale Score"

    levels: tuple[BandColumns, ...] = ()
    met_or_above: BandColumns | None = None
    overall_total: str | None = "Overall Total"
    subscores: tuple[SubscoreColumns, ...] = field(default_factory=tuple)

    @property
    def required_columns(self) -> tuple[str, ...]:
        """Columns that must be present for the layout to match a header."""
        return (
            self.county_code,
            self.district_code,
            self.school_code,
            self.type_id,
            self.test_year,
            self.test_id,
            self.student_group_id,
            self.grade,
            self.students_enrolled,
            self.students_tested,
        )

    def covers_year(self, year: int) -> bool:
        return self.min_year <= year <= self.max_year


def _bands(*pairs: tuple[str, str]) -> tuple[BandColumns, ...]:
    return tuple(BandColumns(pct=pct, count=count) for pct, count in pairs)


def _sb_area(index: int, code: str) -> SubscoreColumns:
    """Smarter Balanced areas print above/near/below; store lowest first."""
    return SubscoreColumns(
        code=code,
        bands=_bands(
            (
                f"Area {index} Percentage Below Standard",
                f"Area {index} Count Below Standard",
            ),
            (
                f"Area {index} Percentage Near Standard",
                f"Area {index} Count Near Standard",
            ),
            (
                f"Area {index} Percentage Above Standard",
                f"Area {index} Count Above Standard",
            ),
        ),
        total=f"Area {index} Total",
    )


def _sb_composite_area(index: int, code: str) -> SubscoreColumns:
    return SubscoreColumns(
        code=code,
        bands=_bands(
            (
                f"Composite Area {index} Percentage Below Standard",
                f"Composite Area {index} Count Below Standard",
            ),
            (
                f"Composite Area {index} Percentage Near Standard",
                f"Composite Area {index} Count Near Standard",
            ),
            (
                f"Composite Area {index} Percentage Above Standard",
                f"Composite Area {index} Count Above Standard",
            ),
        ),
        total=f"Composite Area {index} Total",
    )


def _cast_domain(prefix: str, code: str) -> SubscoreColumns:
    return SubscoreColumns(
        code=code,
        bands=_bands(
            (
                f"{prefix} Domain Percent Below Standard",
                f"{prefix} Domain Count Below Standard",
            ),
            (
                f"{prefix} Domain Percent Near Standard",
                f"{prefix} Domain Count Near Standard",
            ),
            (
                f"{prefix} Domain Percent Above Standard",
                f"{prefix} Domain Count Above Standard",
            ),
        ),
        total=f"{prefix} Domain Total",
    )


def _csa_domain(prefix: str, code: str) -> SubscoreColumns:
    return SubscoreColumns(
        code=code,
        bands=_bands(
            (f"{prefix} Domain Percent Level 1", f"{prefix} Domain Count Level 1"),
            (f"{prefix} Domain Percent Level 2", f"{prefix} Domain Count Level 2"),
            (f"{prefix} Domain Percent Level 3", f"{prefix} Domain Count Level 3"),
        ),
        total=f"{prefix} Domain Total",
    )


def _csa_composite(index: int, code: str) -> SubscoreColumns:
    return SubscoreColumns(
        code=code,
        bands=_bands(
            (f"Composite {index} Percent Level 1", f"Composite {index} Count Level 1"),
            (f"Composite {index} Percent Level 2", f"Composite {index} Count Level 2"),
            (f"Composite {index} Percent Level 3", f"Composite {index} Count Level 3"),
        ),
        total=f"Composite {index} Total",
        mean_scale_score=f"Composite {index} Mean Scale Score",
    )


def _elpac_composite(prefix: str, code: str) -> SubscoreColumns:
    """Summative ELPAC oral/written composites carry four levels and a mean."""
    return SubscoreColumns(
        code=code,
        bands=_bands(
            (f"{prefix}PerfLvl1Pcnt", f"{prefix}PerfLvl1Count"),
            (f"{prefix}PerfLvl2Pcnt", f"{prefix}PerfLvl2Count"),
            (f"{prefix}PerfLvl3Pcnt", f"{prefix}PerfLvl3Count"),
            (f"{prefix}PerfLvl4Pcnt", f"{prefix}PerfLvl4Count"),
        ),
        total=f"{prefix}Total",
        mean_scale_score=f"{prefix}MeanSclScr",
    )


def _elpac_domain(prefix: str, code: str) -> SubscoreColumns:
    return SubscoreColumns(
        code=code,
        bands=_bands(
            (f"{prefix}DomainBeginPcnt", f"{prefix}DomainBeginCount"),
            (f"{prefix}DomainModeratePcnt", f"{prefix}DomainModerateCount"),
            (f"{prefix}DomainDevelopedPcnt", f"{prefix}DomainDevelopedCount"),
        ),
        total=f"{prefix}DomainTotal",
    )


def _elpac_initial_composite(prefix: str, code: str) -> SubscoreColumns:
    return SubscoreColumns(
        code=code,
        bands=_bands(
            (
                f"{prefix}MinimallyDevelopedPerfLvlPcnt",
                f"{prefix}MinimallyDevelopedPerfLvlCount",
            ),
            (
                f"{prefix}ModeratelyDevelopedPerfLvlPcnt",
                f"{prefix}ModeratelyDevelopedPerfLvlCount",
            ),
            (f"{prefix}WellDevelopedPerfLvlPcnt", f"{prefix}WellDevelopedPerfLvlCount"),
        ),
        total=f"{prefix}Total",
    )


_SB_LEVELS = _bands(
    ("Percentage Standard Not Met", "Count Standard Not Met"),
    ("Percentage Standard Nearly Met", "Count Standard Nearly Met"),
    ("Percentage Standard Met", "Count Standard Met"),
    ("Percentage Standard Exceeded", "Count Standard Exceeded"),
)

_CAA_LEVELS = _bands(
    ("Percentage Level 1", "Count Level 1"),
    ("Percentage Level 2", "Count Level 2"),
    ("Percentage Level 3", "Count Level 3"),
)

_ELPAC_OVERALL_LEVELS = _bands(
    ("OverallPerfLvl1Pcnt", "OverallPerfLvl1Count"),
    ("OverallPerfLvl2Pcnt", "OverallPerfLvl2Count"),
    ("OverallPerfLvl3Pcnt", "OverallPerfLvl3Count"),
    ("OverallPerfLvl4Pcnt", "OverallPerfLvl4Count"),
)

_ELPAC_INITIAL_LEVELS = _bands(
    ("NoviceELPerfLvlPcnt", "NoviceELPerfLvlCount"),
    ("IntermediateELPerfLvlPcnt", "IntermediateELPerfLvlCount"),
    ("IFEPPerfLvlPcnt", "IFEPPerfLvlCount"),
)


class _ElpacColumns(TypedDict):
    """The column names ELPAC files share, spelled in their camel case."""

    county_code: str
    district_code: str
    school_code: str
    type_id: str
    test_year: str
    test_id: str
    student_group_id: str
    grade: str
    district_name: str
    school_name: str
    students_enrolled: str
    students_tested: str
    students_tested_with_scores: str
    mean_scale_score: str
    overall_total: str


_ELPAC_COMMON: _ElpacColumns = {
    "county_code": "CountyCode",
    "district_code": "DistrictCode",
    "school_code": "SchoolCode",
    "type_id": "TypeID",
    "test_year": "TestYear",
    "test_id": "TestID",
    "student_group_id": "StudentGroupID",
    "grade": "Grade",
    "district_name": "DistrictName",
    "school_name": "SchoolName",
    "students_enrolled": "TotalStudentsEnrolled",
    "students_tested": "TotalStudentsTested",
    "students_tested_with_scores": "TotalStudentsTestedWithScores",
    "mean_scale_score": "OverallMeanSclScr",
    "overall_total": "OverallTotal",
}

LAYOUTS: tuple[ResearchFileLayout, ...] = (
    ResearchFileLayout(
        key="sb",
        program=Program.CAASPP,
        test_type="B",
        test_ids=(1, 2),
        levels=_SB_LEVELS,
        met_or_above=BandColumns(
            "Percentage Standard Met and Above", "Count Standard Met and Above"
        ),
        subscores=(
            _sb_area(1, "AREA_1"),
            _sb_area(2, "AREA_2"),
            _sb_area(3, "AREA_3"),
            _sb_area(4, "AREA_4"),
            _sb_composite_area(1, "COMPOSITE_AREA_1"),
            _sb_composite_area(2, "COMPOSITE_AREA_2"),
        ),
    ),
    ResearchFileLayout(
        key="cast",
        program=Program.CAASPP,
        test_type="X",
        test_ids=(17,),
        levels=_SB_LEVELS,
        met_or_above=BandColumns(
            "Percentage Standard Met and Above", "Count Standard Met and Above"
        ),
        subscores=(
            _cast_domain("Life Sciences", "LIFE_SCIENCES"),
            _cast_domain("Physical Sciences", "PHYSICAL_SCIENCES"),
            _cast_domain("Earth and Space Sciences", "EARTH_AND_SPACE_SCIENCES"),
        ),
    ),
    ResearchFileLayout(
        key="caa",
        program=Program.CAASPP,
        test_type="A",
        test_ids=(3, 4),
        levels=_CAA_LEVELS,
    ),
    ResearchFileLayout(
        key="caas",
        program=Program.CAASPP,
        test_type="Y",
        test_ids=(18,),
        levels=_CAA_LEVELS,
    ),
    # The CSA reported three score ranges and no domains through 2023-24.
    ResearchFileLayout(
        key="csa_ranges",
        program=Program.CAASPP,
        test_type="R",
        test_ids=(39,),
        max_year=2024,
        levels=_bands(
            ("Percent Range 1", "Count Range 1"),
            ("Percent Range 2", "Count Range 2"),
            ("Percent Range 3", "Count Range 3"),
        ),
    ),
    # From 2024-25 the blueprint changed: levels, four domains and two
    # composites, each composite with its own mean scale score.
    ResearchFileLayout(
        key="csa_levels",
        program=Program.CAASPP,
        test_type="R",
        test_ids=(39,),
        min_year=2025,
        mean_scale_score="Overall Mean Scale Score",
        levels=_bands(
            ("Percent Level 1", "Count Level 1"),
            ("Percent Level 2", "Count Level 2"),
            ("Percent Level 3", "Count Level 3"),
        ),
        subscores=(
            _csa_domain("Listening", "LISTENING"),
            _csa_domain("Writing", "WRITING"),
            _csa_domain("Reading", "READING"),
            _csa_domain("Speaking", "SPEAKING"),
            _csa_composite(1, "COMPOSITE_1"),
            _csa_composite(2, "COMPOSITE_2"),
        ),
    ),
    ResearchFileLayout(
        key="elpac_sa",
        program=Program.ELPAC,
        test_type="SA",
        test_ids=(21,),
        levels=_ELPAC_OVERALL_LEVELS,
        subscores=(
            _elpac_composite("OralLang", "ORAL_LANGUAGE"),
            _elpac_composite("WritLang", "WRITTEN_LANGUAGE"),
            _elpac_domain("Listening", "LISTENING"),
            _elpac_domain("Speaking", "SPEAKING"),
            _elpac_domain("Reading", "READING"),
            _elpac_domain("Writing", "WRITING"),
        ),
        **_ELPAC_COMMON,
    ),
    ResearchFileLayout(
        key="elpac_ia",
        program=Program.ELPAC,
        test_type="IA",
        test_ids=(22,),
        levels=_ELPAC_INITIAL_LEVELS,
        subscores=(
            _elpac_initial_composite("OralLang", "ORAL_LANGUAGE"),
            _elpac_initial_composite("WritLang", "WRITTEN_LANGUAGE"),
        ),
        **_ELPAC_COMMON,
    ),
    ResearchFileLayout(
        key="elpac_altsa",
        program=Program.ELPAC,
        test_type="ALTSA",
        test_ids=(23,),
        levels=_bands(
            ("OverallPerfLvl1Pcnt", "OverallPerfLvl1Count"),
            ("OverallPerfLvl2Pcnt", "OverallPerfLvl2Count"),
            ("OverallPerfLvl3Pcnt", "OverallPerfLvl3Count"),
        ),
        **_ELPAC_COMMON,
    ),
    ResearchFileLayout(
        key="elpac_altia",
        program=Program.ELPAC,
        test_type="ALTIA",
        test_ids=(24,),
        levels=_ELPAC_INITIAL_LEVELS,
        **_ELPAC_COMMON,
    ),
)

_LAYOUTS_BY_KEY = {layout.key: layout for layout in LAYOUTS}

# Research file names begin with the program's short code.  ``sb`` files are
# split by subject but share one layout.
_FILENAME_PREFIXES: tuple[tuple[str, str], ...] = (
    ("sb_", "sb"),
    ("cast_", "cast"),
    ("caas_", "caas"),
    ("caa_", "caa"),
    ("csa_", "csa"),
    ("elpac_sa_", "elpac_sa"),
    ("elpac_ia_", "elpac_ia"),
    ("elpac_altsa_", "elpac_altsa"),
    ("elpac_altia_", "elpac_altia"),
    ("altsa_", "elpac_altsa"),
    ("altia_", "elpac_altia"),
    ("sa_", "elpac_sa"),
    ("ia_", "elpac_ia"),
)


def _read_identically(layouts: Sequence[ResearchFileLayout]) -> bool:
    """Whether every layout would extract the same values from a row."""
    signatures = {
        (
            layout.county_code,
            layout.district_code,
            layout.school_code,
            layout.type_id,
            layout.test_year,
            layout.test_id,
            layout.student_group_id,
            layout.grade,
            layout.district_name,
            layout.school_name,
            layout.county_name,
            layout.zip_code,
            layout.students_enrolled,
            layout.students_tested,
            layout.students_tested_with_scores,
            layout.mean_scale_score,
            layout.levels,
            layout.met_or_above,
            layout.overall_total,
            layout.subscores,
        )
        for layout in layouts
    }
    return len(signatures) == 1


class LayoutError(RuntimeError):
    """Raised when a file cannot be matched to a known research file layout."""


def year_from_filename(name: str) -> int | None:
    """Pull the administration year out of a research file name."""
    match = _YEAR_IN_NAME.search(name)
    return int(match.group(1)) if match else None


def candidate_keys(name: str) -> tuple[str, ...]:
    """Layout keys suggested by a file name, most specific first."""
    stem = name.rsplit("/", 1)[-1].lower()
    for prefix, key in _FILENAME_PREFIXES:
        if stem.startswith(prefix):
            return ("csa_levels", "csa_ranges") if key == "csa" else (key,)
    return ()


def resolve_layout(
        name: str, header: list[str], *, test_year: int | None = None
) -> ResearchFileLayout:
    """Choose the layout that matches a file's name, header and year.

    The name only narrows the search; the header decides.  A file whose name
    is unrecognised still loads as long as its columns match exactly one
    layout, which is what makes renamed or hand-extracted files work.
    """
    columns = set(header)
    year = test_year if test_year is not None else year_from_filename(name)

    def matches(layout: ResearchFileLayout) -> bool:
        if not columns.issuperset(layout.required_columns):
            return False
        if layout.levels and not all(
                (band.pct is None or band.pct in columns)
                and (band.count is None or band.count in columns)
                for band in layout.levels
        ):
            return False
        return year is None or layout.covers_year(year)

    for key in candidate_keys(name):
        layout = _LAYOUTS_BY_KEY[key]
        if matches(layout):
            return layout

    found = [layout for layout in LAYOUTS if matches(layout)]
    if not found:
        raise LayoutError(
            f"No research file layout matches {name!r}. "
            f"First columns seen: {header[:12]}"
        )
    if len(found) == 1 or _read_identically(found):
        # Several tests share a column layout exactly -- the alternate
        # assessments for ELA/mathematics and for science, for instance -- and
        # the test is identified by a column in the data, so any of them reads
        # the file correctly.
        return found[0]
    raise LayoutError(
        f"{name!r} matches more than one layout "
        f"({', '.join(match.key for match in found)}); rename the file to its "
        "published research file name so the year and test type can be resolved."
    )
