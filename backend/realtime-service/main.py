"""Real-time Service - WebSocket server for live updates."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import json
from typing import Set, Dict
from datetime import datetime
import asyncio

from shared.config import settings
from shared.database import get_db, health_check

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


# Connection manager for WebSocket connections
class ConnectionManager:
    """Manage WebSocket connections per tenant."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, tenant_id: str, websocket: WebSocket):
        """Register new WebSocket connection."""

        await websocket.accept()

        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = set()

        self.active_connections[tenant_id].add(websocket)
        logger.info(f"Client connected to tenant {tenant_id}. Total: {len(self.active_connections[tenant_id])}")

    def disconnect(self, tenant_id: str, websocket: WebSocket):
        """Unregister WebSocket connection."""

        if tenant_id in self.active_connections:
            self.active_connections[tenant_id].discard(websocket)

            if not self.active_connections[tenant_id]:
                del self.active_connections[tenant_id]

        logger.info(f"Client disconnected from tenant {tenant_id}")

    async def broadcast_to_tenant(self, tenant_id: str, message: dict):
        """Broadcast message to all clients in tenant."""

        if tenant_id not in self.active_connections:
            return

        disconnected = set()

        for websocket in self.active_connections[tenant_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(websocket)

        # Clean up disconnected clients
        for websocket in disconnected:
            self.active_connections[tenant_id].discard(websocket)

    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected clients."""

        for tenant_id in list(self.active_connections.keys()):
            await self.broadcast_to_tenant(tenant_id, message)

    def get_connection_count(self, tenant_id: str = None) -> int:
        """Get number of active connections."""

        if tenant_id:
            return len(self.active_connections.get(tenant_id, set()))

        return sum(len(conns) for conns in self.active_connections.values())


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""

    # Startup
    logger.info("Starting Real-time Service...")
    db_healthy = await health_check()
    if not db_healthy:
        logger.error("Database health check failed on startup")
        raise RuntimeError("Database connection failed")

    yield

    # Shutdown
    logger.info("Shutting down Real-time Service...")


# Create FastAPI application
app = FastAPI(
    title="Real-time Service",
    version=settings.APP_VERSION,
    description="Real-time Service for Unified Operations Hub",
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
        "service": "realtime-service",
        "version": settings.APP_VERSION,
        "database": "ok" if db_healthy else "error",
        "active_connections": manager.get_connection_count(),
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
# WebSocket Endpoints
# ============================================================================

@app.websocket("/ws/{tenant_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    tenant_id: str,
):
    """WebSocket endpoint for real-time updates."""

    try:
        await manager.connect(tenant_id, websocket)

        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Listen for messages
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                logger.debug(f"Received message from {tenant_id}: {message}")

                # Handle different message types
                message_type = message.get("type")

                if message_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    })

                elif message_type == "subscribe":
                    # TODO: Implement subscription to specific channels
                    await websocket.send_json({
                        "type": "subscribed",
                        "channel": message.get("channel"),
                    })

                elif message_type == "unsubscribe":
                    # TODO: Implement unsubscription
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "channel": message.get("channel"),
                    })

                else:
                    logger.warning(f"Unknown message type: {message_type}")

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                })

    except WebSocketDisconnect:
        manager.disconnect(tenant_id, websocket)
        logger.info(f"WebSocket connection closed for tenant {tenant_id}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(tenant_id, websocket)


# ============================================================================
# Broadcast Endpoints (for testing and internal use)
# ============================================================================

@app.post("/broadcast/{tenant_id}", tags=["Broadcast"])
async def broadcast_to_tenant(
    tenant_id: str,
    message: dict,
):
    """Broadcast message to all clients in tenant (for testing)."""

    try:
        await manager.broadcast_to_tenant(tenant_id, {
            "type": "broadcast",
            "data": message,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            "status": "ok",
            "message": "Broadcast sent",
            "connections": manager.get_connection_count(tenant_id),
        }

    except Exception as e:
        logger.error(f"Error broadcasting: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to broadcast message"
        )


@app.get("/stats", tags=["Stats"])
async def get_stats():
    """Get real-time service statistics."""

    return {
        "total_connections": manager.get_connection_count(),
        "tenants": len(manager.active_connections),
        "timestamp": datetime.utcnow().isoformat(),
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
        workers=1,  # WebSocket requires single worker
    )
