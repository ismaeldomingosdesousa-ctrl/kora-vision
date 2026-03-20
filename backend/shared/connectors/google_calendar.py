"""Google Calendar connector."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import logging

from .base import BaseConnector, ConnectorConfig, SyncResult, DataRecord

logger = logging.getLogger(__name__)


class GoogleCalendarConnector(BaseConnector):
    """Connector for Google Calendar."""

    CONNECTOR_TYPE = "google_calendar"
    API_BASE_URL = "https://www.googleapis.com/calendar/v3"

    def __init__(self, config: ConnectorConfig):
        """Initialize Google Calendar connector."""

        super().__init__(config)
        self.access_token = self.credentials.get("access_token")
        self.calendar_id = self.settings.get("calendar_id", "primary")

    async def test_connection(self) -> bool:
        """Test connection to Google Calendar."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.API_BASE_URL}/calendars/{self.calendar_id}",
                    headers=self._get_headers(),
                    timeout=10,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Google Calendar connection test failed: {e}")
            return False

    async def validate_credentials(self) -> bool:
        """Validate Google Calendar credentials."""

        if not self.access_token:
            logger.error("Missing access token")
            return False

        return await self.test_connection()

    async def sync(self, since: Optional[datetime] = None) -> SyncResult:
        """Sync events from Google Calendar."""

        started_at = datetime.utcnow()

        try:
            records = await self.get_records(since=since)
            completed_at = datetime.utcnow()

            return SyncResult(
                success=True,
                records_synced=len(records),
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=(completed_at - started_at).total_seconds(),
            )

        except Exception as e:
            logger.error(f"Google Calendar sync failed: {e}")
            await self.handle_error(e)

            return SyncResult(
                success=False,
                records_synced=0,
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.utcnow(),
            )

    async def get_records(
        self,
        limit: int = 100,
        offset: int = 0,
        since: Optional[datetime] = None
    ) -> List[DataRecord]:
        """Get events from Google Calendar."""

        try:
            events = []
            page_token = None

            async with httpx.AsyncClient() as client:
                while len(events) < limit:
                    params = {
                        "maxResults": min(limit - len(events), 250),
                        "orderBy": "startTime",
                        "singleEvents": True,
                    }

                    if page_token:
                        params["pageToken"] = page_token

                    if since:
                        params["timeMin"] = since.isoformat()

                    response = await client.get(
                        f"{self.API_BASE_URL}/calendars/{self.calendar_id}/events",
                        headers=self._get_headers(),
                        params=params,
                        timeout=10,
                    )

                    if response.status_code != 200:
                        logger.error(f"Failed to get events: {response.text}")
                        break

                    data = response.json()
                    items = data.get("items", [])

                    for item in items:
                        events.append(
                            DataRecord(
                                external_id=item["id"],
                                data=item,
                                synced_at=datetime.utcnow(),
                                source="google_calendar",
                            )
                        )

                    page_token = data.get("nextPageToken")
                    if not page_token:
                        break

            return events[offset:offset + limit]

        except Exception as e:
            logger.error(f"Failed to get Google Calendar events: {e}")
            return []

    def get_schema(self) -> Dict[str, Any]:
        """Get Google Calendar connector schema."""

        return {
            "type": "object",
            "properties": {
                "access_token": {
                    "type": "string",
                    "description": "Google OAuth2 access token",
                },
                "calendar_id": {
                    "type": "string",
                    "description": "Calendar ID (default: primary)",
                    "default": "primary",
                },
            },
            "required": ["access_token"],
        }

    async def transform_record(self, record: DataRecord) -> Dict[str, Any]:
        """Transform Google Calendar event to internal format."""

        event = record.data

        return {
            "external_id": record.external_id,
            "title": event.get("summary"),
            "description": event.get("description"),
            "start_time": event.get("start", {}).get("dateTime"),
            "end_time": event.get("end", {}).get("dateTime"),
            "location": event.get("location"),
            "attendees": [
                attendee["email"]
                for attendee in event.get("attendees", [])
            ],
            "raw_data": event,
        }

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
