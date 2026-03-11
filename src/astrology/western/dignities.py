"""Essential dignities, receptions, and mutual reception tables.

Based on traditional rules (Lilly, Bonatti):
- Mutual reception: two planets each in the other's dignity (domicile, exaltation, or mixed).
- One-way reception: planet A is in a sign/degree where planet B has dignity; B "receives" A.
- Reception is most operative when there is an aspect between the two planets.
- Minor dignities (triplicity, term, face) alone are insufficient for reception;
  Bonatti requires at least two minor dignities combined.
"""

from __future__ import annotations

from dataclasses import dataclass

# Signs indexed 0-11: Ari, Tau, Gem, Can, Leo, Vir, Lib, Sco, Sag, Cap, Aqu, Pis

# Domicile rulers (入庙)
DOMICILE = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon",
    4: "Sun", 5: "Mercury", 6: "Venus", 7: "Mars",
    8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}

# Exaltation rulers (擢升)
EXALTATION = {
    0: "Sun",       # Sun exalted in Aries (19°)
    1: "Moon",      # Moon exalted in Taurus (3°)
    2: None,
    3: "Jupiter",   # Jupiter exalted in Cancer (15°)
    4: None,
    5: "Mercury",   # Mercury exalted in Virgo (15°)
    6: "Saturn",    # Saturn exalted in Libra (21°)
    7: None,
    8: None,
    9: "Mars",      # Mars exalted in Capricorn (28°)
    10: None,
    11: "Venus",    # Venus exalted in Pisces (27°)
}

# Detriment (落陷 — opposite of domicile)
DETRIMENT = {
    0: "Venus", 1: "Mars", 2: "Jupiter", 3: "Saturn",
    4: "Saturn", 5: "Jupiter", 6: "Mars", 7: "Venus",
    8: "Mercury", 9: "Moon", 10: "Sun", 11: "Mercury",
}

# Fall (衰 — opposite of exaltation)
FALL = {
    0: "Saturn", 1: None, 2: None, 3: "Mars",
    4: None, 5: "Venus", 6: "Sun", 7: "Moon",
    8: None, 9: "Jupiter", 10: None, 11: "Mercury",
}

# Triplicity rulers (三分主星) — day ruler, night ruler
TRIPLICITY = {
    "fire":  ("Sun", "Jupiter"),
    "earth": ("Venus", "Moon"),
    "air":   ("Saturn", "Mercury"),
    "water": ("Mars", "Mars"),
}

SIGN_ELEMENT = {
    0: "fire", 1: "earth", 2: "air", 3: "water",
    4: "fire", 5: "earth", 6: "air", 7: "water",
    8: "fire", 9: "earth", 10: "air", 11: "water",
}

# Egyptian terms (界) — list of (planet, end_degree) for each sign
TERMS = {
    0:  [("Jupiter", 6), ("Venus", 12), ("Mercury", 20), ("Mars", 25), ("Saturn", 30)],
    1:  [("Venus", 8), ("Mercury", 14), ("Jupiter", 22), ("Saturn", 27), ("Mars", 30)],
    2:  [("Mercury", 6), ("Jupiter", 12), ("Venus", 17), ("Mars", 24), ("Saturn", 30)],
    3:  [("Mars", 7), ("Venus", 13), ("Mercury", 19), ("Jupiter", 26), ("Saturn", 30)],
    4:  [("Jupiter", 6), ("Venus", 11), ("Saturn", 18), ("Mercury", 24), ("Mars", 30)],
    5:  [("Mercury", 7), ("Venus", 17), ("Jupiter", 21), ("Mars", 28), ("Saturn", 30)],
    6:  [("Saturn", 6), ("Mercury", 14), ("Jupiter", 21), ("Venus", 28), ("Mars", 30)],
    7:  [("Mars", 7), ("Venus", 11), ("Mercury", 19), ("Jupiter", 24), ("Saturn", 30)],
    8:  [("Jupiter", 12), ("Venus", 17), ("Mercury", 21), ("Saturn", 26), ("Mars", 30)],
    9:  [("Mercury", 7), ("Jupiter", 14), ("Venus", 22), ("Saturn", 26), ("Mars", 30)],
    10: [("Mercury", 7), ("Venus", 13), ("Jupiter", 20), ("Mars", 25), ("Saturn", 30)],
    11: [("Venus", 12), ("Jupiter", 16), ("Mercury", 19), ("Mars", 28), ("Saturn", 30)],
}

# Face/Decan (面) — Chaldean order
_FACE_ORDER = ["Mars", "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter"]


