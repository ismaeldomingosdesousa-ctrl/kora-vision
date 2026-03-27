"""Integration handlers for external services."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import httpx
import json
from enum import Enum

class IntegrationType(str, Enum):
    """Supported integration types."""
    JIRA = "jira"
    GOOGLE_CHAT = "google_chat"
    GMAIL = "gmail"
    GOOGLE_CALENDAR = "google_calendar"
    DATADOG = "datadog"
    DYNATRACE = "dynatrace"


class JiraIntegration:
    """Jira Service Manager Cloud integration."""
    
    def __init__(self, api_token: str, site_url: str, email: str):
        self.api_token = api_token
        self.site_url = site_url
        self.email = email
        self.base_url = f"https://{site_url}.atlassian.net/rest/api/3"
    
    async def get_issues_by_space(self, space_key: str) -> Dict[str, Any]:
        """Get issues (Requests and Incidents) by space."""
        try:
            async with httpx.AsyncClient() as client:
                # Get all issues in the space
                response = await client.get(
                    f"{self.base_url}/search",
                    params={
                        "jql": f"project = {space_key}",
                        "maxResults": 100
                    },
                    auth=(self.email, self.api_token)
                )
                response.raise_for_status()
                
                issues = response.json()["issues"]
                
                # Separate by type
                requests = [i for i in issues if i["fields"]["issuetype"]["name"] == "Service Request"]
                incidents = [i for i in issues if i["fields"]["issuetype"]["name"] == "Incident"]
                
                return {
                    "total_requests": len(requests),
                    "total_incidents": len(incidents),
                    "requests": requests,
                    "incidents": incidents
                }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_sla_at_risk(self, space_key: str) -> List[Dict[str, Any]]:
        """Get incidents at risk of SLA breach."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    params={
                        "jql": f"project = {space_key} AND type = Incident AND status != Done",
                        "maxResults": 100
                    },
                    auth=(self.email, self.api_token)
                )
                response.raise_for_status()
                
                issues = response.json()["issues"]
                at_risk = []
                
                for issue in issues:
                    # Check if SLA is at risk (simplified)
                    if "customfield_10000" in issue["fields"]:  # SLA field
                        at_risk.append({
                            "key": issue["key"],
                            "summary": issue["fields"]["summary"],
                            "sla": issue["fields"].get("customfield_10000")
                        })
                
                return at_risk
        except Exception as e:
            return [{"error": str(e)}]
    
    async def get_metrics(self, space_key: str) -> Dict[str, Any]:
        """Get daily, weekly, and monthly metrics."""
        try:
            today = datetime.now()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            async with httpx.AsyncClient() as client:
                # Daily
                daily_response = await client.get(
                    f"{self.base_url}/search",
                    params={
                        "jql": f"project = {space_key} AND created >= {today.date()}",
                    },
                    auth=(self.email, self.api_token)
                )
                daily_count = daily_response.json()["total"]
                
                # Weekly
                weekly_response = await client.get(
                    f"{self.base_url}/search",
                    params={
                        "jql": f"project = {space_key} AND created >= {week_ago.date()}",
                    },
                    auth=(self.email, self.api_token)
                )
                weekly_count = weekly_response.json()["total"]
                
                # Monthly
                monthly_response = await client.get(
                    f"{self.base_url}/search",
                    params={
                        "jql": f"project = {space_key} AND created >= {month_ago.date()}",
                    },
                    auth=(self.email, self.api_token)
                )
                monthly_count = monthly_response.json()["total"]
                
                return {
                    "daily": daily_count,
                    "weekly": weekly_count,
                    "monthly": monthly_count
                }
        except Exception as e:
            return {"error": str(e)}


class GoogleChatIntegration:
    """Google Chat integration."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://chat.googleapis.com/v1"
    
    async def get_space_messages(self, space_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent messages from a space."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/spaces/{space_id}/messages",
                    params={"pageSize": limit},
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )
                response.raise_for_status()
                
                messages = response.json().get("messages", [])
                return [
                    {
                        "sender": msg.get("sender", {}).get("displayName"),
                        "text": msg.get("text"),
                        "timestamp": msg.get("createTime")
                    }
                    for msg in messages
                ]
        except Exception as e:
            return [{"error": str(e)}]
    
    async def check_war_room_activity(self, space_id: str) -> Dict[str, Any]:
        """Check if war room space has recent activity."""
        try:
            messages = await self.get_space_messages(space_id, limit=10)
            
            if messages and "error" not in messages[0]:
                return {
                    "has_activity": len(messages) > 0,
                    "recent_messages": messages,
                    "last_activity": messages[0].get("timestamp") if messages else None
                }
            else:
                return {"error": "Failed to fetch messages"}
        except Exception as e:
            return {"error": str(e)}


class GmailIntegration:
    """Gmail integration."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://www.googleapis.com/gmail/v1/users/me"
    
    async def get_unread_count(self) -> int:
        """Get count of unread emails."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/messages",
                    params={"q": "is:unread"},
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )
                response.raise_for_status()
                
                return response.json().get("resultSizeEstimate", 0)
        except Exception as e:
            return 0
    
    async def get_recent_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent email titles."""
        try:
            async with httpx.AsyncClient() as client:
                # Get message IDs
                response = await client.get(
                    f"{self.base_url}/messages",
                    params={"maxResults": limit},
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )
                response.raise_for_status()
                
                message_ids = [msg["id"] for msg in response.json().get("messages", [])]
                emails = []
                
                # Get email details
                for msg_id in message_ids:
                    msg_response = await client.get(
                        f"{self.base_url}/messages/{msg_id}",
                        headers={"Authorization": f"Bearer {self.access_token}"}
                    )
                    msg_response.raise_for_status()
                    
                    msg_data = msg_response.json()
                    headers = {h["name"]: h["value"] for h in msg_data["payload"]["headers"]}
                    
                    emails.append({
                        "subject": headers.get("Subject", "No Subject"),
                        "from": headers.get("From", "Unknown"),
                        "date": headers.get("Date", "")
                    })
                
                return emails
        except Exception as e:
            return [{"error": str(e)}]


