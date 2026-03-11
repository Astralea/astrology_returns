"""Solar return and lunar return calculations."""

from __future__ import annotations

import swisseph as swe

from .chart import ChartData, calculate_chart_from_jd
from .ephemeris import (
    GeoLocation,
    datetime_to_jd,
    find_exact_return,
    get_planet_lon,
)


def solar_return(
    natal_year: int,
    natal_month: int,
    natal_day: int,
    natal_hour_ut: float,
    return_year: int,
    location: GeoLocation,
    house_system: str = "placidus",
) -> ChartData:
    """
    Calculate the solar return chart for a given year.

    The solar return is when the transiting Sun returns to the exact
    natal Sun longitude.

    Args:
        natal_*: Birth date/time in UT.
        return_year: Year for which to calculate the solar return.
        location: Location for the return chart (where you are, not birth place).
        house_system: House system to use.

    Returns:
        ChartData for the solar return moment.
    """
    # Get natal Sun longitude
    natal_jd = datetime_to_jd(natal_year, natal_month, natal_day, natal_hour_ut)
    natal_sun_lon = get_planet_lon(natal_jd, swe.SUN)

    # Start searching a few days before birthday in the return year
    search_start = datetime_to_jd(return_year, natal_month, natal_day, 0.0) - 5.0

    return_jd = find_exact_return(search_start, natal_sun_lon, swe.SUN)
    return calculate_chart_from_jd(return_jd, location, house_system)


def lunar_return(
    natal_year: int,
    natal_month: int,
    natal_day: int,
    natal_hour_ut: float,
    search_after_year: int,
    search_after_month: int,
    search_after_day: int,
    location: GeoLocation,
    house_system: str = "placidus",
) -> ChartData:
    """
    Calculate the next lunar return after a given date.

    The lunar return is when the transiting Moon returns to the exact
    natal Moon longitude (~every 27.3 days).

    Args:
        natal_*: Birth date/time in UT.
        search_after_*: Find the next lunar return after this date.
        location: Location for the return chart.
        house_system: House system to use.

    Returns:
        ChartData for the lunar return moment.
    """
    natal_jd = datetime_to_jd(natal_year, natal_month, natal_day, natal_hour_ut)
    natal_moon_lon = get_planet_lon(natal_jd, swe.MOON)

    search_start = datetime_to_jd(
        search_after_year, search_after_month, search_after_day, 0.0
    )

    return_jd = find_exact_return(search_start, natal_moon_lon, swe.MOON)
    return calculate_chart_from_jd(return_jd, location, house_system)


def lunar_returns_in_year(
    natal_year: int,
    natal_month: int,
    natal_day: int,
    natal_hour_ut: float,
    year: int,
    location: GeoLocation,
    house_system: str = "placidus",
) -> list[ChartData]:
    """Calculate all lunar returns in a given year (~13 returns)."""
    results = []
    search_jd = datetime_to_jd(year, 1, 1, 0.0)
    year_end_jd = datetime_to_jd(year + 1, 1, 1, 0.0)

    natal_jd = datetime_to_jd(natal_year, natal_month, natal_day, natal_hour_ut)
    natal_moon_lon = get_planet_lon(natal_jd, swe.MOON)

    while search_jd < year_end_jd:
        return_jd = find_exact_return(search_jd, natal_moon_lon, swe.MOON)
        if return_jd >= year_end_jd:
            break
        results.append(calculate_chart_from_jd(return_jd, location, house_system))
        # Jump forward ~25 days to find the next one
        search_jd = return_jd + 25.0

    return results
