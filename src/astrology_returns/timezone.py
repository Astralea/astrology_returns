"""Timezone resolution from geographic coordinates."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from timezonefinder import TimezoneFinder

from .ephemeris import GeoLocation

_tf = TimezoneFinder()


def get_timezone(location: GeoLocation) -> ZoneInfo:
    """Get the IANA timezone for a geographic location."""
    tz_name = _tf.timezone_at(lat=location.lat, lng=location.lon)
    if tz_name is None:
        raise ValueError(f"Could not determine timezone for {location}")
    return ZoneInfo(tz_name)


def local_to_ut(
    year: int, month: int, day: int, hour: float, tz: ZoneInfo,
) -> tuple[int, int, int, float]:
    """Convert local time to UT, handling DST automatically.

    Returns (year, month, day, hour_ut).
    """
    h = int(hour)
    remainder = (hour - h) * 3600
    m = int(remainder // 60)
    s = int(remainder % 60)
    us = int((remainder - m * 60 - s) * 1_000_000)

    local_dt = datetime(year, month, day, h, m, s, us, tzinfo=tz)
    ut_dt = local_dt.astimezone(timezone.utc)

    hour_ut = ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0 + ut_dt.microsecond / 3_600_000_000.0
    return ut_dt.year, ut_dt.month, ut_dt.day, hour_ut


def ut_to_local(
    year: int, month: int, day: int, hour_ut: float, tz: ZoneInfo,
) -> datetime:
    """Convert UT to local datetime."""
    h = int(hour_ut)
    remainder = (hour_ut - h) * 3600
    m = int(remainder // 60)
    s = int(remainder % 60)
    us = int((remainder - m * 60 - s) * 1_000_000)

    ut_dt = datetime(year, month, day, h, m, s, us, tzinfo=timezone.utc)
    return ut_dt.astimezone(tz)


def format_local_time(dt: datetime) -> str:
    """Format a timezone-aware datetime for display."""
    offset = dt.utcoffset()
    if offset is None:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    total_seconds = int(offset.total_seconds())
    sign = "+" if total_seconds >= 0 else "-"
    abs_seconds = abs(total_seconds)
    oh, om = divmod(abs_seconds // 60, 60)
    tz_name = dt.tzinfo.key if hasattr(dt.tzinfo, "key") else ""
    return f"{dt.strftime('%Y-%m-%d %H:%M:%S')} {sign}{oh:02d}:{om:02d} ({tz_name})"
