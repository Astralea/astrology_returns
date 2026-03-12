"""Synastry — cross-chart aspect analysis between two natal charts."""

from __future__ import annotations

from dataclasses import dataclass

from .aspects import ASPECTS, PLANET_ORBS

# Outer/generational points — aspects between these are meaningless in synastry
_GENERATIONAL = {"Uranus", "Neptune", "Pluto", "North Node"}


@dataclass
class SynastryAspect:
    """An aspect between a planet in chart A and a planet in chart B."""

    planet_a: str  # person A's planet
    planet_b: str  # person B's planet
    aspect_name: str
    aspect_angle: int
    orb: float
    symbol: str


def calculate_synastry(
    planets_a: dict[str, float],
    planets_b: dict[str, float],
) -> list[SynastryAspect]:
    """
    Calculate all inter-chart aspects between two sets of planets.

    Every planet in chart A is checked against every planet in chart B.
    (Unlike natal aspects, we don't skip i < j — all cross-pairs matter.)

    Returns:
        List of SynastryAspect sorted by tightness of orb.
    """
    results: list[SynastryAspect] = []

    for pa, lon_a in planets_a.items():
        for pb, lon_b in planets_b.items():
            # Skip generational-to-generational aspects (everyone born nearby has them)
            if pa in _GENERATIONAL and pb in _GENERATIONAL:
                continue

            diff = abs(lon_a - lon_b)
            if diff > 180:
                diff = 360 - diff

            for asp_name, (angle, symbol) in ASPECTS.items():
                orb_a = PLANET_ORBS.get(pa, 7.0)
                orb_b = PLANET_ORBS.get(pb, 7.0)
                max_orb = (orb_a + orb_b) / 2.0

                actual_orb = abs(diff - angle)
                if actual_orb <= max_orb:
                    results.append(SynastryAspect(
                        planet_a=pa,
                        planet_b=pb,
                        aspect_name=asp_name,
                        aspect_angle=angle,
                        orb=actual_orb,
                        symbol=symbol,
                    ))

    results.sort(key=lambda a: a.orb)
    return results
