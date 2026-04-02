from typing import Optional

import click
from jumpstarter_cli_common.blocking import blocking
from jumpstarter_kubernetes import (
    minikube_installed,
)

from jumpstarter.common.ipaddr import get_ip_address, get_minikube_ip


async def get_ip_generic(cluster_type: Optional[str], minikube: str, cluster_name: str) -> str:
    if cluster_type == "minikube":
        if not minikube_installed(minikube):
            raise click.ClickException("minikube is not installed (or not in your PATH)")
        try:
            ip = await get_minikube_ip(cluster_name, minikube)
        except Exception as e:
            raise click.ClickException(f"Could not determine Minikube IP address.\n{e}") from e
    else:
        ip = get_ip_address()
        if ip == "0.0.0.0":
            raise click.ClickException("Could not determine IP address, use --ip <IP> to specify an IP address")

    return ip


@click.command
@click.option(
    "--kind", is_flag=False, flag_value="kind", default=None, help="Use default settings for a local Kind cluster"
)
@click.option(
    "--minikube",
    is_flag=False,
    flag_value="minikube",
    default=None,
    help="Use default settings for a local Minikube cluster",
)
@click.option("--cluster-name", type=str, help="The name of the cluster", default="jumpstarter-lab")
@blocking
async def ip(
    kind: Optional[str],
    minikube: Optional[str],
    cluster_name: str,
):
    """Attempt to determine the IP address of your computer"""
    if kind and minikube:
        raise click.ClickException('You can only select one local cluster type "kind" or "minikube"')

    cluster_type = None
    if kind is not None:
        cluster_type = "kind"
    elif minikube is not None:
        cluster_type = "minikube"

    minikube_binary = minikube or "minikube"
    result = await get_ip_generic(cluster_type, minikube_binary, cluster_name)
    click.echo(result)
