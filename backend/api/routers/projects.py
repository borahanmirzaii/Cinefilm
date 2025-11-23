"""Projects router"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from api.models.project import ProjectCreate, ProjectUpdate, ProjectResponse
from api.services.project_service import ProjectService
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

