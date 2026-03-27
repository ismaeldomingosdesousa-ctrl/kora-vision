"""Integration management API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
from cryptography.fernet import Fernet
import os

from shared.database import get_db
from shared.models import Integration, DashboardWidget, CachedData
from shared.integrations import (
    JiraIntegration, GoogleChatIntegration, GmailIntegration,
    GoogleCalendarIntegration, DatadogIntegration, DynatraceIntegration,
    IntegrationType
)

router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])

# Encryption key for credentials
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "default-key").encode()
cipher = Fernet(ENCRYPTION_KEY if len(ENCRYPTION_KEY) == 32 else Fernet.generate_key())


class IntegrationCreate(BaseModel):
    """Create integration request."""
    name: str
    type: str
    credentials: Dict[str, Any]
    jira_space_key: Optional[str] = None
    google_chat_space_id: Optional[str] = None
    datadog_site: Optional[str] = None
    dynatrace_environment: Optional[str] = None


class IntegrationUpdate(BaseModel):
    """Update integration request."""
    name: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    jira_space_key: Optional[str] = None
    google_chat_space_id: Optional[str] = None


class IntegrationResponse(BaseModel):
    """Integration response."""
    id: str
    name: str
    type: str
    is_active: bool
    created_at: str
    updated_at: str


@router.post("/", response_model=IntegrationResponse)
async def create_integration(
    integration: IntegrationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new integration."""
    try:
        # Encrypt credentials
        credentials_json = json.dumps(integration.credentials)
        encrypted_creds = cipher.encrypt(credentials_json.encode()).decode()
        
        # Create integration
        new_integration = Integration(
            name=integration.name,
            type=integration.type,
            credentials=encrypted_creds,
            jira_space_key=integration.jira_space_key,
            google_chat_space_id=integration.google_chat_space_id,
            datadog_site=integration.datadog_site,
            dynatrace_environment=integration.dynatrace_environment
        )
        
        db.add(new_integration)
        await db.commit()
        await db.refresh(new_integration)
        
        return IntegrationResponse(
            id=new_integration.id,
            name=new_integration.name,
            type=new_integration.type,
            is_active=new_integration.is_active,
            created_at=new_integration.created_at.isoformat(),
            updated_at=new_integration.updated_at.isoformat()
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[IntegrationResponse])
async def list_integrations(db: AsyncSession = Depends(get_db)):
    """List all integrations."""
    try:
        result = await db.execute(select(Integration))
        integrations = result.scalars().all()
        
        return [
            IntegrationResponse(
                id=i.id,
                name=i.name,
                type=i.type,
                is_active=i.is_active,
                created_at=i.created_at.isoformat(),
                updated_at=i.updated_at.isoformat()
            )
            for i in integrations
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific integration."""
    try:
        result = await db.execute(
            select(Integration).where(Integration.id == integration_id)
        )
        integration = result.scalar_one_or_none()
        
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        return IntegrationResponse(
            id=integration.id,
            name=integration.name,
            type=integration.type,
            is_active=integration.is_active,
            created_at=integration.created_at.isoformat(),
            updated_at=integration.updated_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: str,
    update: IntegrationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an integration."""
    try:
        result = await db.execute(
            select(Integration).where(Integration.id == integration_id)
        )
        integration = result.scalar_one_or_none()
        
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        # Update fields
        if update.name:
            integration.name = update.name
        if update.is_active is not None:
            integration.is_active = update.is_active
        if update.credentials:
            credentials_json = json.dumps(update.credentials)
            integration.credentials = cipher.encrypt(credentials_json.encode()).decode()
        if update.jira_space_key:
            integration.jira_space_key = update.jira_space_key
        if update.google_chat_space_id:
            integration.google_chat_space_id = update.google_chat_space_id
        
        await db.commit()
        await db.refresh(integration)
        
        return IntegrationResponse(
            id=integration.id,
            name=integration.name,
            type=integration.type,
            is_active=integration.is_active,
            created_at=integration.created_at.isoformat(),
            updated_at=integration.updated_at.isoformat()
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an integration."""
    try:
        result = await db.execute(
            select(Integration).where(Integration.id == integration_id)
        )
        integration = result.scalar_one_or_none()
        
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        await db.delete(integration)
        await db.commit()
        
        return {"message": "Integration deleted"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{integration_id}/test")
async def test_integration(
    integration_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Test an integration connection."""
    try:
        result = await db.execute(
            select(Integration).where(Integration.id == integration_id)
        )
        integration = result.scalar_one_or_none()
        
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        # Decrypt credentials
        encrypted_creds = integration.credentials
        decrypted_creds = cipher.decrypt(encrypted_creds.encode()).decode()
        credentials = json.loads(decrypted_creds)
        
        # Test based on type
        if integration.type == "jira":
            jira = JiraIntegration(
                api_token=credentials.get("api_token"),
                site_url=credentials.get("site_url"),
                email=credentials.get("email")
            )
            data = await jira.get_issues_by_space(integration.jira_space_key or "TEST")
            return {"status": "success" if "error" not in data else "failed", "data": data}
        
        elif integration.type == "google_chat":
            chat = GoogleChatIntegration(access_token=credentials.get("access_token"))
            data = await chat.check_war_room_activity(integration.google_chat_space_id or "")
            return {"status": "success" if "error" not in data else "failed", "data": data}
        
        elif integration.type == "gmail":
            gmail = GmailIntegration(access_token=credentials.get("access_token"))
            unread = await gmail.get_unread_count()
            return {"status": "success", "unread_count": unread}
        
        elif integration.type == "google_calendar":
            calendar = GoogleCalendarIntegration(access_token=credentials.get("access_token"))
            events = await calendar.get_today_events()
            return {"status": "success", "events_count": len(events)}
        
        elif integration.type == "datadog":
            datadog = DatadogIntegration(
                api_key=credentials.get("api_key"),
                app_key=credentials.get("app_key")
            )
            alerts = await datadog.get_alerts()
            return {"status": "success", "alerts_count": len(alerts)}
        
        elif integration.type == "dynatrace":
            dynatrace = DynatraceIntegration(
                environment_id=integration.dynatrace_environment or "",
                api_token=credentials.get("api_token")
            )
            alerts = await dynatrace.get_alerts()
            return {"status": "success", "alerts_count": len(alerts)}
        
        else:
            return {"status": "unknown", "message": "Integration type not supported"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