class GoogleCalendarIntegration:
    """Google Calendar integration."""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://www.googleapis.com/calendar/v3"
    
    async def get_today_events(self) -> List[Dict[str, Any]]:
        """Get today's calendar events."""
        try:
            today = datetime.now().date()
            start_time = f"{today}T00:00:00Z"
            end_time = f"{today}T23:59:59Z"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/calendars/primary/events",
                    params={
                        "timeMin": start_time,
                        "timeMax": end_time,
                        "singleEvents": True,
                        "orderBy": "startTime"
                    },
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )
                response.raise_for_status()
                
                events = response.json().get("items", [])
                return [
                    {
                        "title": event.get("summary"),
                        "start": event.get("start", {}).get("dateTime"),
                        "end": event.get("end", {}).get("dateTime"),
                        "description": event.get("description", "")
                    }
                    for event in events
                ]
        except Exception as e:
            return [{"error": str(e)}]


class DatadogIntegration:
    """Datadog integration."""
    
    def __init__(self, api_key: str, app_key: str):
        self.api_key = api_key
        self.app_key = app_key
        self.base_url = "https://api.datadoghq.com/api/v1"
    
    async def get_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/monitor",
                    headers={
                        "DD-API-KEY": self.api_key,
                        "DD-APPLICATION-KEY": self.app_key
                    }
                )
                response.raise_for_status()
                
                monitors = response.json()
                alerts = [
                    {
                        "id": m.get("id"),
                        "name": m.get("name"),
                        "status": m.get("overall_state"),
                        "type": m.get("type")
                    }
                    for m in monitors if m.get("overall_state") != "OK"
                ]
                
                return alerts
        except Exception as e:
            return [{"error": str(e)}]
    
    async def get_errors(self) -> List[Dict[str, Any]]:
        """Get recent errors."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/events",
                    params={
                        "priority": "high",
                        "sources": "monitor"
                    },
                    headers={
                        "DD-API-KEY": self.api_key,
                        "DD-APPLICATION-KEY": self.app_key
                    }
                )
                response.raise_for_status()
                
                events = response.json().get("events", [])
                return [
                    {
                        "title": e.get("title"),
                        "text": e.get("text"),
                        "timestamp": e.get("date_happened")
                    }
                    for e in events[:10]
                ]
        except Exception as e:
            return [{"error": str(e)}]


class DynatraceIntegration:
    """Dynatrace integration."""
    
    def __init__(self, environment_id: str, api_token: str):
        self.environment_id = environment_id
        self.api_token = api_token
        self.base_url = f"https://{environment_id}.live.dynatrace.com/api/v2"
    
    async def get_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/events",
                    params={
                        "filter": "event.kind(\"AVAILABILITY_EVENT\") AND status(\"OPEN\")",
                        "pageSize": 50
                    },
                    headers={"Authorization": f"Api-Token {self.api_token}"}
                )
                response.raise_for_status()
                
                events = response.json().get("events", [])
                return [
                    {
                        "id": e.get("eventId"),
                        "title": e.get("title"),
                        "severity": e.get("severityLevel"),
                        "timestamp": e.get("startTime")
                    }
                    for e in events
                ]
        except Exception as e:
            return [{"error": str(e)}]
    
    async def get_errors(self) -> List[Dict[str, Any]]:
        """Get recent errors."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/events",
                    params={
                        "filter": "event.kind(\"AVAILABILITY_EVENT\") AND severity(\"CRITICAL\", \"MAJOR\")",
                        "pageSize": 50
                    },
                    headers={"Authorization": f"Api-Token {self.api_token}"}
                )
                response.raise_for_status()
                
                events = response.json().get("events", [])
                return [
                    {
                        "id": e.get("eventId"),
                        "title": e.get("title"),
                        "severity": e.get("severityLevel"),
                        "description": e.get("description")
                    }
                    for e in events[:10]
                ]
        except Exception as e:
            return [{"error": str(e)}]
