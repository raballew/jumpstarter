import subprocess
from unittest.mock import patch

import pytest

from jumpstarter.common.ipaddr import get_minikube_ip


class TestIPAddressDetection:
    """Test IP address detection functions."""

    @pytest.mark.anyio
    @patch("jumpstarter.common.ipaddr.anyio.run_process")
    async def test_get_minikube_ip_success(self, mock_run_process):
        mock_run_process.return_value = subprocess.CompletedProcess(
            args=["minikube", "ip"], returncode=0, stdout=b"192.168.49.2\n", stderr=b""
        )

        result = await get_minikube_ip()

        assert result == "192.168.49.2"
        mock_run_process.assert_called_once_with(
            ["minikube", "ip"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    @pytest.mark.anyio
    @patch("jumpstarter.common.ipaddr.anyio.run_process")
    async def test_get_minikube_ip_with_profile(self, mock_run_process):
        mock_run_process.return_value = subprocess.CompletedProcess(
            args=["minikube", "ip", "-p", "test-profile"], returncode=0, stdout=b"192.168.49.3\n", stderr=b""
        )

        result = await get_minikube_ip("test-profile")

        assert result == "192.168.49.3"
        mock_run_process.assert_called_once_with(
            ["minikube", "ip", "-p", "test-profile"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    @pytest.mark.anyio
    @patch("jumpstarter.common.ipaddr.anyio.run_process")
    async def test_get_minikube_ip_custom_binary(self, mock_run_process):
        mock_run_process.return_value = subprocess.CompletedProcess(
            args=["custom-minikube", "ip"], returncode=0, stdout=b"10.0.0.5\n", stderr=b""
        )

        result = await get_minikube_ip(minikube="custom-minikube")

        assert result == "10.0.0.5"
        mock_run_process.assert_called_once_with(
            ["custom-minikube", "ip"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    @pytest.mark.anyio
    @patch("jumpstarter.common.ipaddr.anyio.run_process")
    async def test_get_minikube_ip_failure(self, mock_run_process):
        mock_run_process.return_value = subprocess.CompletedProcess(
            args=["minikube", "ip"], returncode=1, stdout=b"", stderr=b"error: cluster not found\n"
        )

        with pytest.raises(RuntimeError, match="error: cluster not found"):
            await get_minikube_ip()

    @pytest.mark.anyio
    @patch("jumpstarter.common.ipaddr.anyio.run_process")
    async def test_get_minikube_ip_profile_and_custom_binary(self, mock_run_process):
        mock_run_process.return_value = subprocess.CompletedProcess(
            args=["my-minikube", "ip", "-p", "my-profile"], returncode=0, stdout=b"172.16.0.1\n", stderr=b""
        )

        result = await get_minikube_ip("my-profile", "my-minikube")

        assert result == "172.16.0.1"
        mock_run_process.assert_called_once_with(
            ["my-minikube", "ip", "-p", "my-profile"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
