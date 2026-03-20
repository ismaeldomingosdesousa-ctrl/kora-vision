"""Datadog connector."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import httpx
import logging

from .base import BaseConnector, ConnectorConfig, SyncResult, DataRecord

logger = logging.getLogger(__name__)


class DatadogConnector(BaseConnector):
    """Connector for Datadog."""

    CONNECTOR_TYPE = "datadog"
    API_BASE_URL = "https://api.datadoghq.com/api/v1"

    def __init__(self, config: ConnectorConfig):
        """Initialize Datadog connector."""

        super().__init__(config)
        self.api_key = self.credentials.get("api_key")
        self.app_key = self.credentials.get("app_key")
        self.site = self.settings.get("site", "datadoghq.com")
        self.query = self.settings.get("query", "host:*")

    async def test_connection(self) -> bool:
        """Test connection to Datadog."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.API_BASE_URL}/validate",
                    headers=self._get_headers(),
                    timeout=10,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Datadog connection test failed: {e}")
            return False

    async def validate_credentials(self) -> bool:
        """Validate Datadog credentials."""

        if not all([self.api_key, self.app_key]):
            logger.error("Missing Datadog credentials")
            return False

        return await self.test_connection()

    async def sync(self, since: Optional[datetime] = None) -> SyncResult:
        """Sync metrics from Datadog."""

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
            logger.error(f"Datadog sync failed: {e}")
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
        """Get metrics from Datadog."""

        try:
            records = []

            # Calculate time range
            if since is None:
                since = datetime.utcnow() - timedelta(hours=1)

            from_timestamp = int(since.timestamp())
            to_timestamp = int(datetime.utcnow().timestamp())

            async with httpx.AsyncClient() as client:
                # Get metrics list
                response = await client.get(
                    f"{self.API_BASE_URL}/query",
                    headers=self._get_headers(),
                    params={
                        "query": self.query,
                        "from": from_timestamp,
                        "to": to_timestamp,
                    },
                    timeout=10,
                )

                if response.status_code != 200:
                    logger.error(f"Failed to get Datadog metrics: {response.text}")
                    return []

                data = response.json()

                # Transform metrics to records
                for series in data.get("series", []):
                    records.append(
                        DataRecord(
                            external_id=series.get("metric"),
                            data=series,
                            synced_at=datetime.utcnow(),
                            source="datadog",
                        )
                    )

            return records[offset:offset + limit]

        except Exception as e:
            logger.error(f"Failed to get Datadog metrics: {e}")
            return []

    def get_schema(self) -> Dict[str, Any]:
        """Get Datadog connector schema."""

        return {
            "type": "object",
            "properties": {
                "api_key": {
                    "type": "string",
                    "description": "Datadog API key",
                },
                "app_key": {
                    "type": "string",
                    "description": "Datadog application key",
                },
                "site": {
                    "type": "string",
                    "description": "Datadog site (datadoghq.com or datadoghq.eu)",
                    "default": "datadoghq.com",
                },
                "query": {
                    "type": "string",
                    "description": "Datadog query to filter metrics",
                    "default": "host:*",
                },
            },
            "required": ["api_key", "app_key"],
        }

    async def transform_record(self, record: DataRecord) -> Dict[str, Any]:
        """Transform Datadog metric to internal format."""

        series = record.data

        return {
            "external_id": record.external_id,
            "metric_name": series.get("metric"),
            "tags": series.get("tags", []),
            "points": series.get("pointlist", []),
            "host": series.get("host"),
            "raw_data": series,
        }

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""

        return {
            "DD-API-KEY": self.api_key,
            "DD-APPLICATION-KEY": self.app_key,
            "Content-Type": "application/json",
        }
