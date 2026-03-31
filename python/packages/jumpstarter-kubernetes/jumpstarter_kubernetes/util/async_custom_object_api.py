import base64
import logging
from contextlib import AbstractAsyncContextManager
from typing import Optional, Self

from kubernetes_asyncio import config
from kubernetes_asyncio.client.api import CoreV1Api, CustomObjectsApi
from kubernetes_asyncio.client.api_client import ApiClient
from kubernetes_asyncio.client.exceptions import ApiException

logger = logging.getLogger(__name__)

# Fixed ConfigMap name for CA certificate bundle
CA_CONFIGMAP_NAME = "jumpstarter-service-ca-cert"


class AbstractAsyncCustomObjectApi(AbstractAsyncContextManager):
    """An abstract async custom object API client"""

    _client: ApiClient
    config_file: Optional[str]
    context: Optional[str]
    namespace: Optional[str]
    api: CustomObjectsApi
    core_api: CoreV1Api

    def __init__(
        self,
        namespace: Optional[str] = None,
        config_file: Optional[str] = None,
        context: Optional[str] = None,
    ):
        self.config_file = config_file
        self.context = context
        self.namespace = namespace

    async def __aenter__(self) -> Self:
        # Load the kubeconfig
        await self._load_kube_config()
        # Resolve namespace from kubeconfig context if not explicitly provided
        if self.namespace is None:
            self.namespace = self._resolve_namespace_from_kubeconfig()
        # Construct the API client and enter context
        self._client = ApiClient()
        await self._client.__aenter__()
        # Construct the custom objects API client
        self.api = CustomObjectsApi(self._client)
        self.core_api = CoreV1Api(self._client)
        return self

    def _resolve_namespace_from_kubeconfig(self) -> str:
        try:
            _, current_context = config.list_kube_config_contexts(self.config_file)
            if current_context and "context" in current_context:
                namespace = current_context["context"].get("namespace")
                if namespace:
                    return namespace
        except Exception:
            logger.debug("Failed to read namespace from kubeconfig, falling back to 'default'")
        return "default"

    async def _load_kube_config(self):
        await config.load_kube_config(self.config_file, self.context)

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._client.__aexit__(exc_type, exc_value, traceback)
        self._client = None
        self.api = None
        self.core_api = None
        return None

    async def get_ca_bundle(self) -> str:
        """Get the CA certificate bundle from the jumpstarter-service-ca-cert ConfigMap.

        Returns the CA certificate as a base64-encoded string suitable for use in TLS config.
        Returns an empty string if the ConfigMap doesn't exist or has no CA certificate.
        """
        try:
            configmap = await self.core_api.read_namespaced_config_map(CA_CONFIGMAP_NAME, self.namespace)
            ca_crt = configmap.data.get("ca.crt", "") if configmap.data else ""
            if ca_crt:
                # Base64 encode the CA certificate for use in TLS config
                return base64.b64encode(ca_crt.encode("utf-8")).decode("utf-8")
            return ""
        except ApiException as e:
            if e.status == 404:
                logger.debug(f"CA ConfigMap {CA_CONFIGMAP_NAME} not found in namespace {self.namespace}")
                return ""
            raise
