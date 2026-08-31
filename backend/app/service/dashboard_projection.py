"""Apply the state's Dashboard rules to a status and change figure.

This is the accountability arithmetic: given where an entity stands and how
far it moved, decide the status level, the change level and the color.  The
bands and grids come from :mod:`app.ingest.dashboard_reference`, which
transcribes the state's published tables, so this module holds only the rules
that are not expressible as data.

It has two callers with very different standing:

* the loader, which uses it to *check* what the state published, and
* the projection, which uses it to work out a provisional color in the months
  between the underlying data being certified and the Dashboard being
  released.

A projected figure is never a published one.  Everything this module produces
for an unpublished year is stored with ``is_projected`` set, and the caller is
responsible for keeping the two apart.

What a projection cannot capture: the state's academic denominator counts only
*continuously enrolled* students and applies a participation-rate penalty by
substituting the lowest obtainable scale score for untested students.  The
research files expose neither, so a projected academic status is close to but
not the same as the figure the state will publish.  Rate indicators
(absenteeism, suspension, graduation) have no such adjustment and project
exactly, given the same underlying counts.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlmodel import Session, select

from app.model.dashboard import DEFAULT_VARIANT, DashboardColorCell, DashboardCutpoint

# Indicators whose small-denominator grid is three change bands wide.  The cut
# points do not change; the two extreme bands fold inward.
COLLAPSING_INDICATORS = frozenset({"CHRO", "SUSP", "CCI"})

# Indicators whose files carry a small-denominator flag at all.
SMALL_DENOMINATOR_INDICATORS = frozenset({"CHRO", "SUSP", "CCI", "GRAD"})

# Below this many students an entity is judged on the reduced grid.
SMALL_DENOMINATOR_THRESHOLD = 150

_COLLAPSE = {1: 2, 5: 4}

STATUS = "status"
CHANGE = "change"


@dataclass(frozen=True, slots=True)
class Band:
    """One status or change band.  Either bound may be open."""

    level: int
    lower: Decimal | None
    upper: Decimal | None
    label: str

    def contains(self, value: Decimal) -> bool:
        if self.lower is not None and value < self.lower:
            return False
        return not (self.upper is not None and value > self.upper)


@dataclass(frozen=True, slots=True)
class Judgement:
    """What the rules make of one entity's figures."""

    status_level: int | None
    change_level: int | None
    color: int | None
    status_label: str | None = None
    change_label: str | None = None


class DashboardRules:
    """The published bands and grids, ready to apply."""

    def __init__(
        self,
        bands: dict[tuple[str, str, str], list[Band]],
        grid: dict[tuple[str, str, bool, int, int], int | None],
    ) -> None:
        self._bands = bands
        self._grid = grid

    @classmethod
    def load(cls, session: Session) -> DashboardRules:
        """Read every band and grid cell out of the reference tables."""
        bands: dict[tuple[str, str, str], list[Band]] = {}
        for row in session.exec(select(DashboardCutpoint)).all():
            key = (row.indicator_code, row.variant, row.kind)
            bands.setdefault(key, []).append(
                Band(row.level, row.lower_bound, row.upper_bound, row.label)
            )
        for entries in bands.values():
            # Best band first, so a value that falls in a published gap --
            # the tables are written to one decimal place -- lands on the
            # better side rather than nowhere.
            entries.sort(key=lambda band: -band.level)

        grid = {
            (
                cell.indicator_code,
                cell.variant,
                cell.small_denominator,
                cell.status_level,
                cell.change_level,
            ): cell.color
            for cell in session.exec(select(DashboardColorCell)).all()
        }
        if not bands or not grid:
            raise RuntimeError(
                "Dashboard reference data has not been seeded; run the "
                "dashboard importer or seed_dashboard_reference() first."
            )
        return cls(bands, grid)

    def _classify(
        self, indicator: str, variant: str, kind: str, value: Decimal | None
    ) -> Band | None:
        if value is None:
            return None
        for band in self._bands.get((indicator, variant, kind), ()):
            if band.contains(value):
                return band
        return None

    def status_band(
        self, indicator: str, variant: str, value: Decimal | None
    ) -> Band | None:
        return self._classify(indicator, variant, STATUS, value)

    def change_band(
        self,
        indicator: str,
        variant: str,
        value: Decimal | None,
        *,
        small_denominator: bool = False,
    ) -> Band | None:
        band = self._classify(indicator, variant, CHANGE, value)
        if band is None:
            return None
        if small_denominator and indicator in COLLAPSING_INDICATORS:
            level = _COLLAPSE.get(band.level)
            if level is not None:
                return next(
                    (
                        other
                        for other in self._bands[(indicator, variant, CHANGE)]
                        if other.level == level
                    ),
                    band,
                )
        return band

    def color(
        self,
        indicator: str,
        variant: str,
        status_level: int | None,
        change_level: int | None,
        *,
        small_denominator: bool = False,
    ) -> int | None:
        if status_level is None or change_level is None:
            return None
        return self._grid.get(
            (indicator, variant, small_denominator, status_level, change_level)
        )

    def judge(
        self,
        indicator: str,
        *,
        variant: str = DEFAULT_VARIANT,
        curr_status: Decimal | None,
        change: Decimal | None = None,
        prior_status: Decimal | None = None,
        small_denominator: bool = False,
    ) -> Judgement:
        """Classify one entity's figures the way the state would.

        ``change`` is used when given; otherwise it is the difference between
        the current and prior status, which is how the state defines it.
        """
        if change is None and curr_status is not None and prior_status is not None:
            change = curr_status - prior_status

        status = self.status_band(indicator, variant, curr_status)
        change_band = self.change_band(
            indicator, variant, change, small_denominator=small_denominator
        )
        return Judgement(
            status_level=status.level if status else None,
            change_level=change_band.level if change_band else None,
            color=self.color(
                indicator,
                variant,
                status.level if status else None,
                change_band.level if change_band else None,
                small_denominator=small_denominator,
            ),
            status_label=status.label if status else None,
            change_label=change_band.label if change_band else None,
        )


def variant_for(
    indicator: str,
    *,
    school_type: str | None = None,
    high_school_cutpoints: bool = False,
) -> str:
    """Which published table an entity is judged against.

    Suspension is published as six tables keyed by the file's ``type``
    column; the academic indicators as two, split by ``hscutpoints``.
    """
    if indicator == "SUSP":
        return (school_type or "").strip().upper() or DEFAULT_VARIANT
    if indicator in {"ELA", "MATH"} and high_school_cutpoints:
        return "HS"
    return DEFAULT_VARIANT


def is_small_denominator(indicator: str, denominator: int | None) -> bool:
    """Whether the reduced grid applies to an entity of this size."""
    if indicator not in SMALL_DENOMINATOR_INDICATORS or denominator is None:
        return False
    return denominator < SMALL_DENOMINATOR_THRESHOLD
