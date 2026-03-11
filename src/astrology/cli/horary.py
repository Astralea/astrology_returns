"""Horary chart command."""

from __future__ import annotations

from datetime import datetime

import click

from .common import (
    parse_date, parse_time, location_options, house_system_option, ut_option,
    resolve_location, resolve_time,
)
from ..core.chart import calculate_chart
from ..core.timezone import get_timezone
from ..western.formatting import format_chart


@click.command()
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
