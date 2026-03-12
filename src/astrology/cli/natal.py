"""Natal chart command."""

from __future__ import annotations

import click

from .common import (
    parse_date, parse_time, location_options, house_system_option, ut_option,
    resolve_location, resolve_time,
)
from ..core.chart import calculate_chart
from ..western.formatting import format_chart


@click.command()
@click.option("--date", "date_val", required=True, callback=parse_date, help="Birth date YYYY-MM-DD.")
@click.option("--time", "time_val", default=None, callback=parse_time, help="Birth time HH:MM[:SS]. If omitted, uses noon (houses/ASC unreliable).")
@location_options
@house_system_option
@ut_option
@click.pass_context
def natal(ctx, date_val, time_val, location, city, house_system, ut):
    """Calculate a natal chart."""
    loc = resolve_location(location, city)
    approximate = time_val is None
    if approximate:
        time_val = 12.0  # noon local time
    y, m, d, hour_ut, tz = resolve_time(date_val, time_val, loc, ut)
    chart = calculate_chart(y, m, d, hour_ut, loc, house_system)
    chart.approximate_time = approximate
    if tz:
        chart.tz = tz
    click.echo(format_chart(chart, title="Natal Chart", use_unicode=ctx.obj["unicode"], include_outer=ctx.obj["modern"]))
