"""Webhook handlers for n8n callbacks"""
from fastapi import APIRouter, Request, HTTPException, status
from typing import Dict, Any
import logging
from firebase_admin import firestore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/n8n")
async def n8n_webhook(request: Request):
    """
    Receive webhooks from n8n workflows.
    This endpoint is called by n8n workflows to notify the backend of events.
    """
    try:
        body = await request.json()
        event_type = body.get("event_type")
        data = body.get("data", {})

        logger.info(f"Received n8n webhook: {event_type}")

        db = firestore.client()

        # Handle different event types
        if event_type == "workflow_completed":
            workflow_id = data.get("workflow_id")
            execution_id = data.get("execution_id")
            result = data.get("result")

            # Store workflow result in Firestore
            if workflow_id and execution_id:
                db.collection("workflow_executions").document(execution_id).set({
                    "workflow_id": workflow_id,
                    "execution_id": execution_id,
                    "status": "completed",
                    "result": result,
                    "completed_at": firestore.SERVER_TIMESTAMP,
                })

        elif event_type == "workflow_failed":
            workflow_id = data.get("workflow_id")
            execution_id = data.get("execution_id")
            error = data.get("error")

            # Store workflow error
            if workflow_id and execution_id:
                db.collection("workflow_executions").document(execution_id).set({
                    "workflow_id": workflow_id,
                    "execution_id": execution_id,
                    "status": "failed",
                    "error": error,
                    "failed_at": firestore.SERVER_TIMESTAMP,
                }, merge=True)

        elif event_type == "project_created":
            # Handle project creation workflow completion
            project_id = data.get("project_id")
            user_id = data.get("user_id")

            if project_id and user_id:
                # Update project with workflow metadata
                db.collection("projects").document(project_id).update({
                    "workflow_status": "completed",
                    "workflow_completed_at": firestore.SERVER_TIMESTAMP,
                })

        elif event_type == "asset_processed":
            # Handle asset processing workflow completion
            project_id = data.get("project_id")
            asset_id = data.get("asset_id")
            processed_url = data.get("processed_url")

            if project_id and asset_id:
                # Update asset with processed URL
                db.collection("projects").document(project_id).collection("assets").document(asset_id).update({
                    "processed_url": processed_url,
                    "processing_status": "completed",
                    "processed_at": firestore.SERVER_TIMESTAMP,
                })

        return {"status": "ok", "message": "Webhook received"}

    except Exception as e:
        logger.error(f"Error processing n8n webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}",
        )


@router.post("/n8n/{workflow_id}")
async def n8n_workflow_webhook(workflow_id: str, request: Request):
    """
    Generic webhook endpoint for specific workflows.
    This allows n8n workflows to call back to the backend.
    """
    try:
        body = await request.json()
        logger.info(f"Received webhook for workflow {workflow_id}")

        # Store webhook data
        db = firestore.client()
        db.collection("webhook_logs").add({
            "workflow_id": workflow_id,
            "data": body,
            "received_at": firestore.SERVER_TIMESTAMP,
        })

        return {"status": "ok", "workflow_id": workflow_id}

    except Exception as e:
        logger.error(f"Error processing workflow webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}",
        )

