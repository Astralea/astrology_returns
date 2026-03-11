"""Firdaria command."""

from __future__ import annotations

import click

from .common import (
    parse_date, parse_time,
    location_options, house_system_option, ut_option,
    resolve_location, resolve_time,
)
from ..core.chart import calculate_chart
from ..western.firdaria import calculate_firdaria, CYCLE_LENGTH
from ..western.formatting import lon_to_sign, _find_house


def _is_diurnal(chart) -> bool:
    """Check if Sun is above the horizon (above DSC-ASC axis).

    Diurnal = Sun is in houses 7-12 (above horizon).
    Simple check: Sun's longitude is between DSC and ASC going clockwise.
    """
    sun_lon = chart.planets.get("Sun", 0.0)
    sun_house = _find_house(sun_lon, chart.cusps)
    return sun_house >= 7


@click.command()
@click.option("--natal-date", required=True, callback=parse_date, help="Birth date YYYY-MM-DD.")
@click.option("--natal-time", required=True, callback=parse_time, help="Birth time HH:MM[:SS] (local time, or UT with --ut).")
@click.option("--year", required=True, type=int, help="Year to find active firdaria.")
@click.option("--full", is_flag=True, default=False, help="Show full 75-year firdaria table.")
@location_options
@house_system_option
@ut_option
@click.pass_context
def firdaria(ctx, natal_date, natal_time, year, full, location, city, house_system, ut):
    """Calculate firdaria — planetary period system (medieval time-lords)."""
    loc = resolve_location(location, city)
    ny, nm, nd, natal_hour_ut, tz = resolve_time(natal_date, natal_time, loc, ut)
    chart = calculate_chart(ny, nm, nd, natal_hour_ut, loc, house_system)

    diurnal = _is_diurnal(chart)
    result = calculate_firdaria(natal_date, year, diurnal)
    use_unicode = ctx.obj["unicode"]

    by, bm, bd = natal_date
    lines = []
    lines.append(f"{'=' * 60}")
    lines.append(f"  Firdaria {year}")
    lines.append(f"{'=' * 60}")
    lines.append(f"  Birth: {'Diurnal' if diurnal else 'Nocturnal'} chart")
    lines.append(f"  Age: {result.age:.0f}")
    lines.append("")

    # Current period
    cp = result.current_period
    period_start_year = by + int(cp.start_age)
    period_end_year = by + int(cp.end_age)
    lines.append(f"  Active Major Period: {cp.ruler}")
    lines.append(f"    Ages {cp.start_age:.0f}–{cp.end_age:.0f} ({period_start_year}–{period_end_year})")

    # Show ruler's natal position
    ruler_lon = chart.planets.get(cp.ruler)
    if ruler_lon is not None:
        ruler_house = _find_house(ruler_lon, chart.cusps)
        lines.append(f"    Natal: {lon_to_sign(ruler_lon, use_unicode)} (H{ruler_house})")
    lines.append("")

    # Current sub-period
    if result.current_sub:
        cs = result.current_sub
        sub_start_year = by + cs.start_age
        sub_end_year = by + cs.end_age
        lines.append(f"  Active Sub-Period: {cs.ruler}")
        lines.append(f"    Ages {cs.start_age:.1f}–{cs.end_age:.1f} ({sub_start_year:.1f}–{sub_end_year:.1f})")
        sub_lon = chart.planets.get(cs.ruler)
        if sub_lon is not None:
            sub_house = _find_house(sub_lon, chart.cusps)
            lines.append(f"    Natal: {lon_to_sign(sub_lon, use_unicode)} (H{sub_house})")
        lines.append("")
        lines.append(f"  → {cp.ruler}/{cs.ruler} period")
    else:
        lines.append(f"  → {cp.ruler} period (no sub-periods for nodes)")
    lines.append("")

    # Full table
    if full:
        lines.append(f"  {'─' * 56}")
        lines.append(f"  Full Firdaria Table ({int(CYCLE_LENGTH)}-year cycle):")
        lines.append(f"  {'─' * 56}")
        for period in result.all_periods:
            ps = by + int(period.start_age)
            pe = by + int(period.end_age)
            marker = "  ◄" if period is result.current_period else ""
            lines.append(f"  {period.ruler:<12} ages {period.start_age:>4.0f}–{period.end_age:<4.0f} ({ps}–{pe}){marker}")
            for sub in period.sub_periods:
                ss = by + sub.start_age
                se = by + sub.end_age
                sub_marker = "  ◄" if sub is result.current_sub else ""
                lines.append(f"      {sub.ruler:<10} {sub.start_age:>5.1f}–{sub.end_age:<5.1f} ({ss:.1f}–{se:.1f}){sub_marker}")
        lines.append("")

    click.echo("\n".join(lines))
