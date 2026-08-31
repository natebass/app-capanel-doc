"""Census Day enrolment, and how large each student group is.

This is the context the accountability pages otherwise lack.  A Dashboard
result says a group was not rated; it does not say whether that group is
eighteen students or eighteen thousand.  These rows answer that, and let a
school's composition be shown beside its performance.

Census Day is the first Wednesday in October, the single day the state counts
enrolment on, so these are a snapshot rather than an average over the year.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Index
from sqlmodel import Field

from app.model.reference import ApiModel


class EnrollmentRate(ApiModel, table=True):
    """One student group's share of an entity's enrolment."""

    __tablename__ = "enrollment_rates"
    __table_args__ = (
        Index(
            "ix_enrollment_lookup",
            "reporting_year",
            "student_group_code",
            "cds_code",
        ),
    )

    cds_code: str = Field(
        primary_key=True, max_length=14, foreign_key="entities.cds_code"
    )
    reporting_year: int = Field(primary_key=True)
    student_group_code: str = Field(primary_key=True, max_length=8)

    #: Everyone enrolled at the entity on Census Day, repeated on every row.
    total_enrollment: int | None = Field(default=None)
    #: Students in this group.
    subgroup_total: int | None = Field(default=None)
    #: The group as a percentage of total enrolment, as the state rounded it.
    rate: Decimal | None = Field(default=None, max_digits=5, decimal_places=2)
