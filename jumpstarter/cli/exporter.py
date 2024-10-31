import logging
from pathlib import Path

import anyio
import click

from jumpstarter.common.utils import launch_shell
from jumpstarter.config.exporter import ExporterConfigV1Alpha1

from .util import make_table
from .version import version


@click.group()
def exporter():
    """Manage and run exporters"""
    logging.basicConfig(level=logging.INFO)


arg_alias = click.argument("alias", default="default")
opt_config_path = click.option(
    "-c", "--config", "config_path", type=click.Path(exists=True), help="Path of exporter config, overrides ALIAS"
)


@exporter.command
@click.option("--endpoint", prompt=True)
@click.option("--token", prompt=True)
@arg_alias
def create(alias, endpoint, token):
    """Create exporter"""
    try:
        ExporterConfigV1Alpha1.load(alias)
    except FileNotFoundError:
        pass
    else:
        raise click.ClickException(f'exporter "{alias}" exists')

    config = ExporterConfigV1Alpha1(
        alias=alias,
        endpoint=endpoint,
        token=token,
    )
    config.save()


@exporter.command
@arg_alias
def delete(alias):
    """Delete exporter"""
    try:
        config = ExporterConfigV1Alpha1.load(alias)
    except FileNotFoundError as err:
        raise click.ClickException(f'exporter "{alias}" does not exist') from err
    config.delete()


@exporter.command
@arg_alias
def edit(alias):
    """Edit exporter"""
    try:
        config = ExporterConfigV1Alpha1.load(alias)
    except FileNotFoundError as err:
        raise click.ClickException(f'exporter "{alias}" does not exist') from err
    click.edit(filename=config.path)


@exporter.command
def list():
    """List exporters"""
    exporters = ExporterConfigV1Alpha1.list()
    columns = ["ALIAS", "PATH"]
    rows = [
        {
            "ALIAS": exporter.alias,
            "PATH": str(exporter.path),
        }
        for exporter in exporters
    ]
    click.echo(make_table(columns, rows))


@exporter.command
@arg_alias
@opt_config_path
def run(alias, config_path):
    """Run exporter"""
    try:
        if config_path:
            config = ExporterConfigV1Alpha1.load_path(Path(config_path))
        else:
            config = ExporterConfigV1Alpha1.load(alias)
    except FileNotFoundError as err:
        raise click.ClickException(f'exporter "{alias}" does not exist') from err

    anyio.run(config.serve_forever)


@exporter.command
@arg_alias
@opt_config_path
def shell(alias, config_path):
    """Spawns a shell connecting to a transient exporter"""
    try:
        if config_path:
            config = ExporterConfigV1Alpha1.load_path(Path(config_path))
        else:
            config = ExporterConfigV1Alpha1.load(alias)
    except FileNotFoundError as err:
        raise click.ClickException(f'exporter "{alias}" does not exist') from err

    with config.serve_unix() as path:
        # SAFETY: the exporter config is local thus considered trusted
        launch_shell(path, allow=[], unsafe=True)


exporter.add_command(version)


if __name__ == "__main__":
    exporter()
