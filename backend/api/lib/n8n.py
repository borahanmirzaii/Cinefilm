"""n8n client wrapper for API communication"""
import httpx
from typing import Optional, Dict, Any, List
import logging
from api.config import settings

logger = logging.getLogger(__name__)


class N8nClient:
    """Client for interacting with n8n API"""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize n8n client.

        Args:
            base_url: n8n base URL (defaults to N8N_URL from config or http://n8n:5678)
            api_key: n8n API key for authentication (optional, can use basic auth)
        """
        self.base_url = base_url or getattr(settings, "n8n_url", "http://n8n:5678")
        self.api_key = api_key or getattr(settings, "n8n_api_key", None)
        self.timeout = 30.0

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-N8N-API-KEY"] = self.api_key
        return headers

    async def _request(
        self, method: str, endpoint: str, **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Make HTTP request to n8n API"""
        url = f"{self.base_url}{endpoint}"
        headers = {**self._get_headers(), **kwargs.pop("headers", {})}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                return response.json() if response.content else None
        except httpx.HTTPError as e:
            logger.error(f"n8n API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling n8n: {e}")
            raise

    async def get_workflows(self) -> List[Dict[str, Any]]:
        """Get list of all workflows"""
        return await self._request("GET", "/api/v1/workflows") or []

    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by ID"""
        return await self._request("GET", f"/api/v1/workflows/{workflow_id}")

    async def execute_workflow(
        self, workflow_id: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow by ID.

        Args:
            workflow_id: Workflow ID
            data: Input data for the workflow

        Returns:
            Workflow execution result
        """
        endpoint = f"/webhook/{workflow_id}"
        if data:
            return await self._request("POST", endpoint, json=data) or {}
        return await self._request("POST", endpoint) or {}

    async def trigger_webhook(
        self, webhook_path: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Trigger a webhook workflow.

        Args:
            webhook_path: Webhook path (e.g., "project-created")
            data: Webhook payload

        Returns:
            Webhook response
        """
        endpoint = f"/webhook/{webhook_path}"
        if data:
            return await self._request("POST", endpoint, json=data) or {}
        return await self._request("POST", endpoint) or {}

    async def get_executions(
        self, workflow_id: Optional[str] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get workflow executions.

        Args:
            workflow_id: Filter by workflow ID (optional)
            limit: Maximum number of executions to return

        Returns:
            List of executions
        """
        endpoint = f"/api/v1/executions?limit={limit}"
        if workflow_id:
            endpoint += f"&workflowId={workflow_id}"
        return await self._request("GET", endpoint) or []

    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution by ID"""
        return await self._request("GET", f"/api/v1/executions/{execution_id}")

    async def health_check(self) -> bool:
        """Check if n8n is available"""
        try:
            # Try to access n8n health endpoint or workflows list
            await self._request("GET", "/api/v1/workflows", timeout=5.0)
            return True
        except Exception:
            return False


# Singleton instance
_n8n_client: Optional[N8nClient] = None


def get_n8n_client() -> N8nClient:
    """Get n8n client singleton"""
    global _n8n_client
    if _n8n_client is None:
        _n8n_client = N8nClient()
    return _n8n_client