def _build_faces() -> dict[int, list[str]]:
    faces = {}
    idx = 0
    for sign in range(12):
        faces[sign] = []
        for _ in range(3):
            faces[sign].append(_FACE_ORDER[idx % 7])
            idx += 1
    return faces


FACES = _build_faces()

# Dignity scores (for weighted reception evaluation)
DIGNITY_SCORES = {
    "domicile": 5,
    "exaltation": 4,
    "triplicity": 3,
    "term": 2,
    "face": 1,
}


def get_sign(lon: float) -> int:
    return int(lon % 360) // 30


def get_degree_in_sign(lon: float) -> float:
    return lon % 30


def get_domicile_ruler(lon: float) -> str:
    return DOMICILE[get_sign(lon)]


def get_exaltation_ruler(lon: float) -> str | None:
    return EXALTATION[get_sign(lon)]


def get_triplicity_rulers(lon: float) -> tuple[str, str]:
    """Return (day_ruler, night_ruler) for the sign."""
    element = SIGN_ELEMENT[get_sign(lon)]
    return TRIPLICITY[element]


def get_term_ruler(lon: float) -> str:
    sign = get_sign(lon)
    deg = get_degree_in_sign(lon)
    for planet, end_deg in TERMS[sign]:
        if deg < end_deg:
            return planet
    return TERMS[sign][-1][0]


