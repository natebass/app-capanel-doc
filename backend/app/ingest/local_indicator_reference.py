"""Seed data for the LCFF Local Indicators.

The seven priorities as the state names them on
https://www.cde.ca.gov/ta/ac/cm/localindicators.asp.  Priorities 4, 5 and 8 are
LCFF priorities too but are measured by the state indicators rather than
self-reported, which is why the numbering has gaps.
"""

from __future__ import annotations

from sqlmodel import Session

from app.model.local_indicators import LocalIndicatorPriority

# (number, name, short name, county-office only, description)
type _Priority = tuple[int, str, str, bool, str]

_PRIORITIES: tuple[_Priority, ...] = (
    (
        1,
        "Basic Services and Conditions",
        "Basic Services",
        False,
        "Whether teachers are appropriately assigned, every student has "
        "standards-aligned instructional materials, and school facilities are "
        "maintained in good repair.",
    ),
    (
        2,
        "Implementation of State Academic Standards",
        "Academic Standards",
        False,
        "How far the local educational agency has implemented the state "
        "academic standards, rated by subject and by the support given to "
        "teachers.",
    ),
    (
        3,
        "Parent and Family Engagement",
        "Family Engagement",
        False,
        "How the local educational agency builds relationships with families, "
        "builds partnerships for student outcomes, and seeks family input in "
        "decision making.",
    ),
    (
        6,
        "School Climate",
        "School Climate",
        False,
        "What local surveys of students, families and staff say about safety "
        "and connectedness, and what the agency intends to do about it.",
    ),
    (
        7,
        "Access to a Broad Course of Study",
        "Broad Course of Study",
        False,
        "Whether every student has access to a broad course of study, the "
        "barriers to that access, and what the agency is changing.",
    ),
    (
        9,
        "Coordination of Services for Expelled Students",
        "Expelled Students",
        True,
        "How a county office of education coordinates instruction for expelled "
        "students. Reported only by county offices.",
    ),
    (
        10,
        "Coordination of Services for Foster Youth",
        "Foster Youth",
        True,
        "How a county office of education coordinates services for foster "
        "youth. Reported only by county offices.",
    ),
)

#: The order the Dashboard lists them in is the priority number itself.
PRIORITY_NUMBERS = tuple(priority[0] for priority in _PRIORITIES)


def seed_local_indicator_reference(session: Session) -> None:
    """Populate the priority lookup.  Safe to call repeatedly."""
    from app.ingest.reference_data import _upsert

    _upsert(
        session,
        LocalIndicatorPriority,
        [
            {
                "priority_number": number,
                "name": name,
                "short_name": short_name,
                "county_office_only": coe_only,
                "description": description,
                "sort_order": index,
            }
            for index, (number, name, short_name, coe_only, description) in enumerate(
                _PRIORITIES, start=1
            )
        ],
    )
