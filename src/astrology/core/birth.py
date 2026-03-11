"""Unified birth/natal data — the 'who' for all techniques."""

from __future__ import annotations

from dataclasses import dataclass
from zoneinfo import ZoneInfo

from .ephemeris import GeoLocation, datetime_to_jd, get_all_planets, get_planet_speed, PLANETS
from .timezone import get_timezone, local_to_ut


@dataclass
class BirthData:
    """All the information needed to identify a person's chart."""

    year: int
    month: int
    day: int
    hour_ut: float
    location: GeoLocation
    jd: float
    tz: ZoneInfo | None = None

    @classmethod
    def from_local_time(
        cls,
        year: int,
        month: int,
        day: int,
        hour_local: float,
        location: GeoLocation,
    ) -> BirthData:
        """Create from local time (auto-detects timezone from location)."""
        tz = get_timezone(location)
        uy, um, ud, hour_ut = local_to_ut(year, month, day, hour_local, tz)
        jd = datetime_to_jd(uy, um, ud, hour_ut)
        return cls(
            year=uy, month=um, day=ud,
            hour_ut=hour_ut, location=location,
            jd=jd, tz=tz,
        )

    @classmethod
    def from_ut(
        cls,
        year: int,
        month: int,
        day: int,
        hour_ut: float,
        location: GeoLocation,
    ) -> BirthData:
        """Create from UT time directly."""
        jd = datetime_to_jd(year, month, day, hour_ut)
        return cls(
            year=year, month=month, day=day,
            hour_ut=hour_ut, location=location,
            jd=jd, tz=None,
        )

    @property
    def natal_planets(self) -> dict[str, float]:
        """Get natal planet longitudes."""
        return get_all_planets(self.jd)
