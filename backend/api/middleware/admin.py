"""Admin middleware for protecting admin routes"""
from fastapi import Request, HTTPException, status
from firebase_admin import firestore
from api.middleware.auth import get_current_user
import logging

logger = logging.getLogger(__name__)


async def require_admin(request: Request) -> dict:
    """
    Dependency to ensure user is an admin.
    Checks Firestore user document for 'admin' role.
    """
    # Get current user
    current_user = await get_current_user(request)
    user_id = current_user["uid"]

    # Check if user is admin
    try:
        db = firestore.client()
        user_doc = db.collection("users").document(user_id).get()

        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not found",
            )

        user_data = user_doc.to_dict()
        is_admin = user_data.get("role") == "admin" or user_data.get("isAdmin") == True

        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        return current_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying admin access",
        )

