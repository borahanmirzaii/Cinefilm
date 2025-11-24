"""Firestore tools for agents"""
from firebase_admin import firestore
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


def search_firestore(collection: str, filters: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search Firestore collection with filters.

    Args:
        collection: Collection name
        filters: Filter dictionary (field: value)
        limit: Maximum results

    Returns:
        List of documents
    """
    try:
        db = firestore.client()
        query = db.collection(collection)

        # Apply filters
        for field, value in filters.items():
            query = query.where(field, "==", value)

        # Execute query
        results = []
        for doc in query.limit(limit).stream():
            doc_data = doc.to_dict()
            doc_data["id"] = doc.id
            results.append(doc_data)

        return results
    except Exception as e:
        logger.error(f"Firestore search error: {e}")
        return []


def get_project_data(project_id: str) -> Optional[Dict[str, Any]]:
    """Get project data by ID"""
    try:
        db = firestore.client()
        doc = db.collection("projects").document(project_id).get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        return None
    except Exception as e:
        logger.error(f"Error getting project data: {e}")
        return None


def create_project_artifact(
    project_id: str, artifact_type: str, content: Dict[str, Any]
) -> str:
    """
    Create an artifact in Firestore.

    Args:
        project_id: Project ID
        artifact_type: Type of artifact (e.g., "logline", "script_analysis")
        content: Artifact content

    Returns:
        Artifact ID
    """
    try:
        db = firestore.client()
        artifact_data = {
            "project_id": project_id,
            "type": artifact_type,
            "content": content,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        doc_ref = db.collection("projects").document(project_id).collection("artifacts").add(
            artifact_data
        )
        return doc_ref[1].id
    except Exception as e:
        logger.error(f"Error creating artifact: {e}")
        raise

