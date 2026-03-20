"""Webhook Ingestor Service - Receives and processes webhooks."""

from fastapi import FastAPI, Request, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import hmac
import hashlib
from uuid import uuid4
from datetime import datetime

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
    logger.info("Starting Webhook Ingestor Service...")
    db_healthy = await health_check()
    if not db_healthy:
        logger.error("Database health check failed on startup")
        raise RuntimeError("Database connection failed")

    yield

    # Shutdown
    logger.info("Shutting down Webhook Ingestor Service...")


# Create FastAPI application
app = FastAPI(
    title="Webhook Ingestor",
    version=settings.APP_VERSION,
    description="Webhook Ingestor Service for Unified Operations Hub",
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
        "service": "webhook-ingestor",
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
# Webhook Endpoints
# ============================================================================

def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """Verify webhook signature using HMAC-SHA256."""

    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


async def process_webhook(
    webhook_data: dict,
    tenant_id: str,
    integration_id: str,
    db = None,
):
    """Process webhook in background."""

    try:
        logger.info(f"Processing webhook for tenant {tenant_id}, integration {integration_id}")

        # TODO: Implement webhook processing
        # - Validate webhook data
        # - Store in events table
        # - Publish to SQS/EventBridge
        # - Update integration status if needed

        logger.info(f"Webhook processed successfully")

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)


@app.post("/webhooks/{tenant_id}/{integration_id}", tags=["Webhooks"])
async def receive_webhook(
    tenant_id: str,
    integration_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db = None,
):
    """Receive webhook from external service."""

    try:
        # Get request body
        body = await request.body()

        # Get headers
        signature = request.headers.get("X-Webhook-Signature")
        timestamp = request.headers.get("X-Webhook-Timestamp")
        content_type = request.headers.get("Content-Type", "application/json")

        # Validate signature (TODO: get secret from database)
        # if not verify_webhook_signature(body, signature, webhook_secret):
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Invalid webhook signature"
        #     )

        # Parse JSON
        try:
            webhook_data = await request.json()
        except Exception as e:
            logger.error(f"Failed to parse webhook JSON: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )

        # Generate webhook ID
        webhook_id = str(uuid4())

        logger.info(
            f"Received webhook: {webhook_id} for tenant {tenant_id}, "
            f"integration {integration_id}"
        )

        # Process webhook in background
        background_tasks.add_task(
            process_webhook,
            webhook_data,
            tenant_id,
            integration_id,
            db,
        )

        # Return immediate acknowledgment
        return {
            "webhook_id": webhook_id,
            "status": "received",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error receiving webhook: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )


@app.post("/webhooks/test", tags=["Webhooks"])
async def test_webhook(request: Request):
    """Test webhook endpoint for integration testing."""

    body = await request.body()
    logger.info(f"Test webhook received: {body}")

    return {
        "status": "ok",
        "message": "Test webhook received",
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
