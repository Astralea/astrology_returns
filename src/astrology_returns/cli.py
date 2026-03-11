"""CLI for solar/lunar return and horary calculations."""

from __future__ import annotations

from datetime import datetime, timezone

import click

from .ephemeris import GeoLocation, HOUSE_SYSTEMS
from .ephemeris import PLANETS, datetime_to_jd
from .formatting import format_chart, format_transits
from .geo import geocode
from .returns import lunar_return, lunar_returns_in_year, solar_return
from .chart import calculate_chart
from .timezone import get_timezone, local_to_ut
from .transits import find_transits


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


def parse_time(ctx, param, value: str) -> float:
    """Parse time string like '14:30' to decimal hours."""
    try:
        parts = value.split(":")
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 else 0
        s = int(parts[2]) if len(parts) > 2 else 0
        return h + m / 60.0 + s / 3600.0
    except (ValueError, IndexError):
        raise click.BadParameter("Time must be 'HH:MM' or 'HH:MM:SS'")


def resolve_time(date_tuple, time_hour, loc, ut_flag):
    """Convert input time to UT components.

    If --ut is set, time is already UT. Otherwise, convert from local time
    using the timezone derived from location.

    Returns (year, month, day, hour_ut, tz) where tz is the ZoneInfo or None.
    """
    y, m, d = date_tuple
    if ut_flag:
        return y, m, d, time_hour, None
    tz = get_timezone(loc)
    uy, um, ud, hour_ut = local_to_ut(y, m, d, time_hour, tz)
    return uy, um, ud, hour_ut, tz


# Common options for location
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


@click.group()
@click.option(
    "--unicode/--no-unicode",
    default=False,
    help="Use unicode zodiac symbols.",
)
@click.option(
    "--modern/--traditional",
    default=False,
    help="Include outer planets (Uranus/Neptune/Pluto) in dignities & receptions. Default: traditional (exclude them).",
)
@click.pass_context
def cli(ctx, unicode, modern):
    """Astrology chart calculator — Solar/Lunar Returns & Horary."""
    ctx.ensure_object(dict)
    ctx.obj["unicode"] = unicode
    ctx.obj["modern"] = modern


@cli.command()
@click.option("--natal-date", required=True, callback=parse_date, help="Birth date YYYY-MM-DD.")
@click.option("--natal-time", required=True, callback=parse_time, help="Birth time HH:MM[:SS] (local time, or UT with --ut).")
@click.option("--year", required=True, type=int, help="Year for the solar return.")
@location_options
@house_system_option
@ut_option
@click.pass_context
def sr(ctx, natal_date, natal_time, year, location, city, house_system, ut):
    """Calculate a Solar Return chart."""
    loc = resolve_location(location, city)
    ny, nm, nd, natal_hour_ut, tz = resolve_time(natal_date, natal_time, loc, ut)
    chart = solar_return(ny, nm, nd, natal_hour_ut, year, loc, house_system)
    if tz:
        chart.tz = tz
    click.echo(format_chart(chart, title=f"Solar Return {year}", use_unicode=ctx.obj["unicode"], include_outer=ctx.obj["modern"]))


@cli.command()
@click.option("--natal-date", required=True, callback=parse_date, help="Birth date YYYY-MM-DD.")
@click.option("--natal-time", required=True, callback=parse_time, help="Birth time HH:MM[:SS] (local time, or UT with --ut).")
@click.option("--after", required=True, callback=parse_date, help="Find next lunar return after YYYY-MM-DD.")
@location_options
@house_system_option
@ut_option
@click.pass_context
def lr(ctx, natal_date, natal_time, after, location, city, house_system, ut):
    """Calculate the next Lunar Return chart."""
    loc = resolve_location(location, city)
    ny, nm, nd, natal_hour_ut, tz = resolve_time(natal_date, natal_time, loc, ut)
    ay, am, ad = after
    chart = lunar_return(ny, nm, nd, natal_hour_ut, ay, am, ad, loc, house_system)
    if tz:
        chart.tz = tz
    click.echo(format_chart(chart, title="Lunar Return", use_unicode=ctx.obj["unicode"], include_outer=ctx.obj["modern"]))


@cli.command()
@click.option("--natal-date", required=True, callback=parse_date, help="Birth date YYYY-MM-DD.")
@click.option("--natal-time", required=True, callback=parse_time, help="Birth time HH:MM[:SS] (local time, or UT with --ut).")
@click.option("--year", required=True, type=int, help="Year to list all lunar returns.")
@location_options
@house_system_option
@ut_option
@click.pass_context
def lr_year(ctx, natal_date, natal_time, year, location, city, house_system, ut):
    """List all Lunar Returns in a given year."""
    loc = resolve_location(location, city)
    ny, nm, nd, natal_hour_ut, tz = resolve_time(natal_date, natal_time, loc, ut)
    charts = lunar_returns_in_year(ny, nm, nd, natal_hour_ut, year, loc, house_system)
    for i, chart in enumerate(charts, 1):
        if tz:
            chart.tz = tz
        click.echo(format_chart(
            chart, title=f"Lunar Return #{i} of {year}", use_unicode=ctx.obj["unicode"], include_outer=ctx.obj["modern"],
        ))


