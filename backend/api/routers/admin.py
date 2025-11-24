"""Admin API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from api.middleware.admin import require_admin
from api.middleware.auth import get_current_user
from api.lib.redis import is_redis_available
from api.lib.n8n import get_n8n_client
from firebase_admin import firestore
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
async def get_admin_stats(admin_user: dict = Depends(require_admin)):
    """Get admin dashboard statistics"""
    try:
        db = firestore.client()

        # Get user statistics
        users_ref = db.collection("users")
        total_users = len(list(users_ref.stream()))

        # Count active users (users with recent activity - last 30 days)
        # This is a simplified version - in production, track last_active timestamp
        active_users = total_users  # Placeholder

        # Get project statistics
        projects_ref = db.collection("projects")
        total_projects = len(list(projects_ref.stream()))

        # Get usage statistics
        usage_ref = db.collection_group("usage")
        total_api_calls = len(list(usage_ref.limit(1000).stream()))  # Approximate

        # System health
        redis_status = is_redis_available()
        n8n_client = get_n8n_client()
        n8n_status = await n8n_client.health_check() if n8n_client else False

        return {
            "users": {
                "total": total_users,
                "active": active_users,
            },
            "projects": {
                "total": total_projects,
            },
            "usage": {
                "api_calls": total_api_calls,
            },
            "system": {
                "redis": "available" if redis_status else "unavailable",
                "n8n": "available" if n8n_status else "unavailable",
            },
        }
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching statistics: {str(e)}",
        )


@router.get("/users")
async def list_users(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    admin_user: dict = Depends(require_admin),
):
    """List all users"""
    try:
        db = firestore.client()
        users_ref = db.collection("users")
        users = []

        # Get users with pagination
        for doc in users_ref.limit(limit).offset(offset).stream():
            user_data = doc.to_dict()
            user_data["id"] = doc.id
            # Don't expose sensitive data
            user_data.pop("password", None)
            users.append(user_data)

        return {"users": users, "total": len(users)}
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing users: {str(e)}",
        )


@router.get("/users/{user_id}")
async def get_user(user_id: str, admin_user: dict = Depends(require_admin)):
    """Get user details"""
    try:
        db = firestore.client()
        user_doc = db.collection("users").document(user_id).get()

        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user_data = user_doc.to_dict()
        user_data["id"] = user_doc.id
        user_data.pop("password", None)

        # Get user's projects count
        projects_ref = db.collection("projects").where("userId", "==", user_id)
        user_data["project_count"] = len(list(projects_ref.stream()))

        return user_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user: {str(e)}",
        )


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    updates: Dict[str, Any],
    admin_user: dict = Depends(require_admin),
):
    """Update user (admin override)"""
    try:
        db = firestore.client()
        user_doc = db.collection("users").document(user_id).get()

        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Don't allow updating password or sensitive fields via this endpoint
        updates.pop("password", None)
        updates.pop("email", None)  # Email changes should go through auth

        db.collection("users").document(user_id).update(updates)

        # Get updated user
        updated_doc = db.collection("users").document(user_id).get()
        user_data = updated_doc.to_dict()
        user_data["id"] = updated_doc.id

        return user_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}",
        )


@router.get("/projects")
async def list_all_projects(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    admin_user: dict = Depends(require_admin),
):
    """List all projects across all users"""
    try:
        db = firestore.client()
        projects_ref = db.collection("projects")
        projects = []

        for doc in projects_ref.limit(limit).offset(offset).order_by("createdAt", direction=firestore.Query.DESCENDING).stream():
            project_data = doc.to_dict()
            project_data["id"] = doc.id
            projects.append(project_data)

        return {"projects": projects, "total": len(projects)}
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing projects: {str(e)}",
        )


@router.get("/workflows")
async def list_workflows(admin_user: dict = Depends(require_admin)):
    """List n8n workflows"""
    try:
        n8n_client = get_n8n_client()
        workflows = await n8n_client.get_workflows()
        return {"workflows": workflows}
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing workflows: {str(e)}",
        )


@router.get("/agents/sessions")
async def list_agent_sessions(
    project_id: Optional[str] = None,
    stage: Optional[str] = None,
    admin_user: dict = Depends(require_admin),
):
    """List agent sessions"""
    try:
        db = firestore.client()

        if project_id:
            # Get sessions for specific project
            sessions_ref = (
                db.collection("projects")
                .document(project_id)
                .collection("agent_sessions")
            )
        else:
            # Get all sessions (this might be expensive - consider pagination)
            sessions_ref = db.collection_group("agent_sessions")

        sessions = []
        query = sessions_ref
        if stage:
            query = query.where("stage", "==", stage)

        for doc in query.limit(100).stream():
            session_data = doc.to_dict()
            session_data["id"] = doc.id
            sessions.append(session_data)

        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Error listing agent sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing sessions: {str(e)}",
        )

