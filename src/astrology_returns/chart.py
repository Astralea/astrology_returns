"""Natal chart and return chart data structures."""

from __future__ import annotations

from dataclasses import dataclass, field

from .ephemeris import (
    GeoLocation,
    PLANETS,
    datetime_to_jd,
    get_all_planets,
    get_houses,
    get_planet_speed,
    jd_to_datetime,
)


@dataclass
class ChartData:
    """Represents a calculated chart (natal or return)."""

    jd: float
    year: int
    month: int
    day: int
    hour_ut: float
    location: GeoLocation
    planets: dict[str, float]
    speeds: dict[str, float]
    cusps: list[float]  # 12 house cusps
    asc: float
    mc: float
    house_system: str

    @property
    def datetime_str(self) -> str:
        h = int(self.hour_ut)
        m = int((self.hour_ut - h) * 60)
        s = int(((self.hour_ut - h) * 60 - m) * 60)
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d} {h:02d}:{m:02d}:{s:02d} UT"


def calculate_chart(
    year: int,
    month: int,
    day: int,
    hour_ut: float,
    location: GeoLocation,
    house_system: str = "placidus",
) -> ChartData:
    """Calculate a full chart for given time and location."""
    jd = datetime_to_jd(year, month, day, hour_ut)
    planets = get_all_planets(jd)
    cusps, angles = get_houses(jd, location, house_system)

    # Get speeds for each planet
    speeds = {}
    for name, pid in PLANETS.items():
        if name in planets:
            try:
                speeds[name] = get_planet_speed(jd, pid)
            except Exception:
                pass

    return ChartData(
        jd=jd,
        year=year,
        month=month,
        day=day,
        hour_ut=hour_ut,
        location=location,
        planets=planets,
        speeds=speeds,
        cusps=cusps,
        asc=angles[0],
        mc=angles[1],
        house_system=house_system,
    )


def calculate_chart_from_jd(
    jd: float,
    location: GeoLocation,
    house_system: str = "placidus",
) -> ChartData:
    """Calculate a full chart from a Julian Day and location."""
    year, month, day, hour_ut = jd_to_datetime(jd)
    return calculate_chart(year, month, day, hour_ut, location, house_system)
