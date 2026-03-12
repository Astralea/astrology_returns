"""Forecast pipeline — combines profection, firdaria, solar return, and transits."""

from __future__ import annotations

import click

from .common import (
    parse_date, parse_time,
    location_options, house_system_option, ut_option,
    resolve_location, resolve_time,
)
from ..core.chart import calculate_chart
from ..core.ephemeris import PLANETS, datetime_to_jd, get_all_planets
from ..western.profections import annual_profection
from ..western.firdaria import calculate_firdaria
from ..western.returns import solar_return
from ..western.transits import find_transits
from ..western.formatting import (
    format_chart, format_transits, lon_to_sign, _find_house,
    ZODIAC_SIGNS,
)
from ..western.lots import calculate_lots
from ..western.sect import analyze_sect


def _format_profection_section(result, chart, use_unicode):
    """Format profection section for forecast."""
    sign_name = ZODIAC_SIGNS[result.sign_index]
    lord = result.lord_of_year
    lord_lon = chart.planets.get(lord)
    lord_house = _find_house(lord_lon, chart.cusps) if lord_lon is not None else None

    lines = []
    lines.append(f"  Age {result.age} → {result.house_label} house ({sign_name})")
    lines.append(f"  Topics: {result.topics}")
    lines.append(f"  Lord of the Year: {lord}", )
    if lord_lon is not None:
        lines.append(f"    Natal: {lon_to_sign(lord_lon, use_unicode)} (H{lord_house})")
    return "\n".join(lines)


def _format_firdaria_section(result, chart, use_unicode):
    """Format firdaria section for forecast."""
    by = chart.year
    cp = result.current_period
    lines = []
    lines.append(f"  {'Diurnal' if result.is_diurnal else 'Nocturnal'} chart")
    lines.append(f"  Major period: {cp.ruler} (ages {cp.start_age:.0f}–{cp.end_age:.0f})")

    ruler_lon = chart.planets.get(cp.ruler)
    if ruler_lon is not None:
        ruler_house = _find_house(ruler_lon, chart.cusps)
        lines.append(f"    Natal: {lon_to_sign(ruler_lon, use_unicode)} (H{ruler_house})")

    if result.current_sub:
        cs = result.current_sub
        lines.append(f"  Sub-period: {cs.ruler} (ages {cs.start_age:.1f}–{cs.end_age:.1f})")
        sub_lon = chart.planets.get(cs.ruler)
        if sub_lon is not None:
            sub_house = _find_house(sub_lon, chart.cusps)
            lines.append(f"    Natal: {lon_to_sign(sub_lon, use_unicode)} (H{sub_house})")
        lines.append(f"  → {cp.ruler}/{cs.ruler} period")
    else:
        lines.append(f"  → {cp.ruler} period")

    return "\n".join(lines)


@click.command()
@click.option("--natal-date", required=True, callback=parse_date, help="Birth date YYYY-MM-DD.")
@click.option("--natal-time", required=True, callback=parse_time, help="Birth time HH:MM[:SS] (local time, or UT with --ut).")
@click.option("--year", required=True, type=int, help="Year to forecast.")
@location_options
@house_system_option
@ut_option
@click.pass_context
def forecast(ctx, natal_date, natal_time, year, location, city, house_system, ut):
    """Yearly forecast: profection + firdaria + solar return + key transits."""
    loc = resolve_location(location, city)
    ny, nm, nd, natal_hour_ut, tz = resolve_time(natal_date, natal_time, loc, ut)
    use_unicode = ctx.obj["unicode"]
    include_outer = ctx.obj["modern"]

    # Natal chart
    natal_chart = calculate_chart(ny, nm, nd, natal_hour_ut, loc, house_system)
    if tz:
        natal_chart.tz = tz

    lines = []
    lines.append(f"{'=' * 60}")
    lines.append(f"  Forecast {year}")
    lines.append(f"{'=' * 60}")
    lines.append("")

    # === Natal summary ===
    lines.append(f"{'─' * 60}")
    lines.append("  ▸ Natal Chart")
    lines.append(f"{'─' * 60}")
    lines.append(format_chart(natal_chart, use_unicode=use_unicode, include_outer=include_outer))

    # === Profection ===
    prof = annual_profection(natal_date, year, natal_chart.cusps)
    lines.append(f"{'─' * 60}")
    lines.append("  ▸ Annual Profection")
    lines.append(f"{'─' * 60}")
    lines.append(_format_profection_section(prof, natal_chart, use_unicode))
    lines.append("")

    # === Firdaria ===
    sun_house = _find_house(natal_chart.planets.get("Sun", 0.0), natal_chart.cusps)
    is_diurnal = sun_house >= 7
    fird = calculate_firdaria(natal_date, year, is_diurnal)
    lines.append(f"{'─' * 60}")
    lines.append("  ▸ Firdaria")
    lines.append(f"{'─' * 60}")
    lines.append(_format_firdaria_section(fird, natal_chart, use_unicode))
    lines.append("")

    # === Solar Return ===
    sr_chart = solar_return(ny, nm, nd, natal_hour_ut, year, loc, house_system)
    if tz:
        sr_chart.tz = tz
    lines.append(f"{'─' * 60}")
    lines.append("  ▸ Solar Return")
    lines.append(f"{'─' * 60}")
    lines.append(format_chart(sr_chart, use_unicode=use_unicode, include_outer=include_outer))

    # === Key Transits ===
    # Track slow planets (Jupiter+) — inner planet transits are too frequent and slow to scan
    _SKIP_TRANSIT = {"Sun", "Moon", "Mercury", "Venus", "Mars", "North Node", "Chiron", "South Node"}
    transit_planets = ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    year_lord = prof.lord_of_year
    if year_lord not in transit_planets and year_lord in PLANETS and year_lord not in _SKIP_TRANSIT:
        transit_planets.append(year_lord)

    # Also add firdaria major ruler if different
    fird_ruler = fird.current_period.ruler
    if fird_ruler not in transit_planets and fird_ruler in PLANETS and fird_ruler not in _SKIP_TRANSIT:
        transit_planets.append(fird_ruler)

    natal_points = dict(natal_chart.planets)
    natal_points["ASC"] = natal_chart.asc
    natal_points["MC"] = natal_chart.mc

    jd_start = datetime_to_jd(year, 1, 1, 0.0)
    jd_end = datetime_to_jd(year + 1, 1, 1, 0.0)

    lines.append(f"{'─' * 60}")
    lines.append("  ▸ Key Transits")
    lines.append(f"{'─' * 60}")

    note_parts = ["Jupiter, Saturn, Uranus, Neptune, Pluto"]
    if year_lord in transit_planets and year_lord not in ("Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"):
        note_parts.append(f"{year_lord} (Year Lord)")
    if fird_ruler in transit_planets and fird_ruler not in ("Jupiter", "Saturn", "Uranus", "Neptune", "Pluto") and fird_ruler != year_lord:
        note_parts.append(f"{fird_ruler} (Firdaria ruler)")
    lines.append(f"  Tracking: {', '.join(note_parts)}")
    lines.append("")
    lines.append("  How to read: outer planet (slow, transiting) aspects your natal planet (fixed).")
    lines.append("  e.g. 'Uranus ☍ Moon' = transiting Uranus opposes your natal Moon position.")
    lines.append("")

    for planet in transit_planets:
        events = find_transits(natal_points, planet, jd_start, jd_end)
        lines.append(format_transits(events, title=f"{planet} Transits {year}", use_unicode=use_unicode))

    click.echo("\n".join(lines))
