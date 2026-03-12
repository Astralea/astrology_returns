"""Transit calculations — find when transiting planets aspect natal/chart positions."""

from __future__ import annotations

from dataclasses import dataclass

from .aspects import ASPECTS
from ..core.ephemeris import (
    PLANETS,
    find_exact_return,
    get_planet_lon,
    get_planet_speed,
    jd_to_datetime,
)


@dataclass
class TransitEvent:
    """A single exact transit aspect event."""

    jd: float
    transit_planet: str
    natal_planet: str
    aspect_name: str
    aspect_symbol: str
    natal_lon: float
    transit_lon: float
    is_retrograde: bool = False

    @property
    def datetime_str(self) -> str:
        y, m, d, h = jd_to_datetime(self.jd)
        hh = int(h)
        mm = int((h - hh) * 60)
        ss = int(((h - hh) * 60 - mm) * 60)
        return f"{y:04d}-{m:02d}-{d:02d} {hh:02d}:{mm:02d}:{ss:02d} UT"

    @property
    def motion_flag(self) -> str:
        return "R" if self.is_retrograde else "D"


def _aspect_target_lons(natal_lon: float, aspect_angle: int) -> list[float]:
    """Get target longitudes for a transit planet to make the given aspect."""
    if aspect_angle == 0:
        return [natal_lon]
    if aspect_angle == 180:
        return [(natal_lon + 180) % 360]
    # Sextile, square, trine each have two target degrees
    return [
        (natal_lon + aspect_angle) % 360,
        (natal_lon - aspect_angle) % 360,
    ]


def find_transits(
    natal_points: dict[str, float],
    transit_planet: str,
    jd_start: float,
    jd_end: float,
    aspects: dict[str, tuple[int, str]] | None = None,
) -> list[TransitEvent]:
    """
    Find all exact transit aspects from a transiting planet to natal positions.

    Args:
        natal_points: dict of point name -> longitude (planets, ASC, MC, etc.)
        transit_planet: name of the transiting planet (must be a key in PLANETS)
        jd_start: start of search window (Julian Day)
        jd_end: end of search window (Julian Day)
        aspects: aspect definitions; defaults to major Ptolemaic aspects

    Returns:
        List of TransitEvent sorted chronologically.
    """
    if aspects is None:
        aspects = ASPECTS

    planet_id = PLANETS[transit_planet]
    events: list[TransitEvent] = []

    for natal_name, natal_lon in natal_points.items():
        for asp_name, (angle, symbol) in aspects.items():
            targets = _aspect_target_lons(natal_lon, angle)

            for target_lon in targets:
                _scan_crossings(
                    events,
                    planet_id,
                    transit_planet,
                    natal_name,
                    natal_lon,
                    target_lon,
                    asp_name,
                    symbol,
                    jd_start,
                    jd_end,
                )

    events.sort(key=lambda e: e.jd)
    return events


def _scan_crossings(
    events: list[TransitEvent],
    planet_id: int,
    transit_planet: str,
    natal_name: str,
    natal_lon: float,
    target_lon: float,
    asp_name: str,
    symbol: str,
    jd_start: float,
    jd_end: float,
) -> None:
    """Find all crossings of target_lon by the transit planet in [jd_start, jd_end]."""
    search_jd = jd_start

    while search_jd < jd_end:
        try:
            hit_jd = find_exact_return(search_jd, target_lon, planet_id, jd_max=jd_end)
        except Exception:
            break

        if hit_jd >= jd_end:
            break

        # Verify the hit is actually close to target
        actual_lon = get_planet_lon(hit_jd, planet_id)
        diff = abs(actual_lon - target_lon)
        if diff > 180:
            diff = 360 - diff

        if diff < 0.01:
            speed_at_hit = get_planet_speed(hit_jd, planet_id)
            events.append(TransitEvent(
                jd=hit_jd,
                transit_planet=transit_planet,
                natal_planet=natal_name,
                aspect_name=asp_name,
                aspect_symbol=symbol,
                natal_lon=natal_lon,
                transit_lon=actual_lon,
                is_retrograde=speed_at_hit < 0,
            ))

        # Jump forward — enough to avoid re-finding the same crossing,
        # small enough to catch retrograde re-crossings.
        # Near stations (very slow speed), use smaller jumps.
        speed = abs(get_planet_speed(hit_jd, planet_id))
        if speed > 5:
            jump = 10.0    # Moon
        elif speed > 0.5:
            jump = 15.0    # Sun, Mercury, Venus, Mars
        elif speed > 0.05:
            jump = 10.0    # outer planets, normal motion
        else:
            jump = 5.0     # outer planets near station — jump less to catch re-crossings
        search_jd = hit_jd + jump
