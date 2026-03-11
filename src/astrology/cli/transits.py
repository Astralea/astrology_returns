"""Transit command."""

from __future__ import annotations

import click

from .common import (
    parse_date, parse_time, location_options, house_system_option, ut_option,
    resolve_location, resolve_time,
)
from ..core.ephemeris import PLANETS, datetime_to_jd, get_all_planets
from ..core.chart import calculate_chart
from ..western.transits import find_transits
from ..western.formatting import format_transits


TRANSIT_PLANET_NAMES = [
    name for name in PLANETS if name not in ("North Node", "Chiron")
]


@click.command()
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
        jd = datetime_to_jd(ny, nm, nd, natal_hour_ut)
        natal_points = get_all_planets(jd)

    if not transit_planets:
        transit_planets = ("Jupiter", "Saturn")

    jd_start = datetime_to_jd(year, 1, 1, 0.0)
    jd_end = datetime_to_jd(year + 1, 1, 1, 0.0)

    for planet in transit_planets:
        events = find_transits(natal_points, planet, jd_start, jd_end)
        title = f"{planet} Transits in {year}"
        click.echo(format_transits(events, title=title, use_unicode=ctx.obj["unicode"]))
