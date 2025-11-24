"""Health check router"""
from fastapi import APIRouter
from api.lib.redis import is_redis_available

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    redis_status = is_redis_available()
    return {
        "status": "healthy",
        "redis": "available" if redis_status else "unavailable",
    }

