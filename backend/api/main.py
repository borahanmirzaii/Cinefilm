"""FastAPI application entry point"""
# Initialize Firebase FIRST before any other imports that use it
from api.middleware.auth import init_firebase

init_firebase()

# Now import everything else
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from api.routers import health, projects
from api.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cinefilm Platform API",
    description="Backend API for Cinefilm Platform",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list if settings.environment == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware (before cache middleware)
from api.middleware.rate_limit import RateLimitMiddleware, DEFAULT_ENDPOINT_LIMITS
app.add_middleware(
    RateLimitMiddleware,
    endpoint_limits=DEFAULT_ENDPOINT_LIMITS,
)

# Cache middleware (after rate limiting)
from api.middleware.cache import CacheMiddleware
app.add_middleware(
    CacheMiddleware,
    cache_paths=["/api/projects"],  # Cache project endpoints
    ttl=300,  # 5 minutes for project data
)


# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    if settings.debug:
        import traceback
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "traceback": traceback.format_exc(),
            },
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Include routers
app.include_router(health.router)
app.include_router(projects.router)

# Include webhook router
from api.routers import webhooks
app.include_router(webhooks.router)

# Include agents router
from api.routers import agents
app.include_router(agents.router)

# Include admin router
from api.routers import admin
app.include_router(admin.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Cinefilm Platform API",
        "version": "0.1.0",
        "environment": settings.environment,
    }

