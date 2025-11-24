"""Projects router"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from api.models.project import ProjectCreate, ProjectUpdate, ProjectResponse
from api.services.project_service import ProjectService
from api.services.workflow_service import WorkflowService
from api.middleware.auth import get_current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new project"""
    user_id = current_user["uid"]
    project = await ProjectService.create_project(user_id, project_data)

    # Trigger n8n workflow for project creation (async, don't wait)
    try:
        # Convert datetime objects to ISO strings for JSON serialization
        import json
        from datetime import datetime
        
        project_dict = project.model_dump(mode='json')  # Use mode='json' to serialize datetimes
        
        # Additional cleanup for any remaining datetime-like objects
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, '_seconds'):  # Firestore Timestamp
                return datetime.fromtimestamp(obj._seconds).isoformat()
            elif hasattr(obj, 'isoformat'):  # Other datetime-like objects
                return obj.isoformat()
            return obj
        
        # Recursively serialize datetime objects
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(item) for item in d]
            else:
                return serialize_datetime(d)
        
        project_dict = clean_dict(project_dict)
        
        await WorkflowService.trigger_project_created_workflow(
            project_id=project.id,
            user_id=user_id,
            project_data=project_dict,
        )
    except Exception as e:
        # Log but don't fail the request if workflow trigger fails
        import logging
        logging.getLogger(__name__).warning(f"Failed to trigger project workflow: {e}")

    return project


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
):
    """List all projects for the current user"""
    user_id = current_user["uid"]
    projects = await ProjectService.list_projects(user_id, limit=limit)
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a project by ID"""
    user_id = current_user["uid"]
    project = await ProjectService.get_project(project_id, user_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update a project"""
    user_id = current_user["uid"]
    project = await ProjectService.update_project(project_id, user_id, project_data)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a project"""
    user_id = current_user["uid"]
    deleted = await ProjectService.delete_project(project_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return None

