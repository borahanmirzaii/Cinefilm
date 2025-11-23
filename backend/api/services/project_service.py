"""Project service layer"""
from firebase_admin import firestore
from typing import List, Optional
from datetime import datetime
from api.models.project import ProjectCreate, ProjectUpdate, ProjectResponse


def get_db():
    """Get Firestore client (lazy initialization)"""
    return firestore.client()


class ProjectService:
    """Service for project operations"""

    @staticmethod
    async def create_project(user_id: str, project_data: ProjectCreate) -> ProjectResponse:
        """Create a new project"""
        db = get_db()
        project_dict = project_data.model_dump()
        project_dict["userId"] = user_id
        project_dict["createdAt"] = datetime.utcnow()
        project_dict["updatedAt"] = datetime.utcnow()

        # Add to Firestore
        doc_ref = db.collection("projects").add(project_dict)
        project_id = doc_ref[1].id

        # Retrieve created project
        project_doc = db.collection("projects").document(project_id).get()
        project_dict = project_doc.to_dict()
        project_dict["id"] = project_id

        return ProjectResponse(**project_dict)

    @staticmethod
    async def get_project(project_id: str, user_id: str) -> Optional[ProjectResponse]:
        """Get a project by ID"""
        db = get_db()
        project_doc = db.collection("projects").document(project_id).get()

        if not project_doc.exists:
            return None

        project_dict = project_doc.to_dict()
        if project_dict.get("userId") != user_id:
            return None

        project_dict["id"] = project_id
        return ProjectResponse(**project_dict)

    @staticmethod
    async def list_projects(user_id: str, limit: int = 50) -> List[ProjectResponse]:
        """List all projects for a user"""
        db = get_db()
        projects_ref = db.collection("projects")
        query = projects_ref.where("userId", "==", user_id).limit(limit).order_by("createdAt", direction=firestore.Query.DESCENDING)

        projects = []
        for doc in query.stream():
            project_dict = doc.to_dict()
            project_dict["id"] = doc.id
            projects.append(ProjectResponse(**project_dict))

        return projects

    @staticmethod
    async def update_project(
        project_id: str, user_id: str, project_data: ProjectUpdate
    ) -> Optional[ProjectResponse]:
        """Update a project"""
        db = get_db()
        project_doc = db.collection("projects").document(project_id).get()

        if not project_doc.exists:
            return None

        project_dict = project_doc.to_dict()
        if project_dict.get("userId") != user_id:
            return None

        # Update fields
        update_data = project_data.model_dump(exclude_unset=True)
        update_data["updatedAt"] = datetime.utcnow()

        db.collection("projects").document(project_id).update(update_data)

        # Retrieve updated project
        updated_doc = db.collection("projects").document(project_id).get()
        updated_dict = updated_doc.to_dict()
        updated_dict["id"] = project_id

        return ProjectResponse(**updated_dict)

    @staticmethod
    async def delete_project(project_id: str, user_id: str) -> bool:
        """Delete a project"""
        db = get_db()
        project_doc = db.collection("projects").document(project_id).get()

        if not project_doc.exists:
            return False

        project_dict = project_doc.to_dict()
        if project_dict.get("userId") != user_id:
            return False

        db.collection("projects").document(project_id).delete()
        return True

