"""Agent API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from pydantic import BaseModel
from api.middleware.auth import get_current_user
from api.agents.concept_agent import ConceptAgent
from api.agents.script_agent import ScriptAgent
from api.agents.preproduction_agent import PreProductionAgent
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["agents"])


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    project_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    session_id: Optional[str] = None
    agent: str
    artifact_id: Optional[str] = None


class ExecuteTaskRequest(BaseModel):
    """Task execution request"""
    task: str
    parameters: Optional[Dict[str, Any]] = None


# Agent instances (singletons)
_concept_agent: Optional[ConceptAgent] = None
_script_agent: Optional[ScriptAgent] = None
_preproduction_agent: Optional[PreProductionAgent] = None


def get_concept_agent() -> ConceptAgent:
    """Get concept agent singleton"""
    global _concept_agent
    if _concept_agent is None:
        _concept_agent = ConceptAgent()
    return _concept_agent


def get_script_agent() -> ScriptAgent:
    """Get script agent singleton"""
    global _script_agent
    if _script_agent is None:
        _script_agent = ScriptAgent()
    return _script_agent


def get_preproduction_agent() -> PreProductionAgent:
    """Get pre-production agent singleton"""
    global _preproduction_agent
    if _preproduction_agent is None:
        _preproduction_agent = PreProductionAgent()
    return _preproduction_agent


@router.post("/concept/chat", response_model=ChatResponse)
async def chat_with_concept_agent(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """Chat with concept stage agent"""
    try:
        agent = get_concept_agent()
        context = request.context or {}
        context["user_id"] = current_user["uid"]
        if request.project_id:
            context["project_id"] = request.project_id

        result = await agent.chat(request.message, context)
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Error in concept agent chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {str(e)}",
        )


@router.post("/script/chat", response_model=ChatResponse)
async def chat_with_script_agent(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """Chat with script stage agent"""
    try:
        agent = get_script_agent()
        context = request.context or {}
        context["user_id"] = current_user["uid"]
        if request.project_id:
            context["project_id"] = request.project_id

        result = await agent.chat(request.message, context)
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Error in script agent chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {str(e)}",
        )


@router.post("/preproduction/chat", response_model=ChatResponse)
async def chat_with_preproduction_agent(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """Chat with pre-production stage agent"""
    try:
        agent = get_preproduction_agent()
        context = request.context or {}
        context["user_id"] = current_user["uid"]
        if request.project_id:
            context["project_id"] = request.project_id

        result = await agent.chat(request.message, context)
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Error in pre-production agent chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {str(e)}",
        )


@router.post("/concept/execute")
async def execute_concept_task(
    request: ExecuteTaskRequest,
    current_user: dict = Depends(get_current_user),
):
    """Execute a concept agent task"""
    try:
        agent = get_concept_agent()

        if request.task == "suggest_logline":
            project_id = request.parameters.get("project_id") if request.parameters else None
            concept = request.parameters.get("concept") if request.parameters else ""
            if not project_id or not concept:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="project_id and concept are required",
                )
            return await agent.suggest_logline(project_id, concept)

        elif request.task == "brainstorm_themes":
            project_id = request.parameters.get("project_id") if request.parameters else None
            genre = request.parameters.get("genre") if request.parameters else None
            if not project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="project_id is required",
                )
            return await agent.brainstorm_themes(project_id, genre)

        else:
            return await agent.execute_task(request.task, request.parameters)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing concept task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task execution error: {str(e)}",
        )


@router.get("/{stage}/sessions")
async def list_agent_sessions(
    stage: str,
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """List agent sessions for a stage"""
    from firebase_admin import firestore

    try:
        db = firestore.client()
        user_id = current_user["uid"]

        if project_id:
            # Verify project belongs to user
            project_doc = db.collection("projects").document(project_id).get()
            if not project_doc.exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found",
                )
            project_data = project_doc.to_dict()
            if project_data.get("userId") != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied",
                )

            # Get sessions for this project
            sessions_ref = (
                db.collection("projects")
                .document(project_id)
                .collection("agent_sessions")
            )
        else:
            # Get all sessions for user's projects
            projects_ref = db.collection("projects").where("userId", "==", user_id)
            sessions = []
            for project_doc in projects_ref.stream():
                project_sessions_ref = (
                    db.collection("projects")
                    .document(project_doc.id)
                    .collection("agent_sessions")
                )
                for session_doc in project_sessions_ref.where("stage", "==", stage).stream():
                    session_data = session_doc.to_dict()
                    session_data["id"] = session_doc.id
                    session_data["project_id"] = project_doc.id
                    sessions.append(session_data)
            return {"sessions": sessions, "stage": stage}

        # Filter by stage if project_id provided
        query = sessions_ref
        if stage:
            query = query.where("stage", "==", stage)

        sessions = []
        for doc in query.order_by("created_at", direction=firestore.Query.DESCENDING).limit(50).stream():
            session_data = doc.to_dict()
            session_data["id"] = doc.id
            sessions.append(session_data)

        return {"sessions": sessions, "stage": stage}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing sessions: {str(e)}",
        )


@router.get("/{stage}/artifacts")
async def list_agent_artifacts(
    stage: str,
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    """List agent artifacts for a project"""
    from firebase_admin import firestore

    try:
        db = firestore.client()
        artifacts_ref = (
            db.collection("projects")
            .document(project_id)
            .collection("artifacts")
        )

        artifacts = []
        for doc in artifacts_ref.stream():
            artifact_data = doc.to_dict()
            artifact_data["id"] = doc.id
            artifacts.append(artifact_data)

        return {"artifacts": artifacts, "stage": stage, "project_id": project_id}
    except Exception as e:
        logger.error(f"Error listing artifacts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing artifacts: {str(e)}",
        )

