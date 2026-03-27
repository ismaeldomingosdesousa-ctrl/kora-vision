"""Unified dashboard API endpoint."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import os

from shared.database import get_db
from shared.models import Integration, CachedData
from shared.integrations import (
    JiraIntegration, GoogleChatIntegration, GmailIntegration,
    GoogleCalendarIntegration, DatadogIntegration, DynatraceIntegration
)

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

# Encryption key for credentials
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "default-key").encode()
cipher = Fernet(ENCRYPTION_KEY if len(ENCRYPTION_KEY) == 32 else Fernet.generate_key())


async def decrypt_credentials(encrypted_creds: str) -> Dict[str, Any]:
    """Decrypt integration credentials."""
    try:
        decrypted = cipher.decrypt(encrypted_creds.encode()).decode()
        return json.loads(decrypted)
    except:
        return {}


@router.get("/unified")
async def get_unified_dashboard(db: AsyncSession = Depends(get_db)):
    """Get unified dashboard with all integrations data."""
    try:
        # Get all active integrations
        result = await db.execute(
            select(Integration).where(Integration.is_active == True)
        )
        integrations = result.scalars().all()
        
        dashboard_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "jira": {},
            "google_chat": {},
            "gmail": {},
            "google_calendar": {},
            "datadog": {},
            "dynatrace": {}
        }
        
        # Process each integration
        for integration in integrations:
            credentials = await decrypt_credentials(integration.credentials)
            
            try:
                if integration.type == "jira":
                    jira = JiraIntegration(
                        api_token=credentials.get("api_token"),
                        site_url=credentials.get("site_url"),
                        email=credentials.get("email")
                    )
                    
                    issues = await jira.get_issues_by_space(integration.jira_space_key or "")
                    sla_at_risk = await jira.get_sla_at_risk(integration.jira_space_key or "")
                    metrics = await jira.get_metrics(integration.jira_space_key or "")
                    
                    dashboard_data["jira"] = {
                        "name": integration.name,
                        "issues": issues,
                        "sla_at_risk": sla_at_risk,
                        "metrics": metrics,
                        "last_updated": datetime.utcnow().isoformat()
                    }
                
                elif integration.type == "google_chat":
                    chat = GoogleChatIntegration(
                        access_token=credentials.get("access_token")
                    )
                    
                    activity = await chat.check_war_room_activity(
                        integration.google_chat_space_id or ""
                    )
                    
                    dashboard_data["google_chat"] = {
                        "name": integration.name,
                        "activity": activity,
                        "last_updated": datetime.utcnow().isoformat()
                    }
                
                elif integration.type == "gmail":
                    gmail = GmailIntegration(
                        access_token=credentials.get("access_token")
                    )
                    
                    unread_count = await gmail.get_unread_count()
                    recent_emails = await gmail.get_recent_emails(limit=10)
                    
                    dashboard_data["gmail"] = {
                        "name": integration.name,
                        "unread_count": unread_count,
                        "recent_emails": recent_emails,
                        "last_updated": datetime.utcnow().isoformat()
                    }
                
                elif integration.type == "google_calendar":
                    calendar = GoogleCalendarIntegration(
                        access_token=credentials.get("access_token")
                    )
                    
                    events = await calendar.get_today_events()
                    
                    dashboard_data["google_calendar"] = {
                        "name": integration.name,
                        "events": events,
                        "last_updated": datetime.utcnow().isoformat()
                    }
                
                elif integration.type == "datadog":
                    datadog = DatadogIntegration(
                        api_key=credentials.get("api_key"),
                        app_key=credentials.get("app_key")
                    )
                    
                    alerts = await datadog.get_alerts()
                    errors = await datadog.get_errors()
                    
                    dashboard_data["datadog"] = {
                        "name": integration.name,
                        "alerts": alerts,
                        "errors": errors,
                        "last_updated": datetime.utcnow().isoformat()
                    }
                
                elif integration.type == "dynatrace":
                    dynatrace = DynatraceIntegration(
                        environment_id=integration.dynatrace_environment or "",
                        api_token=credentials.get("api_token")
                    )
                    
                    alerts = await dynatrace.get_alerts()
                    errors = await dynatrace.get_errors()
                    
                    dashboard_data["dynatrace"] = {
                        "name": integration.name,
                        "alerts": alerts,
                        "errors": errors,
                        "last_updated": datetime.utcnow().isoformat()
                    }
            
            except Exception as e:
                # Log error but continue with other integrations
                dashboard_data[integration.type]["error"] = str(e)
        
        return dashboard_data
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jira/{integration_id}")
async def get_jira_data(
    integration_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get Jira data for a specific integration."""
    try:
        result = await db.execute(
            select(Integration).where(Integration.id == integration_id)
        )
        integration = result.scalar_one_or_none()
        
        if not integration or integration.type != "jira":
            raise HTTPException(status_code=404, detail="Jira integration not found")
        
        credentials = await decrypt_credentials(integration.credentials)
        jira = JiraIntegration(
            api_token=credentials.get("api_token"),
            site_url=credentials.get("site_url"),
            email=credentials.get("email")
        )
        
        issues = await jira.get_issues_by_space(integration.jira_space_key or "")
        sla_at_risk = await jira.get_sla_at_risk(integration.jira_space_key or "")
        metrics = await jira.get_metrics(integration.jira_space_key or "")
        
        return {
            "name": integration.name,
            "issues": issues,
            "sla_at_risk": sla_at_risk,
            "metrics": metrics
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/gmail/{integration_id}")
async def get_gmail_data(
    integration_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get Gmail data for a specific integration."""
    try:
        result = await db.execute(
            select(Integration).where(Integration.id == integration_id)
        )
        integration = result.scalar_one_or_none()
        
        if not integration or integration.type != "gmail":
            raise HTTPException(status_code=404, detail="Gmail integration not found")
        
        credentials = await decrypt_credentials(integration.credentials)
        gmail = GmailIntegration(access_token=credentials.get("access_token"))
        
        unread_count = await gmail.get_unread_count()
        recent_emails = await gmail.get_recent_emails(limit=10)
        
        return {
            "name": integration.name,
            "unread_count": unread_count,
            "recent_emails": recent_emails
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/google-calendar/{integration_id}")
async def get_calendar_data(
    integration_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get Google Calendar data for a specific integration."""
    try:
        result = await db.execute(
            select(Integration).where(Integration.id == integration_id)
        )
        integration = result.scalar_one_or_none()
        
        if not integration or integration.type != "google_calendar":
            raise HTTPException(status_code=404, detail="Google Calendar integration not found")
        
        credentials = await decrypt_credentials(integration.credentials)
        calendar = GoogleCalendarIntegration(
            access_token=credentials.get("access_token")
        )
        
        events = await calendar.get_today_events()
        
        return {
            "name": integration.name,
            "events": events
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/datadog/{integration_id}")
async def get_datadog_data(
    integration_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get Datadog data for a specific integration."""
    try:
        result = await db.execute(
            select(Integration).where(Integration.id == integration_id)
        )
        integration = result.scalar_one_or_none()
        
        if not integration or integration.type != "datadog":
            raise HTTPException(status_code=404, detail="Datadog integration not found")
        
        credentials = await decrypt_credentials(integration.credentials)
        datadog = DatadogIntegration(
            api_key=credentials.get("api_key"),
            app_key=credentials.get("app_key")
        )
        
        alerts = await datadog.get_alerts()
        errors = await datadog.get_errors()
        
        return {
            "name": integration.name,
            "alerts": alerts,
            "errors": errors
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dynatrace/{integration_id}")
async def get_dynatrace_data(
    integration_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get Dynatrace data for a specific integration."""
    try:
        result = await db.execute(
            select(Integration).where(Integration.id == integration_id)
        )
        integration = result.scalar_one_or_none()
        
        if not integration or integration.type != "dynatrace":
            raise HTTPException(status_code=404, detail="Dynatrace integration not found")
        
        credentials = await decrypt_credentials(integration.credentials)
        dynatrace = DynatraceIntegration(
            environment_id=integration.dynatrace_environment or "",
            api_token=credentials.get("api_token")
        )
        
        alerts = await dynatrace.get_alerts()
        errors = await dynatrace.get_errors()
        
        return {
            "name": integration.name,
            "alerts": alerts,
            "errors": errors
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
