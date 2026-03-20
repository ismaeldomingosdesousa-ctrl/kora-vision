"""Integration Worker Service - Syncs data from external services."""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import asyncio
from datetime import datetime, timedelta

from shared.config import settings
from shared.database import get_db, health_check

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
    logger.info("Starting Integration Worker Service...")
    db_healthy = await health_check()
    if not db_healthy:
        logger.error("Database health check failed on startup")
        raise RuntimeError("Database connection failed")

    # Start background sync task
    sync_task = asyncio.create_task(background_sync_loop())

    yield

    # Shutdown
    logger.info("Shutting down Integration Worker Service...")
    sync_task.cancel()
    try:
        await sync_task
    except asyncio.CancelledError:
        pass


# Create FastAPI application
app = FastAPI(
    title="Integration Worker",
    version=settings.APP_VERSION,
    description="Integration Worker Service for Unified Operations Hub",
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
        "service": "integration-worker",
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
# Integration Sync Endpoints
# ============================================================================

@app.post("/sync/{integration_id}", tags=["Sync"])
async def trigger_sync(
    integration_id: str,
    db = Depends(get_db),
):
    """Manually trigger integration sync."""

    try:
        logger.info(f"Triggering sync for integration {integration_id}")

        # TODO: Implement integration sync
        # - Get integration details from database
        # - Call appropriate connector
        # - Transform and store data
        # - Update sync status

        return {
            "integration_id": integration_id,
            "status": "sync_started",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error triggering sync: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger sync"
        )


@app.get("/sync/{integration_id}/status", tags=["Sync"])
async def get_sync_status(
    integration_id: str,
    db = Depends(get_db),
):
    """Get integration sync status."""

    try:
        # TODO: Implement status retrieval
        return {
            "integration_id": integration_id,
            "status": "idle",
            "last_sync_at": None,
            "next_sync_at": None,
        }

    except Exception as e:
        logger.error(f"Error getting sync status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get sync status"
        )


# ============================================================================
# Background Tasks
# ============================================================================

async def background_sync_loop():
    """Background loop for scheduled integration syncs."""

    logger.info("Starting background sync loop")

    while True:
        try:
            # TODO: Implement scheduled sync logic
            # - Query integrations with next_sync_at <= now
            # - Trigger sync for each
            # - Update next_sync_at based on sync_interval_minutes

            await asyncio.sleep(60)  # Check every minute

        except asyncio.CancelledError:
            logger.info("Background sync loop cancelled")
            break
        except Exception as e:
            logger.error(f"Error in background sync loop: {e}", exc_info=True)
            await asyncio.sleep(60)


# ============================================================================
# Connector Endpoints (for testing)
# ============================================================================

@app.get("/connectors", tags=["Connectors"])
async def list_connectors():
    """List available connectors."""

    return {
        "connectors": [
            {
                "type": "google_calendar",
                "name": "Google Calendar",
                "description": "Sync events from Google Calendar",
            },
            {
                "type": "jira",
                "name": "Jira",
                "description": "Sync issues from Jira",
            },
            {
                "type": "datadog",
                "name": "Datadog",
                "description": "Fetch metrics from Datadog",
            },
            {
                "type": "dynatrace",
                "name": "Dynatrace",
                "description": "Fetch metrics from Dynatrace",
            },
        ]
    }


@app.post("/connectors/{connector_type}/test", tags=["Connectors"])
async def test_connector(
    connector_type: str,
    credentials: dict,
):
    """Test connector with provided credentials."""

    try:
        logger.info(f"Testing connector: {connector_type}")

        # TODO: Implement connector testing
        # - Validate credentials
        # - Make test API call
        # - Return success/failure

        return {
            "connector_type": connector_type,
            "status": "ok",
            "message": "Connector test successful",
        }

    except Exception as e:
        logger.error(f"Error testing connector: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Connector test failed"
        )


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