@cli.command()
@click.option("--date", "date_val", required=True, callback=parse_date, help="Birth date YYYY-MM-DD.")
@click.option("--time", "time_val", required=True, callback=parse_time, help="Birth time HH:MM[:SS] (local time, or UT with --ut).")
@location_options
@house_system_option
@ut_option
@click.pass_context
def natal(ctx, date_val, time_val, location, city, house_system, ut):
    """Calculate a natal chart."""
    loc = resolve_location(location, city)
    y, m, d, hour_ut, tz = resolve_time(date_val, time_val, loc, ut)
    chart = calculate_chart(y, m, d, hour_ut, loc, house_system)
    if tz:
        chart.tz = tz
    click.echo(format_chart(chart, title="Natal Chart", use_unicode=ctx.obj["unicode"], include_outer=ctx.obj["modern"]))


@cli.command()
@click.option("--time", "time_val", default=None, callback=lambda c, p, v: parse_time(c, p, v) if v else None,
              help="Question time HH:MM[:SS] (local time, or UT with --ut). Defaults to now.")
@click.option("--date", "date_val", default=None, callback=lambda c, p, v: parse_date(c, p, v) if v else None,
              help="Question date YYYY-MM-DD. Defaults to today.")
@location_options
@house_system_option
@ut_option
@click.pass_context
def horary(ctx, time_val, date_val, location, city, house_system, ut):
    """Cast a horary chart (for the current or specified moment)."""
    loc = resolve_location(location, city)
    tz = get_timezone(loc)

    if date_val is None or time_val is None:
        # Default to current local time at the chart location
        now_local = datetime.now(tz)
        if date_val is None:
            date_val = (now_local.year, now_local.month, now_local.day)
        if time_val is None:
            time_val = now_local.hour + now_local.minute / 60.0 + now_local.second / 3600.0

    if ut:
        y, m, d = date_val
        hour_ut = time_val
        chart_tz = None
    else:
        y, m, d, hour_ut, chart_tz = resolve_time(date_val, time_val, loc, False)
        chart_tz = tz

    chart = calculate_chart(y, m, d, hour_ut, loc, house_system)
    if chart_tz:
        chart.tz = chart_tz
    click.echo(format_chart(chart, title="Horary Chart", use_unicode=ctx.obj["unicode"], include_outer=ctx.obj["modern"]))


TRANSIT_PLANET_NAMES = [
    name for name in PLANETS if name not in ("North Node", "Chiron")
]


@cli.command()
@click.option("--natal-date", required=True, callback=parse_date, help="Natal/chart date YYYY-MM-DD.")
@click.option("--natal-time", required=True, callback=parse_time, help="Natal/chart time HH:MM[:SS] (local time, or UT with --ut).")
@click.option("--planet", "transit_planets", multiple=True,
              type=click.Choice(TRANSIT_PLANET_NAMES, case_sensitive=False),
              help="Transiting planet(s). Repeat for multiple. Default: Jupiter & Saturn.")
@click.option("--year", required=True, type=int, help="Year to scan for transits.")
@click.option("--include-angles", is_flag=True, default=False,
              help="Include ASC/MC as natal points (requires --location or --city).")
@location_options
@house_system_option
@ut_option
@click.pass_context
def transit(ctx, natal_date, natal_time, transit_planets, year, include_angles, location, city, house_system, ut):
    """Find exact transit aspects to natal/chart positions in a given year."""
    # Build natal points
    if include_angles:
        loc = resolve_location(location, city)
        ny, nm, nd, natal_hour_ut, _ = resolve_time(natal_date, natal_time, loc, ut)
        chart = calculate_chart(ny, nm, nd, natal_hour_ut, loc, house_system)
        natal_points = dict(chart.planets)
        natal_points["ASC"] = chart.asc
        natal_points["MC"] = chart.mc
    else:
        if location or city:
            loc = resolve_location(location, city)
            ny, nm, nd, natal_hour_ut, _ = resolve_time(natal_date, natal_time, loc, ut)
        else:
            ny, nm, nd = natal_date
            natal_hour_ut = natal_time
        from .ephemeris import get_all_planets
        jd = datetime_to_jd(ny, nm, nd, natal_hour_ut)
        natal_points = get_all_planets(jd)

    # Default to Jupiter & Saturn if no planet specified
    if not transit_planets:
        transit_planets = ("Jupiter", "Saturn")

    jd_start = datetime_to_jd(year, 1, 1, 0.0)
    jd_end = datetime_to_jd(year + 1, 1, 1, 0.0)

    for planet in transit_planets:
        events = find_transits(natal_points, planet, jd_start, jd_end)
        title = f"{planet} Transits in {year}"
        click.echo(format_transits(events, title=title, use_unicode=ctx.obj["unicode"]))


@cli.command()
@click.argument("city_name")
def geo(city_name):
    """Look up coordinates for a city name."""
    loc, address = geocode(city_name)
    click.echo(f"  {address}")
    click.echo(f"  Latitude:  {loc.lat}")
    click.echo(f"  Longitude: {loc.lon}")
    click.echo(f"  For --location: {loc.lat},{loc.lon}")


def main():
    cli()
