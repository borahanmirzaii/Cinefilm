"""Firebase Authentication middleware"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth, credentials
import os
import logging
from api.config import settings

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
def init_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        cred_path = settings.google_application_credentials
        if cred_path and os.path.exists(cred_path):
            logger.info(f"Initializing Firebase Admin SDK with credentials file: {cred_path}")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                "projectId": settings.firebase_project_id,
            })
        else:
            # Use default credentials (for Cloud Run or local with gcloud auth)
            logger.info("Initializing Firebase Admin SDK with default credentials")
            try:
                # Explicitly set project ID when using default credentials
                firebase_admin.initialize_app(options={
                    "projectId": settings.firebase_project_id,
                })
                logger.info(f"Firebase Admin SDK initialized successfully with project ID: {settings.firebase_project_id}")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
                raise
    else:
        logger.info("Firebase Admin SDK already initialized")


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
        logger.warning("Authorization header missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    try:
        # Extract token from "Bearer <token>"
        token = authorization.split(" ")[1] if " " in authorization else authorization
        logger.debug(f"Verifying token (first 20 chars): {token[:20]}...")
        decoded_token = auth.verify_id_token(token)
        logger.debug(f"Token verified successfully for user: {decoded_token.get('uid')}")
        return decoded_token
    except Exception as e:
        logger.error(f"Token verification failed: {type(e).__name__}: {str(e)}")
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

