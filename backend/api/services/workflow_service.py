"""Workflow orchestration service"""
from typing import Optional, Dict, Any
import logging
from api.lib.n8n import get_n8n_client
from api.models.workflow import WorkflowExecutionRequest, WorkflowExecutionResponse

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for orchestrating n8n workflows"""

    @staticmethod
    async def trigger_project_created_workflow(
        project_id: str, user_id: str, project_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Trigger workflow when a project is created.

        Args:
            project_id: Project ID
            user_id: User ID
            project_data: Project data

        Returns:
            Execution ID if workflow was triggered
        """
        try:
            n8n_client = get_n8n_client()

            # Try to trigger webhook workflow
            webhook_data = {
                "project_id": project_id,
                "user_id": user_id,
                "project": project_data,
                "event": "project_created",
            }

            # Try webhook path first (more common in n8n)
            try:
                result = await n8n_client.trigger_webhook("project-created", webhook_data)
                logger.info(f"Triggered project-created webhook for project {project_id}")
                return result.get("execution_id")
            except Exception:
                # Fallback: try to find and execute workflow by name
                workflows = await n8n_client.get_workflows()
                workflow = next(
                    (w for w in workflows if "project" in w.get("name", "").lower() and "created" in w.get("name", "").lower()),
                    None
                )
                if workflow:
                    result = await n8n_client.execute_workflow(workflow["id"], webhook_data)
                    logger.info(f"Executed project-created workflow for project {project_id}")
                    return result.get("execution_id")

        except Exception as e:
            logger.warning(f"Failed to trigger project-created workflow: {e}")
            # Don't fail the request if workflow trigger fails

        return None

    @staticmethod
    async def trigger_asset_upload_workflow(
        project_id: str, asset_id: str, asset_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Trigger workflow when an asset is uploaded.

        Args:
            project_id: Project ID
            asset_id: Asset ID
            asset_data: Asset data

        Returns:
            Execution ID if workflow was triggered
        """
        try:
            n8n_client = get_n8n_client()

            webhook_data = {
                "project_id": project_id,
                "asset_id": asset_id,
                "asset": asset_data,
                "event": "asset_uploaded",
            }

            try:
                result = await n8n_client.trigger_webhook("asset-uploaded", webhook_data)
                logger.info(f"Triggered asset-uploaded webhook for asset {asset_id}")
                return result.get("execution_id")
            except Exception:
                workflows = await n8n_client.get_workflows()
                workflow = next(
                    (w for w in workflows if "asset" in w.get("name", "").lower() and "upload" in w.get("name", "").lower()),
                    None
                )
                if workflow:
                    result = await n8n_client.execute_workflow(workflow["id"], webhook_data)
                    logger.info(f"Executed asset-uploaded workflow for asset {asset_id}")
                    return result.get("execution_id")

        except Exception as e:
            logger.warning(f"Failed to trigger asset-uploaded workflow: {e}")

        return None

    @staticmethod
    async def trigger_ai_generation_workflow(
        project_id: str, user_id: str, generation_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Trigger workflow for AI generation tasks.

        Args:
            project_id: Project ID
            user_id: User ID
            generation_data: Generation request data

        Returns:
            Execution ID if workflow was triggered
        """
        try:
            n8n_client = get_n8n_client()

            webhook_data = {
                "project_id": project_id,
                "user_id": user_id,
                "generation": generation_data,
                "event": "ai_generation",
            }

            try:
                result = await n8n_client.trigger_webhook("ai-generation", webhook_data)
                logger.info(f"Triggered ai-generation webhook for project {project_id}")
                return result.get("execution_id")
            except Exception:
                workflows = await n8n_client.get_workflows()
                workflow = next(
                    (w for w in workflows if "ai" in w.get("name", "").lower() or "generation" in w.get("name", "").lower()),
                    None
                )
                if workflow:
                    result = await n8n_client.execute_workflow(workflow["id"], webhook_data)
                    logger.info(f"Executed ai-generation workflow for project {project_id}")
                    return result.get("execution_id")

        except Exception as e:
            logger.warning(f"Failed to trigger ai-generation workflow: {e}")

        return None

    @staticmethod
    async def execute_workflow(
        request: WorkflowExecutionRequest,
    ) -> WorkflowExecutionResponse:
        """
        Execute a workflow by ID.

        Args:
            request: Workflow execution request

        Returns:
            Workflow execution response
        """
        n8n_client = get_n8n_client()
        result = await n8n_client.execute_workflow(
            request.workflow_id, request.data
        )

        return WorkflowExecutionResponse(
            execution_id=result.get("execution_id", ""),
            status=result.get("status", "running"),
            workflow_id=request.workflow_id,
            data=result,
        )

