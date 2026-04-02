from typing import Optional

import aiohttp
import semver
from packaging.version import Version

from .exceptions import JumpstarterKubernetesError

GITHUB_RELEASES_URL = "https://api.github.com/repos/jumpstarter-dev/jumpstarter/releases"


async def get_latest_compatible_controller_version(client_version: Optional[str]):  # noqa: C901
    """Get the latest compatible controller version for a given client version"""
    if client_version is None:
        use_fallback_only = True
        client_version_parsed = None
    else:
        use_fallback_only = False
        version_to_parse = client_version[1:] if client_version.startswith("v") else client_version
        try:
            client_version_parsed = Version(version_to_parse)
        except Exception as e:
            raise JumpstarterKubernetesError(
                f"Invalid client version '{client_version}': {e}"
            ) from e

    async with aiohttp.ClientSession(
        raise_for_status=True,
    ) as session:
        try:
            async with session.get(
                GITHUB_RELEASES_URL,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                releases = await resp.json()
        except Exception as e:
            raise JumpstarterKubernetesError(f"Failed to fetch controller versions: {e}") from e

    compatible = set()
    fallback = set()

    if not isinstance(releases, list):
        raise JumpstarterKubernetesError("Unexpected response fetching controller version")

    for release in releases:
        if not isinstance(release, dict) or "tag_name" not in release:
            continue

        tag_name = release["tag_name"]
        version_str = tag_name[1:] if tag_name.startswith("v") else tag_name

        try:
            version = semver.VersionInfo.parse(version_str)
        except ValueError:
            continue

        if use_fallback_only:
            fallback.add((version, tag_name))
        elif version.major == client_version_parsed.major and version.minor == client_version_parsed.minor:
            compatible.add((version, tag_name))
        else:
            fallback.add((version, tag_name))

    if compatible:
        selected_version, selected_tag = max(compatible)
    elif fallback:
        selected_version, selected_tag = max(fallback)
    else:
        raise JumpstarterKubernetesError("No valid controller versions found in the repository")

    return selected_tag
