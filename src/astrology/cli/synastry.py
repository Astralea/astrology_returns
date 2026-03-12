"""Synastry (compatibility) chart CLI command."""

from __future__ import annotations

import click

from .common import (
    parse_date, parse_time,
    location_options, house_system_option, ut_option,
    resolve_location, resolve_time,
)
from ..core.chart import calculate_chart
from ..western.synastry import calculate_synastry
from ..western.formatting import (
    format_chart, format_synastry, lon_to_sign, _find_house,
)


@click.command()
@click.option("--date-a", required=True, callback=parse_date, help="Person A birth date YYYY-MM-DD.")
@click.option("--time-a", required=True, callback=parse_time, help="Person A birth time HH:MM[:SS].")
@click.option("--date-b", required=True, callback=parse_date, help="Person B birth date YYYY-MM-DD.")
@click.option("--time-b", required=True, callback=parse_time, help="Person B birth time HH:MM[:SS].")
@click.option("--name-a", default="Person A", help="Name for person A.")
@click.option("--name-b", default="Person B", help="Name for person B.")
@location_options
@house_system_option
@ut_option
@click.option("--location-b", default=None, help="Person B coordinates as 'lat,lon' (default: same as A).")
@click.option("--city-b", default=None, help="Person B city (default: same as A).")
@click.pass_context
def synastry(ctx, date_a, time_a, date_b, time_b, name_a, name_b,
             location, city, house_system, ut, location_b, city_b):
    """Synastry: compare two natal charts and show inter-chart aspects."""
    loc_a = resolve_location(location, city)
    ya, ma, da, hour_a, tz_a = resolve_time(date_a, time_a, loc_a, ut)

    if city_b or location_b:
        loc_b = resolve_location(location_b, city_b)
    else:
        loc_b = loc_a
    yb, mb, db, hour_b, tz_b = resolve_time(date_b, time_b, loc_b, ut)

    use_unicode = ctx.obj["unicode"]
    include_outer = ctx.obj["modern"]

    chart_a = calculate_chart(ya, ma, da, hour_a, loc_a, house_system)
    if tz_a:
        chart_a.tz = tz_a
    chart_b = calculate_chart(yb, mb, db, hour_b, loc_b, house_system)
    if tz_b:
        chart_b.tz = tz_b

    lines = []

    # Chart A
    lines.append(f"{'─' * 60}")
    lines.append(f"  ▸ {name_a} — Natal Chart")
    lines.append(f"{'─' * 60}")
    lines.append(format_chart(chart_a, use_unicode=use_unicode, include_outer=include_outer))

    # Chart B
    lines.append(f"{'─' * 60}")
    lines.append(f"  ▸ {name_b} — Natal Chart")
    lines.append(f"{'─' * 60}")
    lines.append(format_chart(chart_b, use_unicode=use_unicode, include_outer=include_outer))

    # Synastry aspects
    # Include angles in synastry
    points_a = dict(chart_a.planets)
    points_a["ASC"] = chart_a.asc
    points_a["MC"] = chart_a.mc
    points_b = dict(chart_b.planets)
    points_b["ASC"] = chart_b.asc
    points_b["MC"] = chart_b.mc

    aspects = calculate_synastry(points_a, points_b)

    lines.append(f"{'─' * 60}")
    lines.append(f"  ▸ Synastry Aspects")
    lines.append(f"{'─' * 60}")
    lines.append(format_synastry(aspects, name_a=name_a, name_b=name_b, use_unicode=use_unicode))

    click.echo("\n".join(lines))
