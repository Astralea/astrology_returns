"""Swiss Ephemeris wrapper for planetary calculations."""

from __future__ import annotations

import swisseph as swe
from dataclasses import dataclass

# House system codes for swisseph
HOUSE_SYSTEMS = {
    "placidus": b"P",
    "koch": b"K",
    "whole_sign": b"W",
    "equal": b"E",
    "campanus": b"C",
    "regiomontanus": b"R",
    "porphyry": b"O",
    "morinus": b"M",
}

# Planet IDs
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
    "North Node": swe.MEAN_NODE,
    "Chiron": swe.CHIRON,
}


@dataclass
class GeoLocation:
    """Geographic location with latitude, longitude, and optional altitude."""

    lat: float  # positive = North
    lon: float  # positive = East
    alt: float = 0.0

    def __str__(self) -> str:
        ns = "N" if self.lat >= 0 else "S"
        ew = "E" if self.lon >= 0 else "W"
        return f"{abs(self.lat):.4f}°{ns} {abs(self.lon):.4f}°{ew}"


def datetime_to_jd(year: int, month: int, day: int, hour: float = 0.0) -> float:
    """Convert date/time to Julian Day number. Hour is in UT (decimal hours)."""
    return swe.julday(year, month, day, hour)


def jd_to_datetime(jd: float) -> tuple[int, int, int, float]:
    """Convert Julian Day to (year, month, day, hour_ut)."""
    year, month, day, hour = swe.revjul(jd)
    return int(year), int(month), int(day), float(hour)


def get_planet_lon(jd: float, planet_id: int) -> float:
    """Get ecliptic longitude of a planet at a given Julian Day."""
    flags = swe.FLG_MOSEPH | swe.FLG_SPEED
    result, _ = swe.calc_ut(jd, planet_id, flags)
    return result[0]  # longitude in degrees


def get_planet_speed(jd: float, planet_id: int) -> float:
    """Get the speed of a planet (degrees/day) at a given Julian Day."""
    flags = swe.FLG_MOSEPH | swe.FLG_SPEED
    result, _ = swe.calc_ut(jd, planet_id, flags)
    return result[3]  # speed in longitude


def get_all_planets(jd: float) -> dict[str, float]:
    """Get longitudes of all planets at a given Julian Day."""
    result = {}
    for name, pid in PLANETS.items():
        try:
            result[name] = get_planet_lon(jd, pid)
        except Exception:
            pass  # skip planets without ephemeris data (e.g. Chiron)
    return result


def get_houses(
    jd: float, location: GeoLocation, system: str = "placidus"
) -> tuple[list[float], list[float]]:
    """
    Calculate house cusps and angles.

    Returns:
        (cusps, angles) where:
        - cusps is a list of 12 house cusp longitudes (1-indexed in astrology, 0-indexed here)
        - angles is [ASC, MC, ARMC, Vertex, Equatorial ASC, ...]
    """
    hsys = HOUSE_SYSTEMS.get(system, b"P")
    cusps, angles = swe.houses(jd, location.lat, location.lon, hsys)
    return list(cusps), list(angles)


def find_exact_return(
    jd_start: float,
    target_lon: float,
    planet_id: int,
    max_iter: int = 100,
    precision: float = 1e-8,
    jd_max: float = 0.0,
) -> float:
    """
    Find the next exact Julian Day (>= jd_start) when a planet reaches target longitude.

    Two-phase approach:
    1. Coarse scan forward to find a bracket where the planet crosses the target.
    2. Newton's method refinement within that bracket.

    Args:
        jd_start: Starting Julian Day for the search (searches forward from here).
        target_lon: Target ecliptic longitude in degrees.
        planet_id: Swiss Ephemeris planet ID.
        max_iter: Maximum Newton iterations.
        precision: Required precision in degrees.
        jd_max: If > 0, stop scanning beyond this Julian Day (returns jd_max + 1 if not found).

    Returns:
        Julian Day of the exact return, or jd_max + 1 if not found within window.
    """
    # Determine scan step based on planet's typical speed
    # Moon: ~13°/day -> step ~2 days; Sun: ~1°/day -> step ~10 days
    speed = abs(get_planet_speed(jd_start, planet_id))
    if speed > 5:
        step = 1.0  # fast movers (Moon)
    elif speed > 0.5:
        step = 5.0  # Sun, Mercury, Venus
    else:
        step = 15.0  # slow movers

    # Phase 1: Coarse scan to find bracket where planet crosses target
    def signed_diff(lon1: float, lon2: float) -> float:
        d = lon1 - lon2
        if d > 180:
            d -= 360
        elif d < -180:
            d += 360
        return d

    jd = jd_start
    prev_diff = signed_diff(get_planet_lon(jd, planet_id), target_lon)

    for _ in range(1000):
        jd_next = jd + step
        # Early exit if we've passed the search window
        if jd_max > 0 and jd_next > jd_max:
            return jd_max + 1
        curr_diff = signed_diff(get_planet_lon(jd_next, planet_id), target_lon)

        # Detect zero crossing (sign change) and the planet is moving forward through target
        if prev_diff * curr_diff <= 0 and abs(prev_diff - curr_diff) < 180:
            # Found bracket [jd, jd_next], refine with Newton from midpoint
            jd_refine = jd + step * abs(prev_diff) / (abs(prev_diff) + abs(curr_diff))
            break

        jd = jd_next
        prev_diff = curr_diff
    else:
        # Fallback: just use jd_start
        jd_refine = jd_start

    # Phase 2: Newton's method refinement
    jd = jd_refine
    for _ in range(max_iter):
        current_lon = get_planet_lon(jd, planet_id)
        spd = get_planet_speed(jd, planet_id)

        diff = target_lon - current_lon
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360

        if abs(diff) < precision:
            return jd

        if abs(spd) > 1e-10:
            jd += diff / spd
        else:
            jd += 0.1

    return jd
