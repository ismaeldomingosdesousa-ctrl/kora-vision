"""Core API Service - Main application."""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from shared.config import settings
from shared.database import get_db, health_check
from shared.auth import get_current_user

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""

    # Startup
    logger.info("Starting Core API Service...")
    db_healthy = await health_check()
    if not db_healthy:
        logger.error("Database health check failed on startup")
        raise RuntimeError("Database connection failed")

    yield

    # Shutdown
    logger.info("Shutting down Core API Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Core API Service for Unified Operations Hub",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint."""

    db_healthy = await health_check()

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": "core-api",
        "version": settings.APP_VERSION,
        "database": "ok" if db_healthy else "error",
    }


@app.get("/ready", tags=["Health"])
async def readiness():
    """Readiness check endpoint."""

    db_healthy = await health_check()

    if not db_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )

    return {"status": "ready"}


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/auth/token", tags=["Auth"])
async def login(email: str, password: str):
    """Login endpoint (placeholder - integrate with Cognito)."""

    # TODO: Implement Cognito authentication
    return {
        "access_token": "placeholder-token",
        "token_type": "bearer",
    }


@app.get("/auth/me", tags=["Auth"])
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current authenticated user."""

    return {
        "id": str(current_user.id),
        "tenant_id": str(current_user.tenant_id),
        "email": current_user.email,
        "role": current_user.role,
    }


# ============================================================================
# Tenant Endpoints
# ============================================================================

@app.get("/tenants", tags=["Tenants"])
async def list_tenants(
    skip: int = 0,
    limit: int = 10,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """List tenants (admin only)."""

    # TODO: Implement tenant listing with proper authorization
    return {
        "total": 0,
        "items": []
    }


@app.get("/tenants/{tenant_id}", tags=["Tenants"])
async def get_tenant(
    tenant_id: str,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get tenant details."""

    # TODO: Implement tenant retrieval with RLS
    return {
        "id": tenant_id,
        "name": "Tenant Name",
        "slug": "tenant-slug",
    }


# ============================================================================
# User Endpoints
# ============================================================================

@app.get("/users", tags=["Users"])
async def list_users(
    skip: int = 0,
    limit: int = 10,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """List users in tenant."""

    # TODO: Implement user listing with RLS
    return {
        "total": 0,
        "items": []
    }


@app.post("/users", tags=["Users"])
async def create_user(
    email: str,
    first_name: str,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Create new user."""

    # TODO: Implement user creation
    return {
        "id": "user-id",
        "email": email,
        "first_name": first_name,
    }


# ============================================================================
# Dashboard Endpoints
# ============================================================================

@app.get("/dashboards", tags=["Dashboards"])
async def list_dashboards(
    skip: int = 0,
    limit: int = 10,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """List dashboards."""

    # TODO: Implement dashboard listing with RLS
    return {
        "total": 0,
        "items": []
    }


@app.post("/dashboards", tags=["Dashboards"])
async def create_dashboard(
    name: str,
    description: str = None,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Create new dashboard."""

    # TODO: Implement dashboard creation
    return {
        "id": "dashboard-id",
        "name": name,
        "description": description,
    }


@app.get("/dashboards/{dashboard_id}", tags=["Dashboards"])
async def get_dashboard(
    dashboard_id: str,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get dashboard details."""

    # TODO: Implement dashboard retrieval with RLS
    return {
        "id": dashboard_id,
        "name": "Dashboard Name",
    }


# ============================================================================
# Integration Endpoints
# ============================================================================

@app.get("/integrations", tags=["Integrations"])
async def list_integrations(
    skip: int = 0,
    limit: int = 10,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """List integrations."""

    # TODO: Implement integration listing with RLS
    return {
        "total": 0,
        "items": []
    }


@app.post("/integrations", tags=["Integrations"])
async def create_integration(
    connector_type: str,
    name: str,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Create new integration."""

    # TODO: Implement integration creation
    return {
        "id": "integration-id",
        "connector_type": connector_type,
        "name": name,
        "status": "pending",
    }


# ============================================================================
# Webhook Endpoints
# ============================================================================

@app.post("/webhooks/register", tags=["Webhooks"])
async def register_webhook(
    integration_id: str,
    webhook_url: str,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Register webhook for integration."""

    # TODO: Implement webhook registration
    return {
        "webhook_id": "webhook-id",
        "integration_id": integration_id,
        "webhook_url": webhook_url,
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""

    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": 500,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
    )
