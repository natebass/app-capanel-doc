import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Column, DateTime, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.core.utils import get_datetime_utc

if TYPE_CHECKING:
    pass


# ============================================================
# ACADEMIC INDICATOR TABLE (Base)
# ============================================================


class AcademicIndicatorBase(SQLModel):
    """
    Shared properties for AcademicIndicator (California Dashboard data)
    Current metrics have been moved to CurrentMetrics table.
    """

    # Identifiers
    cds: str = Field(primary_key=True, max_length=14, index=True)  # 14-char CDS code
    rtype: str = Field(max_length=1, index=True)  # S/D/X (School/District/State)
    schoolname: str | None = Field(default=None, max_length=255, index=True)
    districtname: str | None = Field(default=None, max_length=255, index=True)
    countyname: str | None = Field(default=None, max_length=255, index=True)

    # Flags (Y or blank)
    charter_flag: str | None = Field(default=None, max_length=1, index=True)
    coe_flag: str | None = Field(default=None, max_length=1, index=True)
    dass_flag: str | None = Field(default=None, max_length=1, index=True)

    # Demographics
    studentgroup: str = Field(index=True, max_length=10)  # ALL, AA, AI, AS, etc.

    # Prior metrics
    priordenom: int | None = Field(default=None, index=True)
    priorstatus: float | None = Field(default=None, index=True)

    # Performance
    change: float | None = Field(default=None, index=True)
    statuslevel: int | None = Field(default=None, index=True)  # 1-5 or 0
    changelevel: int | None = Field(default=None, index=True)  # 1-5 or 0
    color: int | None = Field(default=None, index=True)  # 1-5 or 0
    box: int | None = Field(default=None, index=True)  # 0-250

    # Accountability
    priornsizemet: str | None = Field(default=None, max_length=10, index=True)
    accountabilitymet: str | None = Field(default=None, max_length=10, index=True)
    hscutpoints: str | None = Field(default=None, max_length=255)
    pairshare_method: str | None = Field(default=None, max_length=255)

    # Participation (prior)
    priorprate_enrolled: int | None = Field(default=None, index=True)
    priorprate_tested: int | None = Field(default=None, index=True)
    priorprate: float | None = Field(default=None, index=True)
    priornumprloss: int | None = Field(default=None)
    priordenom_withoutprloss: int | None = Field(default=None)
    priorstatus_withoutprloss: float | None = Field(default=None)

    # Metadata
    indicator: str = Field(default="ELA", max_length=10, index=True)
    reportingyear: str = Field(max_length=10, index=True)  # e.g., "2025"

    # === Extended fields for all indicator types ===

    # Common fields (Chronic, Suspension, Graduation, ELPI)
    priornumer: int | None = Field(default=None, index=True)
    smalldenom: str | None = Field(default=None, max_length=10, index=True)
    priorcertifyflag: str | None = Field(default=None, max_length=10, index=True)
    dataerrorflag: str | None = Field(default=None, max_length=10, index=True)

    # Suspension-specific
    school_type: str | None = Field(
        default=None, max_length=50, index=True
    )  # 'type' column

    # Graduation-specific
    fiveyrnumer: int | None = Field(default=None)

    # ELPI-specific (English Learner Progress) - Prior fields
    priorprogressed: int | None = Field(default=None, index=True)
    priormaintainpl4: int | None = Field(default=None)
    priormaintainoth: int | None = Field(default=None)
    priordeclined: int | None = Field(default=None)
    priorprogressed_alternate: int | None = Field(default=None)
    priormaintainpl3_alternate: int | None = Field(default=None)
    priornotprognotmain_alternate: int | None = Field(default=None)
    prior95: int | None = Field(default=None)

    # CCI studentgroup percentage
    studentgroup_pct: float | None = Field(default=None, index=True)


class AcademicIndicator(AcademicIndicatorBase, table=True):
    __table_args__ = (
        UniqueConstraint(
            "cds",
            "indicator",
            "studentgroup",
            "reportingyear",
            name="uq_indicator_natural_key",
        ),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
        index=True,
    )
    # CCI-specific (stored as JSON to avoid 100+ columns)
    cci_details: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))

    # Relationship to CurrentMetrics (one-to-many)
    current_metrics: list["CurrentMetrics"] = Relationship(
        back_populates="academic_indicator"
    )


class AcademicIndicatorCreate(AcademicIndicatorBase):
    pass