def get_face_ruler(lon: float) -> str:
    sign = get_sign(lon)
    deg = get_degree_in_sign(lon)
    decan = min(int(deg // 10), 2)
    return FACES[sign][decan]


def get_dignities_for_planet(planet_name: str, lon: float) -> dict[str, str]:
    """Get all dignity/debility info for a planet at a given longitude."""
    result: dict[str, str] = {}
    sign = get_sign(lon)

    if DOMICILE[sign] == planet_name:
        result["domicile"] = "+"
    if EXALTATION[sign] == planet_name:
        result["exaltation"] = "+"
    day_r, night_r = get_triplicity_rulers(lon)
    if planet_name in (day_r, night_r):
        result["triplicity"] = "+"
    if get_term_ruler(lon) == planet_name:
        result["term"] = "+"
    if get_face_ruler(lon) == planet_name:
        result["face"] = "+"
    if DETRIMENT.get(sign) == planet_name:
        result["detriment"] = "-"
    if FALL.get(sign) == planet_name:
        result["fall"] = "-"

    return result


def get_all_dignities_at(lon: float) -> dict[str, list[str]]:
    """
    Get all planets that have dignity at a given longitude.

    Returns dict like {"domicile": ["Venus"], "exaltation": ["Moon"], "triplicity": [...], ...}
    """
    sign = get_sign(lon)
    result: dict[str, list[str]] = {}
    result["domicile"] = [DOMICILE[sign]]
    if EXALTATION[sign]:
        result["exaltation"] = [EXALTATION[sign]]
    day_r, night_r = get_triplicity_rulers(lon)
    result["triplicity"] = list(dict.fromkeys([day_r, night_r]))  # dedupe preserving order
    result["term"] = [get_term_ruler(lon)]
    result["face"] = [get_face_ruler(lon)]
    return result


# ---- Reception analysis ----

@dataclass
class Reception:
    """A reception relationship between two planets."""
    planet_a: str       # the "guest" or first planet
    planet_b: str       # the "host"/receiver or second planet
    rtype: str          # reception type (see below)
    strength: int       # total dignity score
    has_aspect: bool    # whether the two planets have a major aspect
    detail: str         # human-readable detail

    # rtype values:
    # "mutual_domicile"  — strongest mutual reception (5+5=10)
    # "mutual_exalt"     — mutual reception by exaltation (4+4=8)
    # "mutual_mixed"     — domicile+exaltation cross (5+4=9)
    # "mutual_minor"     — mutual reception by combined minor dignities (Bonatti: need 2+)
    # "reception"        — one-way reception (host receives guest)


def _get_dignities_of_planet_at(planet_name: str, lon: float) -> list[str]:
    """What dignities does `planet_name` have at longitude `lon`?"""
    result = []
    dignities = get_all_dignities_at(lon)
    for dtype, rulers in dignities.items():
        if planet_name in rulers:
            result.append(dtype)
    return result


def find_receptions(
    planets: dict[str, float],
    aspect_pairs: set[tuple[str, str]] | None = None,
) -> list[Reception]:
    """
    Find all receptions between planets.

    Args:
        planets: dict of planet_name -> longitude
        aspect_pairs: set of (planet_a, planet_b) tuples that have aspects.
                     If None, aspect info is not checked.

    Rules applied:
    - Domicile or exaltation: sufficient alone for reception.
    - Single minor dignity (triplicity/term/face) alone: NOT sufficient.
    - Two or more minor dignities combined: sufficient (Bonatti's rule).
    - Mutual receptions are detected and reported with combined strength.
    - Each reception is tagged with whether an aspect exists.
    """
    results: list[Reception] = []
    skip = {"North Node"}
    planet_names = [p for p in planets if p not in skip]

    def has_asp(a: str, b: str) -> bool:
        if aspect_pairs is None:
            return False
        return (a, b) in aspect_pairs or (b, a) in aspect_pairs

    # For each pair, compute what dignities each has at the other's position
    for i, pa in enumerate(planet_names):
        for pb in planet_names[i + 1:]:
            lon_a = planets[pa]
            lon_b = planets[pb]

            # What dignities does pb have at lon_a? (pb could "receive" pa)
            pb_digs_at_a = _get_dignities_of_planet_at(pb, lon_a)
            # What dignities does pa have at lon_b? (pa could "receive" pb)
            pa_digs_at_b = _get_dignities_of_planet_at(pa, lon_b)

            aspected = has_asp(pa, pb)

            # --- Check mutual reception ---
            mutual_found = False

            # Both have major dignity at each other's position?
            a_major = [d for d in pa_digs_at_b if d in ("domicile", "exaltation")]
            b_major = [d for d in pb_digs_at_a if d in ("domicile", "exaltation")]

            if a_major and b_major:
                mutual_found = True
                # Pick the strongest combination
                best_a = max(a_major, key=lambda d: DIGNITY_SCORES[d])
                best_b = max(b_major, key=lambda d: DIGNITY_SCORES[d])
                score = DIGNITY_SCORES[best_a] + DIGNITY_SCORES[best_b]

                if best_a == "domicile" and best_b == "domicile":
                    rtype = "mutual_domicile"
                elif best_a == "exaltation" and best_b == "exaltation":
                    rtype = "mutual_exalt"
                else:
                    rtype = "mutual_mixed"

                results.append(Reception(
                    pa, pb, rtype, score, aspected,
                    f"{pa} in {pb}'s {best_b}, {pb} in {pa}'s {best_a}",
                ))

            if not mutual_found:
                # Check minor-dignity mutual reception (Bonatti: need 2+ each side)
                a_minor = [d for d in pa_digs_at_b if d in ("triplicity", "term", "face")]
                b_minor = [d for d in pb_digs_at_a if d in ("triplicity", "term", "face")]
                if len(a_minor) >= 2 and len(b_minor) >= 2:
                    mutual_found = True
                    score_a = sum(DIGNITY_SCORES[d] for d in a_minor)
                    score_b = sum(DIGNITY_SCORES[d] for d in b_minor)
                    results.append(Reception(
                        pa, pb, "mutual_minor", score_a + score_b, aspected,
                        f"{pa} in {pb}'s {'+'.join(b_minor)}, {pb} in {pa}'s {'+'.join(a_minor)}",
                    ))

            # --- One-way receptions (require aspect) ---
            if not mutual_found and aspected:
                # pb receives pa
                _add_one_way(results, pa, pb, pb_digs_at_a, aspected)
                # pa receives pb
                _add_one_way(results, pb, pa, pa_digs_at_b, aspected)

    # Sort: mutual first, then by strength descending, then aspected first
    results.sort(key=lambda r: (
        0 if r.rtype.startswith("mutual") else 1,
        -r.strength,
        0 if r.has_aspect else 1,
    ))
    return results


def _add_one_way(
    results: list[Reception],
    guest: str,
    host: str,
    host_dignities: list[str],
    aspected: bool,
) -> None:
    """Add one-way reception if the host has sufficient dignity."""
    if not host_dignities:
        return

    major = [d for d in host_dignities if d in ("domicile", "exaltation")]
    minor = [d for d in host_dignities if d in ("triplicity", "term", "face")]

    if major:
        # Major dignity alone is sufficient
        best = max(major, key=lambda d: DIGNITY_SCORES[d])
        score = DIGNITY_SCORES[best]
        results.append(Reception(
            guest, host, "reception", score, aspected,
            f"{host} receives {guest} by {best}",
        ))
    elif len(minor) >= 2:
        # Bonatti: two+ minor dignities combined
        score = sum(DIGNITY_SCORES[d] for d in minor)
        results.append(Reception(
            guest, host, "reception", score, aspected,
            f"{host} receives {guest} by {'+'.join(minor)}",
        ))
    # Single minor dignity alone: not sufficient, skip
