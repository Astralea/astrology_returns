"""Annual profection command."""

from __future__ import annotations

import click

from .common import (
    parse_date, parse_time,
    location_options, house_system_option, ut_option,
    resolve_location, resolve_time,
)
from ..core.chart import calculate_chart
from ..western.profections import annual_profection, HOUSE_TOPICS
from ..western.formatting import lon_to_sign, ZODIAC_SIGNS, _find_house


@click.command()
@click.option("--natal-date", required=True, callback=parse_date, help="Birth date YYYY-MM-DD.")
@click.option("--natal-time", required=True, callback=parse_time, help="Birth time HH:MM[:SS] (local time, or UT with --ut).")
@click.option("--year", required=True, type=int, help="Year to calculate profection for.")
@location_options
@house_system_option
@ut_option
@click.pass_context
def profection(ctx, natal_date, natal_time, year, location, city, house_system, ut):
    """Calculate annual profection — which house and planet rule the year."""
    loc = resolve_location(location, city)
    ny, nm, nd, natal_hour_ut, tz = resolve_time(natal_date, natal_time, loc, ut)
    chart = calculate_chart(ny, nm, nd, natal_hour_ut, loc, house_system)

    result = annual_profection(natal_date, year, chart.cusps)

    use_unicode = ctx.obj["unicode"]
    sign_name = ZODIAC_SIGNS[result.sign_index]

    # Find where the lord of the year is in the natal chart
    lord = result.lord_of_year
    lord_lon = chart.planets.get(lord)
    lord_house = _find_house(lord_lon, chart.cusps) if lord_lon is not None else None

    lines = []
    lines.append(f"{'=' * 60}")
    lines.append(f"  Annual Profection {year}")
    lines.append(f"{'=' * 60}")
    lines.append(f"  Age: {result.age}")
    lines.append(f"  Profected House: {result.house_label} house ({sign_name})")
    lines.append(f"  Topics: {result.topics}")
    lines.append("")
    lines.append(f"  Lord of the Year: {lord}")
    if lord_lon is not None:
        lines.append(f"    Natal position: {lon_to_sign(lord_lon, use_unicode)} (H{lord_house})")
    lines.append("")
    lines.append("  Watch for:")
    lines.append(f"    - Transits to/from {lord}")
    lines.append(f"    - {lord}'s condition in Solar Return")
    lines.append(f"    - {lord}'s placement in Lunar Returns")
    lines.append("")

    click.echo("\n".join(lines))
