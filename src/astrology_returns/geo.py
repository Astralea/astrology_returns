"""City name to coordinates geocoding via OpenStreetMap Nominatim."""

from __future__ import annotations

import click
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geopy.geocoders import Nominatim

from .ephemeris import GeoLocation

_geolocator = Nominatim(user_agent="astrology-returns", timeout=10)


def geocode(city: str) -> tuple[GeoLocation, str]:
    """
    Look up a city name and return (GeoLocation, display_name).

    Raises click.ClickException on failure.
    """
    try:
        result = _geolocator.geocode(city)
    except GeocoderTimedOut:
        raise click.ClickException(
            f"Geocoding timed out for {city!r}. Check your network or use --location instead."
        )
    except GeocoderServiceError as e:
        raise click.ClickException(f"Geocoding failed: {e}. Use --location instead.")

    if result is None:
        raise click.ClickException(
            f"Location not found: {city!r}. Try a different name or use --location."
        )
    return (
        GeoLocation(lat=result.latitude, lon=result.longitude),
        result.address,
    )
