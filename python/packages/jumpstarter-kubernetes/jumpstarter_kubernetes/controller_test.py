"""Tests for controller version discovery."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from jumpstarter_kubernetes.controller import get_latest_compatible_controller_version
from jumpstarter_kubernetes.exceptions import JumpstarterKubernetesError

GITHUB_RELEASES_URL = "https://api.github.com/repos/jumpstarter-dev/jumpstarter/releases"


class TestGetLatestCompatibleControllerVersion:
    """Test controller version discovery via GitHub releases API."""

    @pytest.mark.asyncio
    async def test_queries_github_releases_api(self):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(
            return_value=[{"tag_name": "v1.0.0"}, {"tag_name": "v1.0.1"}]
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("jumpstarter_kubernetes.controller.aiohttp.ClientSession", return_value=mock_session):
            result = await get_latest_compatible_controller_version(None)

        mock_session.get.assert_called_once()
        called_url = mock_session.get.call_args[0][0]
        assert called_url == GITHUB_RELEASES_URL
        assert result == "v1.0.1"

    @pytest.mark.asyncio
    async def test_selects_compatible_version(self):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(
            return_value=[
                {"tag_name": "v1.0.0"},
                {"tag_name": "v1.0.3"},
                {"tag_name": "v2.0.0"},
            ]
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("jumpstarter_kubernetes.controller.aiohttp.ClientSession", return_value=mock_session):
            result = await get_latest_compatible_controller_version("v1.0.0")

        assert result == "v1.0.3"

    @pytest.mark.asyncio
    async def test_falls_back_when_no_compatible_version(self):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(
            return_value=[
                {"tag_name": "v2.0.0"},
                {"tag_name": "v3.0.0"},
            ]
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("jumpstarter_kubernetes.controller.aiohttp.ClientSession", return_value=mock_session):
            result = await get_latest_compatible_controller_version("v1.0.0")

        assert result == "v3.0.0"

    @pytest.mark.asyncio
    async def test_raises_on_empty_releases(self):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=[])
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("jumpstarter_kubernetes.controller.aiohttp.ClientSession", return_value=mock_session):
            with pytest.raises(JumpstarterKubernetesError, match="No valid controller versions found"):
                await get_latest_compatible_controller_version(None)

    @pytest.mark.asyncio
    async def test_invalid_client_version_raises(self):
        with pytest.raises(JumpstarterKubernetesError, match="Invalid client version"):
            await get_latest_compatible_controller_version("not-a-version")

    @pytest.mark.asyncio
    async def test_skips_invalid_tag_names(self):
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(
            return_value=[
                {"tag_name": "latest"},
                {"tag_name": "v1.0.0"},
            ]
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("jumpstarter_kubernetes.controller.aiohttp.ClientSession", return_value=mock_session):
            result = await get_latest_compatible_controller_version(None)

        assert result == "v1.0.0"
