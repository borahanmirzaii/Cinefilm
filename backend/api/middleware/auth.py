"""Firebase Authentication middleware"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth, credentials
import os
from api.config import settings


# Initialize Firebase Admin SDK
def init_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        cred_path = settings.google_application_credentials
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Use default credentials (for Cloud Run or local with gcloud auth)
            firebase_admin.initialize_app()


# Initialize on import
init_firebase()


security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials) -> dict:
    """
    Verify Firebase ID token and return decoded token
    """
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
        )


async def get_current_user(request: Request) -> dict:
    """
    Dependency to get current authenticated user from request
    """
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    try:
        # Extract token from "Bearer <token>"
        token = authorization.split(" ")[1] if " " in authorization else authorization
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
        )


def get_user_id(request: Request) -> str:
    """
    Extract user ID from request state (set by auth middleware)
    """
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
        )
    return request.state.user_id

