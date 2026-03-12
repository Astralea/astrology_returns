"""Shared CLI options and parsers."""

from __future__ import annotations

import click

from ..core.ephemeris import GeoLocation, HOUSE_SYSTEMS
from ..core.geo import geocode
from ..core.birth import BirthData
from ..core.timezone import get_timezone, local_to_ut


def resolve_location(location: str | None, city: str | None) -> GeoLocation:
    """Resolve location from either --location or --city."""
    if city:
        loc, address = geocode(city)
        click.echo(f"  Resolved: {address}", err=True)
        click.echo(f"  Coords:   {loc}", err=True)
        click.echo("", err=True)
        return loc
    if location:
        return parse_location_str(location)
    raise click.UsageError("Provide either --location or --city.")


def parse_location_str(value: str) -> GeoLocation:
    """Parse location string like '39.9042,116.4074' (lat,lon)."""
    try:
        parts = value.split(",")
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        alt = float(parts[2].strip()) if len(parts) > 2 else 0.0
        return GeoLocation(lat, lon, alt)
    except (ValueError, IndexError):
        raise click.BadParameter(
            "Location must be 'lat,lon' or 'lat,lon,alt' (e.g. '39.9042,116.4074')"
        )


def parse_date(ctx, param, value: str) -> tuple[int, int, int]:
    """Parse date string like '1990-01-15'."""
    try:
        parts = value.split("-")
        return int(parts[0]), int(parts[1]), int(parts[2])
    except (ValueError, IndexError):
        raise click.BadParameter("Date must be 'YYYY-MM-DD'")


def parse_time(ctx, param, value: str | None) -> float | None:
    """Parse time string like '14:30' to decimal hours."""
    if value is None:
        return None
    try:
        parts = value.split(":")
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 0
        s = int(parts[2]) if len(parts) > 2 else 0
        return h + m / 60.0 + s / 3600.0
    except (ValueError, IndexError):
        raise click.BadParameter("Time must be 'HH:MM' or 'HH:MM:SS'")


def resolve_birth(date_tuple, time_hour, loc, ut_flag) -> BirthData:
    """Build a BirthData from CLI inputs."""
    y, m, d = date_tuple
    if ut_flag:
        return BirthData.from_ut(y, m, d, time_hour, loc)
    return BirthData.from_local_time(y, m, d, time_hour, loc)


def resolve_time(date_tuple, time_hour, loc, ut_flag):
    """Convert input time to UT components (legacy helper).

    Returns (year, month, day, hour_ut, tz).
    """
    y, m, d = date_tuple
    if ut_flag:
        return y, m, d, time_hour, None
    tz = get_timezone(loc)
    uy, um, ud, hour_ut = local_to_ut(y, m, d, time_hour, tz)
    return uy, um, ud, hour_ut, tz


# Reusable click option decorators

def location_options(f):
    f = click.option("--location", default=None, help="Coordinates as 'lat,lon'.")(f)
    f = click.option("--city", default=None, help="City name (geocoded via OpenStreetMap).")(f)
    return f


def house_system_option(f):
    return click.option(
        "--house-system",
        type=click.Choice(list(HOUSE_SYSTEMS.keys()), case_sensitive=False),
        default="placidus",
        help="House system.",
    )(f)


def ut_option(f):
    return click.option(
        "--ut", is_flag=True, default=False,
        help="Input time is in UT (default: local time, auto-detected from location).",
    )(f)


def natal_options(f):
    """Common options for commands that need natal/birth data."""
    f = click.option("--natal-date", required=True, callback=parse_date, help="Birth date YYYY-MM-DD.")(f)
    f = click.option("--natal-time", required=True, callback=parse_time, help="Birth time HH:MM[:SS] (local time, or UT with --ut).")(f)
    f = location_options(f)
    f = house_system_option(f)
    f = ut_option(f)
    return f
