from unittest.mock import patch

import pytest
from click.testing import CliRunner
from jumpstarter_kubernetes.callbacks import SilentCallback
from jumpstarter_kubernetes.cluster.kind import create_kind_cluster_with_options
from jumpstarter_kubernetes.cluster.minikube import create_minikube_cluster_with_options
from jumpstarter_kubernetes.cluster.operations import validate_cluster_type_selection

from jumpstarter_cli_admin.install import (
    ip,
)


class TestValidationFunctions:
    """Test validation helper functions."""

    def test_validate_cluster_type_both_specified(self):
        """Test that error is raised when both kind and minikube are specified."""
        from jumpstarter_kubernetes.exceptions import ClusterTypeValidationError

        with pytest.raises(
            ClusterTypeValidationError, match='You can only select one cluster type'
        ):
            validate_cluster_type_selection("kind", "minikube")

    def test_validate_cluster_type_kind_only(self):
        """Test that 'kind' is returned when only kind is specified."""
        result = validate_cluster_type_selection("kind", None)
        assert result == "kind"

    def test_validate_cluster_type_minikube_only(self):
        """Test that 'minikube' is returned when only minikube is specified."""
        result = validate_cluster_type_selection(None, "minikube")
        assert result == "minikube"


class TestClusterCreation:
    """Test cluster creation functions."""

    @pytest.mark.asyncio
    @patch("jumpstarter_kubernetes.cluster.kind.kind_installed")
    @patch("jumpstarter_kubernetes.cluster.kind.create_kind_cluster")
    async def test_create_kind_cluster_with_options_success(self, mock_create_kind, mock_kind_installed):
        """Test creating a Kind cluster with the new function structure."""

        mock_kind_installed.return_value = True
        mock_create_kind.return_value = True
        callback = SilentCallback()

        await create_kind_cluster_with_options(
            "kind", "test-cluster", "--verbosity=1", False, None, callback
        )

        mock_create_kind.assert_called_once()

    @pytest.mark.asyncio
    @patch("jumpstarter_kubernetes.cluster.kind.kind_installed")
    async def test_create_kind_cluster_with_options_not_installed(self, mock_kind_installed):
        """Test that ToolNotInstalledError is raised when kind is not installed."""
        from jumpstarter_kubernetes.exceptions import ToolNotInstalledError

        mock_kind_installed.return_value = False
        callback = SilentCallback()

        with pytest.raises(ToolNotInstalledError, match="kind is not installed"):
            await create_kind_cluster_with_options(
                "kind", "test-cluster", "", False, None, callback
            )

    @pytest.mark.asyncio
    @patch("jumpstarter_kubernetes.cluster.minikube.minikube_installed")
    @patch("jumpstarter_kubernetes.cluster.minikube.create_minikube_cluster")
    async def test_create_minikube_cluster_with_options_success(self, mock_create_minikube, mock_minikube_installed):
        """Test creating a Minikube cluster with the new function structure."""
        mock_minikube_installed.return_value = True
        mock_create_minikube.return_value = True
        callback = SilentCallback()

        await create_minikube_cluster_with_options(
            "minikube", "test-cluster", "--memory=4096", False, None, callback
        )

        mock_create_minikube.assert_called_once()


class TestCLICommands:
    """Test CLI command execution."""

    def test_ip_command_help(self):
        runner = CliRunner()
        result = runner.invoke(ip, ["--help"])
        assert result.exit_code == 0
        assert "Attempt to determine the IP address" in result.output
