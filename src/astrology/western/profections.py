"""Annual Profections — the simplest time-lord technique.

Each year of life activates a house (age mod 12) and its ruler becomes
the Lord of the Year. All transits/returns involving that planet are
especially significant.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .dignities import DOMICILE


HOUSE_TOPICS = {
    1: "self, body, vitality",
    2: "money, possessions, values",
    3: "siblings, communication, short trips",
    4: "home, family, roots, father",
    5: "children, creativity, pleasure",
    6: "health, work, service",
    7: "relationships, partnerships, open enemies",
    8: "shared resources, death, transformation",
    9: "travel, higher education, philosophy",
    10: "career, reputation, public life",
    11: "friends, groups, hopes",
    12: "hidden enemies, isolation, spirituality",
}


@dataclass
class ProfectionResult:
    """Annual profection for a specific year."""

    age: int
    house: int              # 1-12
    sign_index: int         # 0-11, sign on the profected house cusp
    lord_of_year: str       # planet ruling that sign
    topics: str             # house topics description

    @property
    def house_label(self) -> str:
        suffixes = {1: "st", 2: "nd", 3: "rd"}
        s = suffixes.get(self.house if self.house < 20 else self.house % 10, "th")
        return f"{self.house}{s}"


def annual_profection(
    birth_date: tuple[int, int, int],
    target_year: int,
    cusps: list[float],
) -> ProfectionResult:
    """Calculate annual profection for a given year.

    Args:
        birth_date: (year, month, day) of birth.
        target_year: the year to calculate for.
        cusps: list of 12 house cusp longitudes (from natal chart).

    Returns:
        ProfectionResult with the activated house and lord of the year.
    """
    by, bm, bd = birth_date
    # Age at the start of the profection year (birthday to birthday)
    # If target_year's birthday hasn't happened yet, we're still in the previous profection year
    age = target_year - by
    # The profection year runs from birthday to birthday
    # age 0 = 1st house, age 1 = 2nd house, etc.
    house = (age % 12) + 1  # 1-indexed

    # The sign on that house cusp determines the lord
    cusp_lon = cusps[house - 1]
    sign_index = int(cusp_lon // 30) % 12
    lord = DOMICILE[sign_index]

    return ProfectionResult(
        age=age,
        house=house,
        sign_index=sign_index,
        lord_of_year=lord,
        topics=HOUSE_TOPICS[house],
    )
