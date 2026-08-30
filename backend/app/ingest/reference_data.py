"""Seed data for the CAASPP and ELPAC reference tables.

Everything here is transcribed from the state's published record definitions
and "Understanding Results" pages, which are the authoritative source for the
vocabulary the research files only encode positionally:

* Record layouts and Tables A/B/C --
  ``https://caaspp-elpac.ets.org/caaspp/ResearchFileFormatSB``
  (and the ``CAA``/``CAST``/``CAAS``/``CSA`` variants), plus
  ``https://caaspp-elpac.ets.org/elpac/ResearchFileFormatSA`` (and ``IA``,
  ``ALTSA``, ``ALTIA``).
* Achievement level descriptors --
  ``https://caaspp-elpac.ets.org/caaspp/UnderstandingCAAResults``,
  ``.../UnderstandingCSAResults``,
  ``https://caaspp-elpac.ets.org/elpac/UnderstandingReportsSA`` and
  ``.../UnderstandingReportsIA``.

Seeding is idempotent: rows are upserted on their primary keys so a redeploy
can safely re-run it.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, SQLModel

from app.model.reference import (
    Assessment,
    AssessmentYear,
    GradeLevel,
    PerformanceLevel,
    PerformanceLevelScheme,
    Program,
    StudentGroup,
    SubscoreDefinition,
    SubscoreKind,
)

# The last year the seeds describe.  Reference rows are generated up to this
# year so a newly published file can be imported without a code change; the API
# only advertises years that actually have result rows.
MAX_SEED_YEAR = 2030

# Testing was suspended statewide because of COVID-19, so no results exist.
SUSPENDED_YEARS = frozenset({2020})


# --------------------------------------------------------------------------
# Performance level schemes
# --------------------------------------------------------------------------

_SCHEMES: tuple[tuple[str, str, int, int | None, str], ...] = (
    (
        "SB_ACHIEVEMENT_4",
        "Smarter Balanced achievement levels",
        4,
        3,
        "Four achievement levels reported for Smarter Balanced ELA/mathematics "
        "and the California Science Test.",
    ),
    (
        "AREA_3",
        "Reporting category bands",
        3,
        None,
        "Three bands used for Smarter Balanced areas and CAST domains. The "
        "research files list these above-to-below; they are stored lowest first.",
    ),
    (
        "CAA_3",
        "California Alternate Assessment levels",
        3,
        3,
        "Three levels describing the depth of a student's understanding of "
        "adapted grade-level content.",
    ),
    (
        "CSA_RANGE_3",
        "California Spanish Assessment score ranges",
        3,
        None,
        "Score ranges reported for the CSA through the 2023-24 administration. "
        "The state publishes no proficiency cut for these ranges.",
    ),
    (
        "CSA_LEVEL_3",
        "California Spanish Assessment levels",
        3,
        3,
        "Achievement levels reported for the CSA from the 2024-25 "
        "administration, when the test blueprint changed.",
    ),
    (
        "CSA_BAND_3",
        "California Spanish Assessment domain bands",
        3,
        None,
        "Domain and composite bands reported for the CSA from 2024-25.",
    ),
    (
        "ELPAC_OVERALL_4",
        "Summative ELPAC performance levels",
        4,
        4,
        "Four overall performance levels; level 4 is one of the criteria the "
        "state uses for reclassification.",
    ),
    (
        "ELPAC_DOMAIN_3",
        "Summative ELPAC domain levels",
        3,
        None,
        "Three domain bands reported for listening, speaking, reading and "
        "writing on the Summative ELPAC.",
    ),
    (
        "ELPAC_INITIAL_3",
        "Initial ELPAC performance levels",
        3,
        3,
        "The Initial ELPAC classifies a student rather than scoring "
        "proficiency; Initial Fluent English Proficient is the top level.",
    ),
    (
        "ELPAC_INITIAL_COMPOSITE_3",
        "Initial ELPAC composite levels",
        3,
        None,
        "Oral and written language composite levels on the Initial ELPAC.",
    ),
    (
        "ALT_ELPAC_3",
        "Alternate ELPAC performance levels",
        3,
        3,
        "Three levels reported for the Summative Alternate ELPAC.",
    ),
)

_LEVELS: dict[str, tuple[tuple[int, str, str, str], ...]] = {
    "SB_ACHIEVEMENT_4": (
        (1, "Standard Not Met", "Not Met", "Level 1"),
        (2, "Standard Nearly Met", "Nearly Met", "Level 2"),
        (3, "Standard Met", "Met", "Level 3"),
        (4, "Standard Exceeded", "Exceeded", "Level 4"),
    ),
    "AREA_3": (
        (
            1,
            "Below Standard",
            "Below",
            "Below the standard for this reporting category",
        ),
        (2, "Near Standard", "Near", "Near the standard for this reporting category"),
        (
            3,
            "Above Standard",
            "Above",
            "Above the standard for this reporting category",
        ),
    ),
    "CAA_3": (
        (1, "Limited Understanding", "Level 1", "Level 1"),
        (2, "Foundational Understanding", "Level 2", "Level 2"),
        (3, "Understanding", "Level 3", "Level 3"),
    ),
    "CSA_RANGE_3": (
        (1, "Range 1", "Range 1", "Lowest reported score range"),
        (2, "Range 2", "Range 2", "Middle reported score range"),
        (3, "Range 3", "Range 3", "Highest reported score range"),
    ),
    "CSA_LEVEL_3": (
        (
            1,
            "Level 1",
            "Level 1",
            "A limited degree of grade-appropriate Spanish literacy",
        ),
        (
            2,
            "Level 2",
            "Level 2",
            "A moderate degree of grade-appropriate Spanish literacy",
        ),
        (
            3,
            "Level 3",
            "Level 3",
            "A high degree of grade-appropriate Spanish literacy",
        ),
    ),
    "CSA_BAND_3": (
        (1, "Beginning", "Beginning", "Beginning to demonstrate these skills"),
        (2, "Progressing", "Progressing", "Progressing in these skills"),
        (3, "Well Developed", "Well Developed", "Well developed in these skills"),
    ),
    "ELPAC_OVERALL_4": (
        (1, "Level 1", "Level 1", "Beginning to develop English skills"),
        (2, "Level 2", "Level 2", "Somewhat developed English skills"),
        (3, "Level 3", "Level 3", "Moderately developed English skills"),
        (4, "Level 4", "Level 4", "Well developed English skills"),
    ),
    "ELPAC_DOMAIN_3": (
        (1, "Beginning", "Beginning", "Beginning to develop skills in this domain"),
        (
            2,
            "Somewhat/Moderately Developed",
            "Somewhat/Moderately",
            "Somewhat to moderately developed skills",
        ),
        (3, "Well Developed", "Well Developed", "Well developed skills in this domain"),
    ),
    "ELPAC_INITIAL_3": (
        (1, "Novice English Learner", "Novice", "Novice English skills"),
        (
            2,
            "Intermediate English Learner",
            "Intermediate",
            "Intermediate English skills",
        ),
        (
            3,
            "Initial Fluent English Proficient (IFEP)",
            "IFEP",
            "Well developed English skills",
        ),
    ),
    "ELPAC_INITIAL_COMPOSITE_3": (
        (1, "Minimally Developed", "Minimally", "Minimally developed"),
        (
            2,
            "Somewhat to Moderately Developed",
            "Somewhat/Moderately",
            "Somewhat to moderately developed",
        ),
        (3, "Well Developed", "Well Developed", "Well developed"),
    ),
    "ALT_ELPAC_3": (
        (1, "Level 1", "Level 1", "Level 1"),
        (2, "Level 2", "Level 2", "Level 2"),
        (3, "Level 3", "Level 3", "Level 3"),
    ),
}


# --------------------------------------------------------------------------
# Assessments (Table C of every record layout)
# --------------------------------------------------------------------------

# test_id, code, program, test_type, name, short_name, subject, alternate,
# first_year, sort_order
_ASSESSMENTS: tuple[
    tuple[int, str, Program, str, str, str, str, bool, int, int], ...
] = (
    (
        1,
        "SB_ELA",
        Program.CAASPP,
        "B",
        "Smarter Balanced English Language Arts/Literacy",
        "SB ELA",
        "English Language Arts/Literacy",
        False,
        2015,
        10,
    ),
    (
        2,
        "SB_MATH",
        Program.CAASPP,
        "B",
        "Smarter Balanced Mathematics",
        "SB Math",
        "Mathematics",
        False,
        2015,
        20,
    ),
    (
        17,
        "CAST",
        Program.CAASPP,
        "X",
        "California Science Test",
        "CAST",
        "Science",
        False,
        2019,
        30,
    ),
    (
        39,
        "CSA",
        Program.CAASPP,
        "R",
        "California Spanish Assessment",
        "CSA",
        "Spanish Reading/Language Arts",
        False,
        2019,
        40,
    ),
    (
        3,
        "CAA_ELA",
        Program.CAASPP,
        "A",
        "California Alternate Assessment for English Language Arts/Literacy",
        "CAA ELA",
        "English Language Arts/Literacy",
        True,
        2017,
        50,
    ),
    (
        4,
        "CAA_MATH",
        Program.CAASPP,
        "A",
        "California Alternate Assessment for Mathematics",
        "CAA Math",
        "Mathematics",
        True,
        2017,
        60,
    ),
    (
        18,
        "CAA_SCIENCE",
        Program.CAASPP,
        "Y",
        "California Alternate Assessment for Science",
        "CAA Science",
        "Science",
        True,
        2019,
        70,
    ),
    (
        21,
        "ELPAC_SUMMATIVE",
        Program.ELPAC,
        "SA",
        "Summative ELPAC",
        "Summative ELPAC",
        "English Language Proficiency",
        False,
        2018,
        80,
    ),
    (
        22,
        "ELPAC_INITIAL",
        Program.ELPAC,
        "IA",
        "Initial ELPAC",
        "Initial ELPAC",
        "English Language Proficiency",
        False,
        2018,
        90,
    ),
    (
        23,
        "ALT_ELPAC_SUMMATIVE",
        Program.ELPAC,
        "ALTSA",
        "Summative Alternate ELPAC",
        "Alt Summative ELPAC",
        "English Language Proficiency",
        True,
        2023,
        100,
    ),
    (
        24,
        "ALT_ELPAC_INITIAL",
        Program.ELPAC,
        "ALTIA",
        "Initial Alternate ELPAC",
        "Alt Initial ELPAC",
        "English Language Proficiency",
        True,
        2024,
        110,
    ),
)

_GRADES_NOTE: dict[int, str] = {
    1: "Grades 3-8 and grade 11.",
    2: "Grades 3-8 and grade 11.",
    3: "Grades 3-8 and grade 11.",
    4: "Grades 3-8 and grade 11.",
    17: "Grades 5 and 8, and once in high school (grade 10, 11 or 12).",
    18: "Grades 5 and 8, and once in high school (grade 10, 11 or 12).",
    39: "Grades 3-8 and grades 9-12.",
    21: "Kindergarten through grade 12.",
    22: "Kindergarten through grade 12.",
    23: "Kindergarten through grade 12.",
    24: "Kindergarten through grade 12.",
}


def _level_scheme_for(test_id: int, test_year: int) -> str:
    """Return the achievement level scheme a test used in a given year."""
    match test_id:
        case 1 | 2 | 17:
            return "SB_ACHIEVEMENT_4"
        case 3 | 4 | 18:
            return "CAA_3"
        case 39:
            # The CSA blueprint changed for 2024-25: score ranges became
            # achievement levels and domains began to be reported.
            return "CSA_LEVEL_3" if test_year >= 2025 else "CSA_RANGE_3"
        case 21:
            return "ELPAC_OVERALL_4"
        case 22 | 24:
            return "ELPAC_INITIAL_3"
        case 23:
            return "ALT_ELPAC_3"
        case _:  # pragma: no cover - guarded by the seed table above
            raise ValueError(f"Unknown test id {test_id}")


_PROFICIENT_FROM_LEVEL = {
    code: proficient for code, _name, _count, proficient, _description in _SCHEMES
}


def proficient_from_level(test_id: int, test_year: int) -> int | None:
    """The lowest level a test counts as meeting the standard, if any.

    Used to derive a "met or above" figure for the tests whose research files
    do not publish one; Smarter Balanced and CAST publish it directly.
    """
    return _PROFICIENT_FROM_LEVEL.get(_level_scheme_for(test_id, test_year))


def level_scheme_for(test_id: int, test_year: int) -> str:
    """Public alias for the year-aware achievement level scheme lookup."""
    return _level_scheme_for(test_id, test_year)


# --------------------------------------------------------------------------
# Subscores
# --------------------------------------------------------------------------

# code, kind, name, band scheme, has mean scale score, sort order
type _SubscoreSeed = tuple[str, SubscoreKind, str, str, bool, int]

_SB_ELA_SUBSCORES: tuple[_SubscoreSeed, ...] = (
    ("AREA_1", SubscoreKind.AREA, "Reading", "AREA_3", False, 10),
    ("AREA_2", SubscoreKind.AREA, "Writing", "AREA_3", False, 20),
    ("AREA_3", SubscoreKind.AREA, "Speaking/Listening", "AREA_3", False, 30),
    ("AREA_4", SubscoreKind.AREA, "Research/Inquiry", "AREA_3", False, 40),
    (
        "COMPOSITE_AREA_1",
        SubscoreKind.COMPOSITE_AREA,
        "Reading and Listening",
        "AREA_3",
        False,
        50,
    ),
    (
        "COMPOSITE_AREA_2",
        SubscoreKind.COMPOSITE_AREA,
        "Writing and Research",
        "AREA_3",
        False,
        60,
    ),
)

# Mathematics reports no fourth area; the research file carries the columns but
# leaves them at zero.
_SB_MATH_SUBSCORES: tuple[_SubscoreSeed, ...] = (
    ("AREA_1", SubscoreKind.AREA, "Concepts and Procedures", "AREA_3", False, 10),
    ("AREA_2", SubscoreKind.AREA, "Problem Solving", "AREA_3", False, 20),
    ("AREA_3", SubscoreKind.AREA, "Communicating Reasoning", "AREA_3", False, 30),
    (
        "COMPOSITE_AREA_1",
        SubscoreKind.COMPOSITE_AREA,
        "Concepts and Procedures",
        "AREA_3",
        False,
        50,
    ),
    (
        "COMPOSITE_AREA_2",
        SubscoreKind.COMPOSITE_AREA,
        "Mathematical Practices",
        "AREA_3",
        False,
        60,
    ),
)

_CAST_SUBSCORES: tuple[_SubscoreSeed, ...] = (
    ("LIFE_SCIENCES", SubscoreKind.DOMAIN, "Life Sciences", "AREA_3", False, 10),
    (
        "PHYSICAL_SCIENCES",
        SubscoreKind.DOMAIN,
        "Physical Sciences",
        "AREA_3",
        False,
        20,
    ),
    (
        "EARTH_AND_SPACE_SCIENCES",
        SubscoreKind.DOMAIN,
        "Earth and Space Sciences",
        "AREA_3",
        False,
        30,
    ),
)

_CSA_SUBSCORES_2025: tuple[_SubscoreSeed, ...] = (
    ("LISTENING", SubscoreKind.DOMAIN, "Listening", "CSA_BAND_3", False, 10),
    ("WRITING", SubscoreKind.DOMAIN, "Writing", "CSA_BAND_3", False, 20),
    ("READING", SubscoreKind.DOMAIN, "Reading", "CSA_BAND_3", False, 30),
    ("SPEAKING", SubscoreKind.DOMAIN, "Speaking", "CSA_BAND_3", False, 40),
    ("COMPOSITE_1", SubscoreKind.COMPOSITE, "Oral Literacy", "CSA_BAND_3", True, 50),
    ("COMPOSITE_2", SubscoreKind.COMPOSITE, "Written Literacy", "CSA_BAND_3", True, 60),
)

_ELPAC_SA_SUBSCORES: tuple[_SubscoreSeed, ...] = (
    (
        "ORAL_LANGUAGE",
        SubscoreKind.COMPOSITE,
        "Oral Language",
        "ELPAC_OVERALL_4",
        True,
        10,
    ),
    (
        "WRITTEN_LANGUAGE",
        SubscoreKind.COMPOSITE,
        "Written Language",
        "ELPAC_OVERALL_4",
        True,
        20,
    ),
    ("LISTENING", SubscoreKind.DOMAIN, "Listening", "ELPAC_DOMAIN_3", False, 30),
    ("SPEAKING", SubscoreKind.DOMAIN, "Speaking", "ELPAC_DOMAIN_3", False, 40),
    ("READING", SubscoreKind.DOMAIN, "Reading", "ELPAC_DOMAIN_3", False, 50),
    ("WRITING", SubscoreKind.DOMAIN, "Writing", "ELPAC_DOMAIN_3", False, 60),
)

_ELPAC_IA_SUBSCORES: tuple[_SubscoreSeed, ...] = (
    (
        "ORAL_LANGUAGE",
        SubscoreKind.COMPOSITE,
        "Oral Language",
        "ELPAC_INITIAL_COMPOSITE_3",
        False,
        10,
    ),
    (
        "WRITTEN_LANGUAGE",
        SubscoreKind.COMPOSITE,
        "Written Language",
        "ELPAC_INITIAL_COMPOSITE_3",
        False,
        20,
    ),
)


def subscores_for(test_id: int, test_year: int) -> tuple[_SubscoreSeed, ...]:
    """Return the subscores a test published in a given year."""
    match test_id:
        case 1:
            return _SB_ELA_SUBSCORES
        case 2:
            return _SB_MATH_SUBSCORES
        case 17:
            return _CAST_SUBSCORES
        case 39:
            return _CSA_SUBSCORES_2025 if test_year >= 2025 else ()
        case 21:
            return _ELPAC_SA_SUBSCORES
        case 22:
            return _ELPAC_IA_SUBSCORES
        case _:
            return ()


# --------------------------------------------------------------------------
# Student groups (Table A)
# --------------------------------------------------------------------------

# The two programs reuse identifiers with different wording, so each program
# carries its own copy of the table.
_CAASPP_GROUPS: tuple[tuple[int, str, str], ...] = (
    (1, "All Students", "All Students"),
    (128, "Reported disabilities", "Disability Status"),
    (99, "No reported disabilities", "Disability Status"),
    (31, "Socioeconomically disadvantaged", "Economic Status"),
    (111, "Not socioeconomically disadvantaged", "Economic Status"),
    (
        6,
        "IFEP, RFEP, and EO (Fluent English proficient and English only)",
        "English-Language Fluency",
    ),
    (7, "IFEP (Initial fluent English proficient)", "English-Language Fluency"),
    (8, "RFEP (Reclassified fluent English proficient)", "English-Language Fluency"),
    (120, "ELs enrolled less than 12 months", "English-Language Fluency"),
    (142, "ELs enrolled 12 months or more", "English-Language Fluency"),
    (160, "EL (English learner, excluding RFEP)", "English-Language Fluency"),
    (243, "ADEL (Adult English learner)", "English-Language Fluency"),
    (180, "EO (English only)", "English-Language Fluency"),
    (170, "Ever-EL", "English-Language Fluency"),
    (250, "LTEL (Long-Term English learner)", "English-Language Fluency"),
    (251, "AR-LTEL (At-Risk of becoming LTEL)", "English-Language Fluency"),
    (252, "Never-EL", "English-Language Fluency"),
    (190, "TBD (To be determined)", "English-Language Fluency"),
    (75, "American Indian or Alaska Native", "Race and Ethnicity"),
    (76, "Asian", "Race and Ethnicity"),
    (74, "Black or African American", "Race and Ethnicity"),
    (77, "Filipino", "Race and Ethnicity"),
    (78, "Hispanic or Latino", "Race and Ethnicity"),
    (79, "Native Hawaiian or Pacific Islander", "Race and Ethnicity"),
    (80, "White", "Race and Ethnicity"),
    (144, "Two or more races", "Race and Ethnicity"),
    (
        201,
        "American Indian or Alaska Native",
        "Ethnicity for Socioeconomically Disadvantaged",
    ),
    (202, "Asian", "Ethnicity for Socioeconomically Disadvantaged"),
    (200, "Black or African American", "Ethnicity for Socioeconomically Disadvantaged"),
    (203, "Filipino", "Ethnicity for Socioeconomically Disadvantaged"),
    (204, "Hispanic or Latino", "Ethnicity for Socioeconomically Disadvantaged"),
    (
        205,
        "Native Hawaiian or Pacific Islander",
        "Ethnicity for Socioeconomically Disadvantaged",
    ),
    (206, "White", "Ethnicity for Socioeconomically Disadvantaged"),
    (207, "Two or more races", "Ethnicity for Socioeconomically Disadvantaged"),
    (
        221,
        "American Indian or Alaska Native",
        "Ethnicity for Not Socioeconomically Disadvantaged",
    ),
    (222, "Asian", "Ethnicity for Not Socioeconomically Disadvantaged"),
    (
        220,
        "Black or African American",
        "Ethnicity for Not Socioeconomically Disadvantaged",
    ),
    (223, "Filipino", "Ethnicity for Not Socioeconomically Disadvantaged"),
    (224, "Hispanic or Latino", "Ethnicity for Not Socioeconomically Disadvantaged"),
    (
        225,
        "Native Hawaiian or Pacific Islander",
        "Ethnicity for Not Socioeconomically Disadvantaged",
    ),
    (226, "White", "Ethnicity for Not Socioeconomically Disadvantaged"),
    (227, "Two or more races", "Ethnicity for Not Socioeconomically Disadvantaged"),
    (4, "Female", "Gender"),
    (3, "Male", "Gender"),
    (28, "Migrant education", "Migrant"),
    (29, "Not migrant education", "Migrant"),
    (90, "Not a high school graduate", "Parent Education"),
    (91, "High school graduate", "Parent Education"),
    (92, "Some college (includes AA degree)", "Parent Education"),
    (93, "College graduate", "Parent Education"),
    (94, "Graduate school/Postgraduate", "Parent Education"),
    (121, "Declined to state", "Parent Education"),
    (50, "Armed forces family member", "Military Status"),
    (51, "Not armed forces family member", "Military Status"),
    (52, "Homeless", "Homeless Status"),
    (53, "Not homeless", "Homeless Status"),
    (240, "Foster youth", "Foster Status"),
    (241, "Not foster youth", "Foster Status"),
)

_ELPAC_GROUPS: tuple[tuple[int, str, str], ...] = (
    (1, "All Students", "All Students"),
    (4, "Female", "Gender"),
    (3, "Male", "Gender"),
    (228, "Spanish", "Primary Language"),
    (229, "Vietnamese", "Primary Language"),
    (230, "Mandarin (Putonghua)", "Primary Language"),
    (231, "Arabic", "Primary Language"),
    (232, "Filipino (Pilipino or Tagalog)", "Primary Language"),
    (233, "Cantonese", "Primary Language"),
    (234, "Korean", "Primary Language"),
    (235, "Hmong", "Primary Language"),
    (236, "Punjabi", "Primary Language"),
    (237, "Russian", "Primary Language"),
    (238, "All Remaining Languages", "Primary Language"),
    (28, "Migrant Education", "Migrant"),
    (99, "Students not Receiving Special Education Services", "Disability Status"),
    (128, "Students Receiving Special Education Services", "Disability Status"),
    (
        239,
        "Students Receiving Special Education Services Tested with Alternate Assessment for any or all Domains",
        "Disability Status",
    ),
    (31, "Economically Disadvantaged", "Economic Status"),
    (111, "Not Economically Disadvantaged", "Economic Status"),
    (74, "Black or African American", "Ethnicity"),
    (75, "American Indian or Alaska Native", "Ethnicity"),
    (76, "Asian", "Ethnicity"),
    (77, "Filipino", "Ethnicity"),
    (78, "Hispanic or Latino", "Ethnicity"),
    (79, "Native Hawaiian or Other Pacific Islander", "Ethnicity"),
    (80, "White", "Ethnicity"),
    (144, "Two or More Races", "Ethnicity"),
    (
        120,
        "English Learners (ELs) Enrolled in School in the U.S. Fewer Than 12 Months",
        "English Learners",
    ),
    (
        142,
        "English Learners Enrolled in School in the U.S. 12 Months or More",
        "English Learners",
    ),
    (160, "All English Learners", "English Learners"),
    (50, "Military", "Military Status"),
    (51, "Not Military", "Military Status"),
    (52, "Homeless", "Homeless Status"),
    (53, "Not Homeless", "Homeless Status"),
    (240, "Foster youth", "Foster Status"),
    (241, "Not foster youth", "Foster Status"),
)

_CATEGORY_ORDER: tuple[str, ...] = (
    "All Students",
    "Gender",
    "Race and Ethnicity",
    "Ethnicity",
    "English-Language Fluency",
    "English Learners",
    "Primary Language",
    "Economic Status",
    "Disability Status",
    "Parent Education",
    "Foster Status",
    "Homeless Status",
    "Migrant",
    "Military Status",
    "Ethnicity for Socioeconomically Disadvantaged",
    "Ethnicity for Not Socioeconomically Disadvantaged",
)


# --------------------------------------------------------------------------
# Grades (Table B)
# --------------------------------------------------------------------------

_GRADES: tuple[tuple[str, str, int, bool], ...] = (
    ("KN", "Kindergarten", 0, False),
    ("01", "Grade 1", 1, False),
    ("02", "Grade 2", 2, False),
    ("03", "Grade 3", 3, False),
    ("04", "Grade 4", 4, False),
    ("05", "Grade 5", 5, False),
    ("06", "Grade 6", 6, False),
    ("07", "Grade 7", 7, False),
    ("08", "Grade 8", 8, False),
    ("09", "Grade 9", 9, False),
    ("10", "Grade 10", 10, False),
    ("11", "Grade 11", 11, False),
    ("12", "Grade 12", 12, False),
    ("14", "All High School", 90, True),
    ("99", "High School Graduating Class", 95, True),
    ("13", "All Grades", 99, True),
)


# --------------------------------------------------------------------------
# Counties
# --------------------------------------------------------------------------

# Research file rows carry district and school names but never a county name,
# so the 58 counties (plus the statewide row) are seeded here.  Names are taken
# from the entities file that accompanies every statewide research file.
COUNTY_NAMES: dict[str, str] = {
    "00": "State of California",
    "01": "Alameda",
    "02": "Alpine",
    "03": "Amador",
    "04": "Butte",
    "05": "Calaveras",
    "06": "Colusa",
    "07": "Contra Costa",
    "08": "Del Norte",
    "09": "El Dorado",
    "10": "Fresno",
    "11": "Glenn",
    "12": "Humboldt",
    "13": "Imperial",
    "14": "Inyo",
    "15": "Kern",
    "16": "Kings",
    "17": "Lake",
    "18": "Lassen",
    "19": "Los Angeles",
    "20": "Madera",
    "21": "Marin",
    "22": "Mariposa",
    "23": "Mendocino",
    "24": "Merced",
    "25": "Modoc",
    "26": "Mono",
    "27": "Monterey",
    "28": "Napa",
    "29": "Nevada",
    "30": "Orange",
    "31": "Placer",
    "32": "Plumas",
    "33": "Riverside",
    "34": "Sacramento",
    "35": "San Benito",
    "36": "San Bernardino",
    "37": "San Diego",
    "38": "San Francisco",
    "39": "San Joaquin",
    "40": "San Luis Obispo",
    "41": "San Mateo",
    "42": "Santa Barbara",
    "43": "Santa Clara",
    "44": "Santa Cruz",
    "45": "Shasta",
    "46": "Sierra",
    "47": "Siskiyou",
    "48": "Solano",
    "49": "Sonoma",
    "50": "Stanislaus",
    "51": "Sutter",
    "52": "Tehama",
    "53": "Trinity",
    "54": "Tulare",
    "55": "Tuolumne",
    "56": "Ventura",
    "57": "Yolo",
    "58": "Yuba",
}


# --------------------------------------------------------------------------
# Seeding
# --------------------------------------------------------------------------


def _upsert(
    session: Session, model: type[SQLModel], rows: Sequence[dict[str, object]]
) -> None:
    """Insert rows, updating any that already exist on the primary key."""
    if not rows:
        return
    table = model.__table__  # type: ignore[attr-defined]
    key_columns = {column.name for column in table.primary_key.columns}
    statement = insert(table).values(list(rows))
    updatable = {
        name: statement.excluded[name] for name in rows[0] if name not in key_columns
    }
    if updatable:
        statement = statement.on_conflict_do_update(
            index_elements=sorted(key_columns), set_=updatable
        )
    else:
        statement = statement.on_conflict_do_nothing(index_elements=sorted(key_columns))
    session.exec(statement)  # type: ignore[call-overload]


def _seed_years() -> Iterable[int]:
    return (
        year for year in range(2015, MAX_SEED_YEAR + 1) if year not in SUSPENDED_YEARS
    )


def seed_reference_data(session: Session) -> None:
    """Populate every reference table.  Safe to call repeatedly."""
    _upsert(
        session,
        PerformanceLevelScheme,
        [
            {
                "code": code,
                "name": name,
                "level_count": count,
                "proficient_from_level": proficient,
                "description": description,
            }
            for code, name, count, proficient, description in _SCHEMES
        ],
    )
    _upsert(
        session,
        PerformanceLevel,
        [
            {
                "scheme_code": scheme,
                "level_number": number,
                "name": name,
                "short_name": short,
                "description": description,
            }
            for scheme, levels in _LEVELS.items()
            for number, name, short, description in levels
        ],
    )
    _upsert(
        session,
        Assessment,
        [
            {
                "test_id": test_id,
                "code": code,
                "program": program,
                "test_type": test_type,
                "name": name,
                "short_name": short_name,
                "subject": subject,
                "is_alternate": is_alternate,
                "sort_order": sort_order,
            }
            for test_id, code, program, test_type, name, short_name, subject, is_alternate, _first_year, sort_order in _ASSESSMENTS
        ],
    )

    assessment_years: list[dict[str, object]] = []
    subscore_rows: list[dict[str, object]] = []
    for test_id, *_rest in _ASSESSMENTS:
        first_year = next(row[8] for row in _ASSESSMENTS if row[0] == test_id)
        for year in _seed_years():
            if year < first_year:
                continue
            assessment_years.append(
                {
                    "test_id": test_id,
                    "test_year": year,
                    "level_scheme_code": _level_scheme_for(test_id, year),
                    "reports_mean_scale_score": True,
                    "grades_note": _GRADES_NOTE.get(test_id),
                }
            )
            for code, kind, name, band_scheme, has_mean, order in subscores_for(
                test_id, year
            ):
                subscore_rows.append(
                    {
                        "test_id": test_id,
                        "test_year": year,
                        "code": code,
                        "kind": kind,
                        "name": name,
                        "band_scheme_code": band_scheme,
                        "reports_mean_scale_score": has_mean,
                        "sort_order": order,
                    }
                )
    _upsert(session, AssessmentYear, assessment_years)
    _upsert(session, SubscoreDefinition, subscore_rows)

    group_rows: list[dict[str, object]] = []
    for program, groups in (
        (Program.CAASPP, _CAASPP_GROUPS),
        (Program.ELPAC, _ELPAC_GROUPS),
    ):
        for position, (group_id, name, category) in enumerate(groups):
            category_rank = (
                _CATEGORY_ORDER.index(category) if category in _CATEGORY_ORDER else 99
            )
            group_rows.append(
                {
                    "program": program,
                    "student_group_id": group_id,
                    "code": f"{group_id:03d}",
                    "name": name,
                    "category": category,
                    "sort_order": category_rank * 100 + position,
                }
            )
    _upsert(session, StudentGroup, group_rows)

    _upsert(
        session,
        GradeLevel,
        [
            {
                "code": code,
                "label": label,
                "sort_order": order,
                "is_aggregate": is_aggregate,
            }
            for code, label, order, is_aggregate in _GRADES
        ],
    )
    session.commit()
