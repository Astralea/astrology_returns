"""CLI entry point and command registration."""

from __future__ import annotations

import click

from .common import location_options, house_system_option, ut_option


@click.group()
@click.option(
    "--unicode/--no-unicode",
    default=False,
    help="Use unicode zodiac symbols.",
)
@click.option(
    "--modern/--traditional",
    default=False,
    help="Include outer planets (Uranus/Neptune/Pluto) in dignities & receptions. Default: traditional (exclude them).",
)
@click.pass_context
def cli(ctx, unicode, modern):
    """Astrology chart calculator — natal charts, returns, transits & more."""
    ctx.ensure_object(dict)
    ctx.obj["unicode"] = unicode
    ctx.obj["modern"] = modern


# Import and register subcommands
from .natal import natal  # noqa: E402
from .returns import sr, lr, lr_year  # noqa: E402
from .horary import horary  # noqa: E402
from .transits import transit  # noqa: E402
from .geo import geo  # noqa: E402
from .profection import profection  # noqa: E402
from .firdaria import firdaria  # noqa: E402
from .forecast import forecast  # noqa: E402
from .synastry import synastry  # noqa: E402

cli.add_command(natal)
cli.add_command(sr)
cli.add_command(lr)
cli.add_command(lr_year)
cli.add_command(horary)
cli.add_command(transit)
cli.add_command(geo)
cli.add_command(profection)
cli.add_command(firdaria)
cli.add_command(forecast)
cli.add_command(synastry)


def main():
    cli()
