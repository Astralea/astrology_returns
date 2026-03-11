"""Solar and Lunar return commands."""

from __future__ import annotations

import click

from .common import (
    parse_date, parse_time,
    location_options, house_system_option, ut_option,
    resolve_location, resolve_time,
)
from ..western.returns import solar_return, lunar_return, lunar_returns_in_year
from ..western.formatting import format_chart


@click.command()
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


@click.command()
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


@click.command()
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
