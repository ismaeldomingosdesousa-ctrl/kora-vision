"""WhatsApp connector."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import logging

from .base import BaseConnector, ConnectorConfig, SyncResult, DataRecord

logger = logging.getLogger(__name__)


class WhatsAppConnector(BaseConnector):
    """Connector for WhatsApp Business API."""

    CONNECTOR_TYPE = "whatsapp"
    API_BASE_URL = "https://graph.instagram.com/v18.0"

    def __init__(self, config: ConnectorConfig):
        """Initialize WhatsApp connector."""

        super().__init__(config)
        self.phone_number_id = self.credentials.get("phone_number_id")
        self.access_token = self.credentials.get("access_token")
        self.business_account_id = self.credentials.get("business_account_id")

    async def test_connection(self) -> bool:
        """Test connection to WhatsApp."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.API_BASE_URL}/{self.phone_number_id}",
                    params={"access_token": self.access_token},
                    timeout=10,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"WhatsApp connection test failed: {e}")
            return False

    async def validate_credentials(self) -> bool:
        """Validate WhatsApp credentials."""

        if not all([self.phone_number_id, self.access_token, self.business_account_id]):
            logger.error("Missing WhatsApp credentials")
            return False

        return await self.test_connection()

    async def sync(self, since: Optional[datetime] = None) -> SyncResult:
        """Sync messages from WhatsApp."""

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
            logger.error(f"WhatsApp sync failed: {e}")
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
        """Get messages from WhatsApp."""

        try:
            messages = []

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.API_BASE_URL}/{self.phone_number_id}/messages",
                    params={
                        "access_token": self.access_token,
                        "limit": limit,
                        "after": offset if offset > 0 else None,
                    },
                    timeout=10,
                )

                if response.status_code != 200:
                    logger.error(f"Failed to get WhatsApp messages: {response.text}")
                    return []

                data = response.json()

                for item in data.get("data", []):
                    messages.append(
                        DataRecord(
                            external_id=item["id"],
                            data=item,
                            synced_at=datetime.utcnow(),
                            source="whatsapp",
                        )
                    )

            return messages

        except Exception as e:
            logger.error(f"Failed to get WhatsApp messages: {e}")
            return []

    def get_schema(self) -> Dict[str, Any]:
        """Get WhatsApp connector schema."""

        return {
            "type": "object",
            "properties": {
                "phone_number_id": {
                    "type": "string",
                    "description": "WhatsApp phone number ID",
                },
                "access_token": {
                    "type": "string",
                    "description": "WhatsApp Business API access token",
                },
                "business_account_id": {
                    "type": "string",
                    "description": "WhatsApp Business Account ID",
                },
            },
            "required": ["phone_number_id", "access_token", "business_account_id"],
        }

    async def transform_record(self, record: DataRecord) -> Dict[str, Any]:
        """Transform WhatsApp message to internal format."""

        message = record.data

        return {
            "external_id": record.external_id,
            "message_id": message.get("id"),
            "from": message.get("from"),
            "to": message.get("to"),
            "timestamp": message.get("timestamp"),
            "type": message.get("type"),
            "text": message.get("text", {}).get("body") if message.get("type") == "text" else None,
            "status": message.get("status"),
            "raw_data": message,
        }
