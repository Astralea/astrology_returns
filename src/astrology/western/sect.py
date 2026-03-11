"""Sect — the diurnal/nocturnal team system.

Diurnal team (day): Sun, Jupiter, Saturn
Nocturnal team (night): Moon, Venus, Mars
Mercury is neutral (sect by sign: diurnal in diurnal signs, nocturnal in nocturnal).

A planet "in sect" means:
1. It belongs to the correct team (diurnal planet in a day chart, or vice versa)
2. Bonus: in a sign of matching sect (fire/air = diurnal, earth/water = nocturnal)
3. Bonus: above/below horizon matching its nature
   - Diurnal planets prefer to be above horizon by day
   - Nocturnal planets prefer to be below horizon by night

The most "in sect" planet (benefic of sect) is the strongest helper;
the most "contrary to sect" (malefic contrary to sect) is the biggest troublemaker.
"""

from __future__ import annotations

from dataclasses import dataclass


# Planet sect membership
DIURNAL_PLANETS = {"Sun", "Jupiter", "Saturn"}
NOCTURNAL_PLANETS = {"Moon", "Venus", "Mars"}

# Diurnal signs (fire + air)
DIURNAL_SIGNS = {0, 2, 4, 6, 8, 10}  # Ari, Gem, Leo, Lib, Sag, Aqu
# Nocturnal signs (earth + water)
NOCTURNAL_SIGNS = {1, 3, 5, 7, 9, 11}  # Tau, Can, Vir, Sco, Cap, Pis


@dataclass
class SectStatus:
    """Sect analysis for a single planet."""

    planet: str
    in_sect: bool           # belongs to the ruling sect team
    in_sect_sign: bool      # in a sign matching its sect
    in_sect_position: bool  # above/below horizon matching its nature
    score: int              # 0-3, how many sect conditions are met

    @property
    def label(self) -> str:
        if self.score == 3:
            return "fully in sect"
        if self.score == 0:
            return "contrary to sect"
        parts = []
        if self.in_sect:
            parts.append("sect")
        if self.in_sect_sign:
            parts.append("sign")
        if self.in_sect_position:
            parts.append("position")
        return "in sect by " + "+".join(parts)


@dataclass
class SectAnalysis:
    """Full sect analysis for a chart."""

    is_diurnal: bool
    statuses: dict[str, SectStatus]
    benefic_of_sect: str      # most helpful planet
    malefic_of_sect: str      # challenging but manageable
    benefic_contrary: str     # less helpful than expected
    malefic_contrary: str     # most problematic planet


def _is_above_horizon(planet_lon: float, cusps: list[float]) -> bool:
    """Check if a planet is above the horizon (houses 7-12)."""
    from ..western.formatting import _find_house
    house = _find_house(planet_lon, cusps)
    return house >= 7


def analyze_sect(
    planets: dict[str, float],
    cusps: list[float],
    is_diurnal: bool,
) -> SectAnalysis:
    """Analyze sect conditions for all planets.

    Args:
        planets: planet name -> longitude.
        cusps: 12 house cusps.
        is_diurnal: True if Sun is above horizon at birth.
    """
    statuses: dict[str, SectStatus] = {}

    for name, lon in planets.items():
        if name in ("North Node", "Chiron"):
            continue

        sign_idx = int(lon // 30) % 12
        above = _is_above_horizon(lon, cusps)

        # 1. Team membership
        if name in DIURNAL_PLANETS:
            in_sect = is_diurnal
        elif name in NOCTURNAL_PLANETS:
            in_sect = not is_diurnal
        else:
            # Mercury: sect by sign
            in_sect = (sign_idx in DIURNAL_SIGNS) == is_diurnal

        # 2. Sign sect
        planet_is_diurnal_nature = name in DIURNAL_PLANETS or (
            name == "Mercury" and sign_idx in DIURNAL_SIGNS
        )
        if name in NOCTURNAL_PLANETS:
            in_sect_sign = sign_idx in NOCTURNAL_SIGNS
        elif name in DIURNAL_PLANETS:
            in_sect_sign = sign_idx in DIURNAL_SIGNS
        else:
            # Mercury follows sign
            in_sect_sign = in_sect

        # 3. Position (hemisphere)
        if name in DIURNAL_PLANETS:
            in_sect_position = above  # diurnal planets prefer above
        elif name in NOCTURNAL_PLANETS:
            in_sect_position = not above  # nocturnal planets prefer below
        else:
            # Mercury: diurnal above, nocturnal below
            in_sect_position = above if (sign_idx in DIURNAL_SIGNS) else not above

        score = sum([in_sect, in_sect_sign, in_sect_position])

        statuses[name] = SectStatus(
            planet=name,
            in_sect=in_sect,
            in_sect_sign=in_sect_sign,
            in_sect_position=in_sect_position,
            score=score,
        )

    # Identify the four key sect planets
    if is_diurnal:
        benefic_of_sect = "Jupiter"
        malefic_of_sect = "Saturn"
        benefic_contrary = "Venus"
        malefic_contrary = "Mars"
    else:
        benefic_of_sect = "Venus"
        malefic_of_sect = "Mars"
        benefic_contrary = "Jupiter"
        malefic_contrary = "Saturn"

    return SectAnalysis(
        is_diurnal=is_diurnal,
        statuses=statuses,
        benefic_of_sect=benefic_of_sect,
        malefic_of_sect=malefic_of_sect,
        benefic_contrary=benefic_contrary,
        malefic_contrary=malefic_contrary,
    )
