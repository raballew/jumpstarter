from unittest.mock import patch

import pytest

from jumpstarter_kubernetes.util.async_custom_object_api import AbstractAsyncCustomObjectApi


class TestNamespaceResolution:
    def test_explicit_namespace_is_stored(self):
        api = AbstractAsyncCustomObjectApi(namespace="my-namespace")
        assert api.namespace == "my-namespace"

    def test_none_namespace_is_stored_before_entering_context(self):
        api = AbstractAsyncCustomObjectApi(namespace=None)
        assert api.namespace is None

    @patch("jumpstarter_kubernetes.util.async_custom_object_api.config")
    def test_none_namespace_resolves_from_kubeconfig_context(self, mock_config):
        mock_config.list_kube_config_contexts.return_value = (
            [{"name": "my-context", "context": {"namespace": "context-ns"}}],
            {"name": "my-context", "context": {"namespace": "context-ns"}},
        )

        api = AbstractAsyncCustomObjectApi(namespace=None)
        assert api._resolve_namespace_from_kubeconfig() == "context-ns"

    @patch("jumpstarter_kubernetes.util.async_custom_object_api.config")
    def test_none_namespace_falls_back_to_default_when_context_has_no_namespace(self, mock_config):
        mock_config.list_kube_config_contexts.return_value = (
            [{"name": "my-context", "context": {"cluster": "my-cluster"}}],
            {"name": "my-context", "context": {"cluster": "my-cluster"}},
        )

        api = AbstractAsyncCustomObjectApi(namespace=None)
        assert api._resolve_namespace_from_kubeconfig() == "default"

    @patch("jumpstarter_kubernetes.util.async_custom_object_api.config")
    def test_none_namespace_falls_back_to_default_when_no_current_context(self, mock_config):
        mock_config.list_kube_config_contexts.return_value = ([], None)

        api = AbstractAsyncCustomObjectApi(namespace=None)
        assert api._resolve_namespace_from_kubeconfig() == "default"

    @patch("jumpstarter_kubernetes.util.async_custom_object_api.config")
    def test_explicit_namespace_skips_resolution(self, mock_config):
        api = AbstractAsyncCustomObjectApi(namespace="explicit-ns")
        assert api.namespace == "explicit-ns"
        mock_config.list_kube_config_contexts.assert_not_called()

    @patch("jumpstarter_kubernetes.util.async_custom_object_api.config")
    def test_namespace_resolution_uses_specified_config_file(self, mock_config):
        mock_config.list_kube_config_contexts.return_value = (
            [{"name": "my-context", "context": {"namespace": "file-ns"}}],
            {"name": "my-context", "context": {"namespace": "file-ns"}},
        )

        api = AbstractAsyncCustomObjectApi(namespace=None, config_file="/path/to/kubeconfig")
        assert api._resolve_namespace_from_kubeconfig() == "file-ns"
        mock_config.list_kube_config_contexts.assert_called_once_with("/path/to/kubeconfig")
