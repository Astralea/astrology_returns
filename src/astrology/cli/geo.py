"""Geo lookup command."""

from __future__ import annotations

import click

from ..core.geo import geocode


@click.command()
@click.argument("city_name")
def geo(city_name):
    """Look up coordinates for a city name."""
    loc, address = geocode(city_name)
    click.echo(f"  {address}")
    click.echo(f"  Latitude:  {loc.lat}")
    click.echo(f"  Longitude: {loc.lon}")
    click.echo(f"  For --location: {loc.lat},{loc.lon}")
