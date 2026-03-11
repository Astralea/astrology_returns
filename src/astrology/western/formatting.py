"""Output formatting for chart data — designed for easy copy-paste."""

from __future__ import annotations

from .aspects import calculate_aspects, is_moon_void_of_course
from ..core.chart import ChartData
from .lots import calculate_lots
from .sect import analyze_sect
from .dignities import (
    find_receptions,
    get_dignities_for_planet,
    get_domicile_ruler,
    get_exaltation_ruler,
    get_face_ruler,
    get_sign,
    get_term_ruler,
    get_triplicity_rulers,
)

ZODIAC_SIGNS = [
    "Ari", "Tau", "Gem", "Can", "Leo", "Vir",
    "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis",
]

ZODIAC_UNICODE = [
    "♈", "♉", "♊", "♋", "♌", "♍",
    "♎", "♏", "♐", "♑", "♒", "♓",
]


def lon_to_sign(lon: float, use_unicode: bool = False) -> str:
    """Convert ecliptic longitude to sign + degree format."""
    sign_idx = int(lon // 30)
    degree = lon % 30
    deg = int(degree)
    minute = int((degree - deg) * 60)
    second = int(((degree - deg) * 60 - minute) * 60)
    signs = ZODIAC_UNICODE if use_unicode else ZODIAC_SIGNS
    return f"{deg:02d}{signs[sign_idx]}{minute:02d}'{second:02d}\""


def _dignity_flags(planet_name: str, lon: float) -> str:
    """Short dignity/debility flags for a planet."""
    d = get_dignities_for_planet(planet_name, lon)
    flags = []
    if "domicile" in d:
        flags.append("Dom")
    if "exaltation" in d:
        flags.append("Exl")
    if "triplicity" in d:
        flags.append("Tri")
    if "detriment" in d:
        flags.append("Det")
    if "fall" in d:
        flags.append("Fall")
    if "term" in d:
        flags.append("Trm")
    if "face" in d:
        flags.append("Fac")
    return " ".join(flags)


def _find_house(lon: float, cusps: list[float]) -> int:
    """Determine which house (1-12) a planet falls in."""
    for i in range(12):
        cusp_start = cusps[i]
        cusp_end = cusps[(i + 1) % 12]
        if cusp_start <= cusp_end:
            if cusp_start <= lon < cusp_end:
                return i + 1
        else:
            # Wraps around 0° Aries
            if lon >= cusp_start or lon < cusp_end:
                return i + 1
    return 12  # fallback


def _retrograde_flag(planet_name: str, speeds: dict[str, float]) -> str:
    spd = speeds.get(planet_name, 0.0)
    if spd < 0:
        return " R"
    return ""


OUTER_PLANETS = {"Uranus", "Neptune", "Pluto"}


def format_chart(chart: ChartData, title: str = "", use_unicode: bool = False, include_outer: bool = False) -> str:
    """Format a chart for display with aspects, dignities, and receptions."""
    lines: list[str] = []

    if title:
        lines.append(f"{'=' * 60}")
        lines.append(f"  {title}")
        lines.append(f"{'=' * 60}")

    local_str = chart.local_datetime_str
    if local_str:
        lines.append(f"  Time: {local_str}")
        lines.append(f"        {chart.datetime_str}")
    else:
        lines.append(f"  Time: {chart.datetime_str}")
    lines.append(f"  Location: {chart.location}")
    lines.append(f"  House System: {chart.house_system.title()}")
    lines.append("")

    # Angles
    lines.append("  Angles:")
    lines.append(f"    ASC  {lon_to_sign(chart.asc, use_unicode)}")
    lines.append(f"    MC   {lon_to_sign(chart.mc, use_unicode)}")
    lines.append("")

    # Sect
    sun_house = _find_house(chart.planets.get("Sun", 0.0), chart.cusps)
    is_diurnal = sun_house >= 7
    sect = analyze_sect(chart.planets, chart.cusps, is_diurnal)
    lines.append(f"  Sect: {'Diurnal' if is_diurnal else 'Nocturnal'}")
    lines.append(f"    Benefic of sect:      {sect.benefic_of_sect:<10} (helper)")
    lines.append(f"    Malefic of sect:      {sect.malefic_of_sect:<10} (challenge, manageable)")
    lines.append(f"    Benefic contra sect:  {sect.benefic_contrary:<10} (less effective)")
    lines.append(f"    Malefic contra sect:  {sect.malefic_contrary:<10} (most difficult)")
    lines.append("")

    # Lots (Fortune & Spirit)
    lots = calculate_lots(chart.asc, chart.planets, is_diurnal)
    lines.append("  Lots:")
    for lot in lots:
        lot_house = _find_house(lot.longitude, chart.cusps)
        lot_ruler = get_domicile_ruler(lot.longitude)
        ruler_lon = chart.planets.get(lot_ruler)
        ruler_house = _find_house(ruler_lon, chart.cusps) if ruler_lon is not None else None
        ruler_info = f"ruler {lot_ruler} (H{ruler_house})" if ruler_house else f"ruler {lot_ruler}"
        lines.append(
            f"    {lot.name:<10} {lon_to_sign(lot.longitude, use_unicode)}"
            f"  H{lot_house:<2} {ruler_info}  — {lot.description}"
        )
    lines.append("")

    # Moon Void of Course
    voc, deg_remaining = is_moon_void_of_course(chart.planets, chart.speeds)
    if voc:
        lines.append(f"  ⚠ Moon Void of Course ({deg_remaining:.1f}° remaining in sign)")
        lines.append("")

    # Planets with dignities and house placement
    lines.append("  Planets:")
    max_name_len = max(len(name) for name in chart.planets)
    for name, lon in chart.planets.items():
        retro = _retrograde_flag(name, chart.speeds)
        show_dignity = include_outer or name not in OUTER_PLANETS
        dflags = _dignity_flags(name, lon) if show_dignity else ""
        dstr = f"  [{dflags}]" if dflags else ""
        house = _find_house(lon, chart.cusps)
        lines.append(
            f"    {name:<{max_name_len}}  {lon_to_sign(lon, use_unicode)}{retro}"
            f"  ({lon:>8.4f}°)  H{house:<2}{dstr}"
        )
    lines.append("")

    # Houses
    lines.append("  Houses:")
    for i, cusp in enumerate(chart.cusps):
        lines.append(f"    House {i + 1:>2}  {lon_to_sign(cusp, use_unicode)}  ({cusp:>8.4f}°)")
    lines.append("")

    # Essential Dignities Table (now with triplicity)
    # Exclude outer planets from table unless --modern
    dignity_planets = {
        name: lon for name, lon in chart.planets.items()
        if name != "North Node" and (include_outer or name not in OUTER_PLANETS)
    }
    lines.append("  Essential Dignities Table:")
    lines.append(f"    {'Planet':<12} {'Sign':<5} {'Domicile':<10} {'Exalt':<10} {'Trip':<10} {'Term':<10} {'Face':<10}")
    lines.append(f"    {'-' * 67}")
    for name, lon in dignity_planets.items():
        sign_idx = get_sign(lon)
        sign_name = ZODIAC_SIGNS[sign_idx]
        dom = get_domicile_ruler(lon)
        exl = get_exaltation_ruler(lon) or "—"
        day_r, night_r = get_triplicity_rulers(lon)
        tri = day_r if day_r == night_r else f"{day_r}/{night_r}"
        trm = get_term_ruler(lon)
        fac = get_face_ruler(lon)
        lines.append(f"    {name:<12} {sign_name:<5} {dom:<10} {exl:<10} {tri:<10} {trm:<10} {fac:<10}")
    lines.append("")

    # Aspects (always show all planets including outer)
    aspects = calculate_aspects(chart.planets, chart.speeds)
    if aspects:
        lines.append("  Aspects:")
        for asp in aspects:
            app_sep = "a" if asp.applying else "s"
            lines.append(
                f"    {asp.planet_a:<12} {asp.symbol} {asp.planet_b:<12}"
                f"  {asp.aspect_name:<12} orb {asp.orb:>5.2f}° ({app_sep})"
            )
        lines.append("")

    # Build aspect pairs set for reception analysis
    aspect_pairs: set[tuple[str, str]] = set()
    for asp in aspects:
        aspect_pairs.add((asp.planet_a, asp.planet_b))

    # Receptions — filter outer planets unless --modern
    reception_planets = {
        name: lon for name, lon in chart.planets.items()
        if include_outer or name not in OUTER_PLANETS
    }
    receptions = find_receptions(reception_planets, aspect_pairs)
    if receptions:
        lines.append("  Receptions:")
        for rec in receptions:
            asp_mark = " ★" if rec.has_aspect else ""
            if rec.rtype.startswith("mutual"):
                label = {
                    "mutual_domicile": "mutual domicile",
                    "mutual_exalt":    "mutual exaltation",
                    "mutual_mixed":    "mutual mixed",
                    "mutual_minor":    "mutual minor",
                }.get(rec.rtype, rec.rtype)
                lines.append(
                    f"    {rec.planet_a:<10} ⟷ {rec.planet_b:<10}"
                    f"  {label} (score {rec.strength}){asp_mark}"
                )
            else:
                lines.append(
                    f"    {rec.detail}  (score {rec.strength}){asp_mark}"
                )

        lines.append("")
        lines.append("    ★ = has aspect (reception is operative)")
        lines.append("")

    return "\n".join(lines)


def format_transits(
    events: list,
    title: str = "Transits",
    use_unicode: bool = False,
) -> str:
    """Format a list of TransitEvent for display."""
    from .transits import TransitEvent

    lines: list[str] = []
    lines.append(f"{'=' * 60}")
    lines.append(f"  {title}")
    lines.append(f"{'=' * 60}")
    lines.append("")

    if not events:
        lines.append("  No transits found.")
        lines.append("")
        return "\n".join(lines)

    lines.append(
        f"  {'Date/Time':<22} {'Transit':<10} {'Asp':^3} {'Natal':<12} {'Transit°'}"
    )
    lines.append(f"  {'-' * 56}")

    for ev in events:
        lines.append(
            f"  {ev.datetime_str:<22} {ev.transit_planet:<10} "
            f"{ev.aspect_symbol:^3} {ev.natal_planet:<12} "
            f"{lon_to_sign(ev.transit_lon, use_unicode)}"
        )

    lines.append("")
    lines.append(f"  Total: {len(events)} transit events")
    lines.append("")
    return "\n".join(lines)