class AcademicIndicatorUpdate(SQLModel):
    cds: str | None = Field(default=None, max_length=14)
    rtype: str | None = Field(default=None, max_length=1)
    schoolname: str | None = Field(default=None, max_length=255)
    districtname: str | None = Field(default=None, max_length=255)
    countyname: str | None = Field(default=None, max_length=255)
    charter_flag: str | None = Field(default=None, max_length=1)
    coe_flag: str | None = Field(default=None, max_length=1)
    dass_flag: str | None = Field(default=None, max_length=1)
    studentgroup: str | None = Field(default=None, max_length=10)
    priordenom: int | None = Field(default=None)
    priorstatus: float | None = Field(default=None)
    change: float | None = Field(default=None)
    statuslevel: int | None = Field(default=None)
    changelevel: int | None = Field(default=None)
    color: int | None = Field(default=None)
    box: int | None = Field(default=None)
    priornsizemet: str | None = Field(default=None, max_length=10)
    accountabilitymet: str | None = Field(default=None, max_length=10)
    hscutpoints: str | None = Field(default=None, max_length=255)
    pairshare_method: str | None = Field(default=None, max_length=255)
    priorprate_enrolled: int | None = Field(default=None)
    priorprate_tested: int | None = Field(default=None)
    priorprate: float | None = Field(default=None)
    priornumprloss: int | None = Field(default=None)
    priordenom_withoutprloss: int | None = Field(default=None)
    priorstatus_withoutprloss: float | None = Field(default=None)
    indicator: str | None = Field(default=None, max_length=10)
    reportingyear: str | None = Field(default=None, max_length=10)


class AcademicIndicatorPublic(AcademicIndicatorBase):
    id: uuid.UUID
    created_at: datetime | None = None


class AcademicIndicatorsPublic(SQLModel):
    data: list[AcademicIndicatorPublic]
    count: int


# ============================================================
# CURRENT METRICS TABLE (Separated for timestamp tracking)
# ============================================================


class CurrentMetricsBase(SQLModel):
    """
    Current metrics extracted into separate table for timestamp tracking.
    Foreign key links to AcademicIndicator via cds.
    """

    # Foreign key to AcademicIndicator
    cds: str = Field(
        foreign_key="academicindicator.cds",
        max_length=14,
        index=True,
    )

    # Current metrics (basic)
    currdenom: int | None = Field(default=None, index=True)
    currstatus: float | None = Field(default=None, index=True)

    # Accountability (current)
    currnsizemet: str | None = Field(default=None, max_length=10, index=True)

    # Participation (current)
    currprate_enrolled: int | None = Field(default=None, index=True)
    currprate_tested: int | None = Field(default=None, index=True)
    currprate: float | None = Field(default=None, index=True)
    currnumprloss: int | None = Field(default=None)
    currdenom_withoutprloss: int | None = Field(default=None)
    currstatus_withoutprloss: float | None = Field(default=None)

    # Common current fields (Chronic, Suspension, Graduation, ELPI)
    currnumer: int | None = Field(default=None, index=True)
    certifyflag: str | None = Field(default=None, max_length=10, index=True)

    # ELPI-specific current fields
    currprogressed: int | None = Field(default=None, index=True)
    currmaintainpl4: int | None = Field(default=None)
    currmaintainoth: int | None = Field(default=None)
    currdeclined: int | None = Field(default=None)
    currprogressed_alternate: int | None = Field(default=None)
    currmaintainpl3_alternate: int | None = Field(default=None)
    currnotprognotmain_alternate: int | None = Field(default=None)
    curr95: int | None = Field(default=None)


class CurrentMetrics(CurrentMetricsBase, table=True):
    """
    Current metrics table with timestamp tracking.
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
        index=True,
    )

    # Relationship back to AcademicIndicator
    academic_indicator: "AcademicIndicator" = Relationship(
        back_populates="current_metrics"
    )


class CurrentMetricsCreate(CurrentMetricsBase):
    pass


class CurrentMetricsUpdate(SQLModel):
    currdenom: int | None = Field(default=None)
    currstatus: float | None = Field(default=None)
    currnsizemet: str | None = Field(default=None, max_length=10)
    currprate_enrolled: int | None = Field(default=None)
    currprate_tested: int | None = Field(default=None)
    currprate: float | None = Field(default=None)
    currnumprloss: int | None = Field(default=None)
    currdenom_withoutprloss: int | None = Field(default=None)
    currstatus_withoutprloss: float | None = Field(default=None)
    currnumer: int | None = Field(default=None)
    certifyflag: str | None = Field(default=None, max_length=10)
    currprogressed: int | None = Field(default=None)
    currmaintainpl4: int | None = Field(default=None)
    currmaintainoth: int | None = Field(default=None)
    currdeclined: int | None = Field(default=None)
    currprogressed_alternate: int | None = Field(default=None)
    currmaintainpl3_alternate: int | None = Field(default=None)
    currnotprognotmain_alternate: int | None = Field(default=None)
    curr95: int | None = Field(default=None)


class CurrentMetricsPublic(CurrentMetricsBase):
    id: uuid.UUID
    updated_at: datetime | None = None
