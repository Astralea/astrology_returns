"""Arabic Lots (Greek: Kleros) — Lot of Fortune and Lot of Spirit.

Fortune = ASC + Moon - Sun  (diurnal)  /  ASC + Sun - Moon  (nocturnal)
Spirit  = ASC + Sun - Moon  (diurnal)  /  ASC + Moon - Sun  (nocturnal)

Fortune: body, health, material circumstances, external luck.
Spirit:  mind, will, action, career direction, agency.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LotResult:
    """A calculated Arabic Lot."""

    name: str
    longitude: float   # 0-360
    description: str


def lot_of_fortune(asc: float, sun: float, moon: float, is_diurnal: bool) -> LotResult:
    """Calculate the Lot of Fortune."""
    if is_diurnal:
        lon = (asc + moon - sun) % 360
    else:
        lon = (asc + sun - moon) % 360
    return LotResult("Fortune", lon, "body, health, material circumstances, luck")


def lot_of_spirit(asc: float, sun: float, moon: float, is_diurnal: bool) -> LotResult:
    """Calculate the Lot of Spirit."""
    if is_diurnal:
        lon = (asc + sun - moon) % 360
    else:
        lon = (asc + moon - sun) % 360
    return LotResult("Spirit", lon, "mind, will, action, career direction")


def calculate_lots(
    asc: float,
    planets: dict[str, float],
    is_diurnal: bool,
) -> list[LotResult]:
    """Calculate Fortune and Spirit lots."""
    sun = planets.get("Sun", 0.0)
    moon = planets.get("Moon", 0.0)
    return [
        lot_of_fortune(asc, sun, moon, is_diurnal),
        lot_of_spirit(asc, sun, moon, is_diurnal),
    ]
