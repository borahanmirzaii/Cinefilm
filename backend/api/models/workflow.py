"""Workflow models"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class WorkflowExecutionRequest(BaseModel):
    """Request to execute a workflow"""
    workflow_id: str
    data: Optional[Dict[str, Any]] = None


class WorkflowWebhookRequest(BaseModel):
    """Request to trigger a webhook workflow"""
    webhook_path: str
    data: Optional[Dict[str, Any]] = None


class WorkflowExecutionResponse(BaseModel):
    """Workflow execution response"""
    execution_id: str
    status: str
    workflow_id: str
    data: Optional[Dict[str, Any]] = None

