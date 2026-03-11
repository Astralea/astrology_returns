"""Firdaria — medieval planetary period system.

Each life is divided into major periods ruled by planets in a fixed sequence
(different for diurnal vs nocturnal births). Each major period is subdivided
into 7 sub-periods cycling through the traditional planets.

Total cycle: 75 years, then repeats.
"""

from __future__ import annotations

from dataclasses import dataclass


# Major period lengths in years
PERIOD_YEARS = {
    "Sun": 10,
    "Venus": 8,
    "Mercury": 13,
    "Moon": 9,
    "Saturn": 11,
    "Jupiter": 12,
    "Mars": 7,
    "North Node": 3,
    "South Node": 2,
}

# Diurnal birth sequence
DIURNAL_ORDER = [
    "Sun", "Venus", "Mercury", "Moon",
    "Saturn", "Jupiter", "Mars",
    "North Node", "South Node",
]

# Nocturnal birth sequence
NOCTURNAL_ORDER = [
    "Moon", "Saturn", "Jupiter", "Mars",
    "North Node", "South Node",
    "Sun", "Venus", "Mercury",
]

# Traditional planets for sub-period rotation
_TRADITIONAL = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

CYCLE_LENGTH = sum(PERIOD_YEARS.values())  # 75 years


@dataclass
class SubPeriod:
    """A sub-period within a firdaria major period."""

    ruler: str
    start_age: float  # age in decimal years
    end_age: float

    @property
    def duration_years(self) -> float:
        return self.end_age - self.start_age


@dataclass
class FirdariaPeriod:
    """A major firdaria period."""

    ruler: str
    start_age: float
    end_age: float
    sub_periods: list[SubPeriod]

    @property
    def duration_years(self) -> float:
        return self.end_age - self.start_age


@dataclass
class FirdariaResult:
    """Current firdaria state for a person."""

    all_periods: list[FirdariaPeriod]
    current_period: FirdariaPeriod
    current_sub: SubPeriod | None
    age: float
    is_diurnal: bool


def _sub_period_order(major_ruler: str) -> list[str]:
    """Get sub-period planet order starting from the major ruler."""
    if major_ruler not in _TRADITIONAL:
        # Nodes don't have sub-periods
        return []
    idx = _TRADITIONAL.index(major_ruler)
    return _TRADITIONAL[idx:] + _TRADITIONAL[:idx]


def build_firdaria(is_diurnal: bool) -> list[FirdariaPeriod]:
    """Build the full 75-year firdaria sequence."""
    order = DIURNAL_ORDER if is_diurnal else NOCTURNAL_ORDER
    periods: list[FirdariaPeriod] = []
    age = 0.0

    for planet in order:
        years = PERIOD_YEARS[planet]
        sub_order = _sub_period_order(planet)

        subs: list[SubPeriod] = []
        if sub_order:
            sub_len = years / len(sub_order)
            sub_age = age
            for sub_planet in sub_order:
                subs.append(SubPeriod(
                    ruler=sub_planet,
                    start_age=sub_age,
                    end_age=sub_age + sub_len,
                ))
                sub_age += sub_len

        periods.append(FirdariaPeriod(
            ruler=planet,
            start_age=age,
            end_age=age + years,
            sub_periods=subs,
        ))
        age += years

    return periods


def calculate_firdaria(
    birth_date: tuple[int, int, int],
    target_year: int,
    is_diurnal: bool,
) -> FirdariaResult:
    """Calculate firdaria for a given year.

    Args:
        birth_date: (year, month, day).
        target_year: year to find the active period for.
        is_diurnal: True if Sun was above horizon at birth.

    Returns:
        FirdariaResult with the active major/sub period.
    """
    by, bm, bd = birth_date
    age = float(target_year - by)

    # Handle ages beyond 75 by cycling
    effective_age = age % CYCLE_LENGTH

    periods = build_firdaria(is_diurnal)

    current_period = periods[-1]  # fallback
    current_sub = None

    for period in periods:
        if period.start_age <= effective_age < period.end_age:
            current_period = period
            for sub in period.sub_periods:
                if sub.start_age <= effective_age < sub.end_age:
                    current_sub = sub
                    break
            break

    return FirdariaResult(
        all_periods=periods,
        current_period=current_period,
        current_sub=current_sub,
        age=age,
        is_diurnal=is_diurnal,
    )
