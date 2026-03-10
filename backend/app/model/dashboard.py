from sqlmodel import SQLModel


class DashboardAggregation(SQLModel):
    """
    Dashboard aggregation response model (legacy single-indicator)
    """

    cds: str
    schoolname: str | None = None
    districtname: str | None = None
    countyname: str | None = None
    studentgroup: str
    currstatus: float | None = None
    priorstatus: float | None = None
    change: float | None = None
    statuslevel: int | None = None  # 0-5, used for gauge display
    changelevel: int | None = None
    color: int | None = None
    indicator: str
    reportingyear: str


class IndicatorSummary(SQLModel):
    """
    New dashboard summary response models
    Summary of a single indicator for the dashboard.
    """

    indicator: str
    currstatus: float | None = None
    priorstatus: float | None = None
    change: float | None = None
    statuslevel: int | None = None
    changelevel: int | None = None
    color: int | None = None
    currdenom: int | None = None


class DashboardSummaryResponse(SQLModel):
    """Response containing all indicators for a school/district/state."""

    cds: str
    rtype: str
    schoolname: str | None = None
    districtname: str | None = None
    countyname: str | None = None
    charter_flag: str | None = None
    reportingyear: str
    indicators: list[IndicatorSummary]


class EquityGroupSummary(SQLModel):
    """Summary of a student group for the equity report."""

    studentgroup: str
    statuslevel: int | None = None
    color: int | None = None
    currdenom: int | None = None


class EquityReportResponse(SQLModel):
    """Response containing student group breakdown for an indicator."""

    cds: str
    indicator: str
    reportingyear: str
    color_counts: dict[str, int]  # {"red": 1, "orange": 2, ...}
    groups: list[EquityGroupSummary]
