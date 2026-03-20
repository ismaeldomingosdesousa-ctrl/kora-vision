"""Dynatrace connector."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import httpx
import logging

from .base import BaseConnector, ConnectorConfig, SyncResult, DataRecord

logger = logging.getLogger(__name__)


class DynatraceConnector(BaseConnector):
    """Connector for Dynatrace."""

    CONNECTOR_TYPE = "dynatrace"

    def __init__(self, config: ConnectorConfig):
        """Initialize Dynatrace connector."""

        super().__init__(config)
        self.environment_id = self.credentials.get("environment_id")
        self.api_token = self.credentials.get("api_token")
        self.environment_url = self.credentials.get("environment_url")
        self.metric_selector = self.settings.get("metric_selector", "builtin:host.cpu.usage")

    async def test_connection(self) -> bool:
        """Test connection to Dynatrace."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.environment_url}/api/v2/environments/{self.environment_id}",
                    headers=self._get_headers(),
                    timeout=10,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Dynatrace connection test failed: {e}")
            return False

    async def validate_credentials(self) -> bool:
        """Validate Dynatrace credentials."""

        if not all([self.environment_id, self.api_token, self.environment_url]):
            logger.error("Missing Dynatrace credentials")
            return False

        return await self.test_connection()

    async def sync(self, since: Optional[datetime] = None) -> SyncResult:
        """Sync metrics from Dynatrace."""

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
            logger.error(f"Dynatrace sync failed: {e}")
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
        """Get metrics from Dynatrace."""

        try:
            records = []

            # Calculate time range
            if since is None:
                since = datetime.utcnow() - timedelta(hours=1)

            from_timestamp = int(since.timestamp() * 1000)
            to_timestamp = int(datetime.utcnow().timestamp() * 1000)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.environment_url}/api/v2/metrics/query",
                    headers=self._get_headers(),
                    params={
                        "metricSelector": self.metric_selector,
                        "from": from_timestamp,
                        "to": to_timestamp,
                        "resolution": "1m",
                    },
                    timeout=10,
                )

                if response.status_code != 200:
                    logger.error(f"Failed to get Dynatrace metrics: {response.text}")
                    return []

                data = response.json()

                # Transform metrics to records
                for result in data.get("result", []):
                    for data_point in result.get("data", []):
                        records.append(
                            DataRecord(
                                external_id=f"{result.get('metricId')}_{data_point.get('timestamp')}",
                                data=data_point,
                                synced_at=datetime.utcnow(),
                                source="dynatrace",
                            )
                        )

            return records[offset:offset + limit]

        except Exception as e:
            logger.error(f"Failed to get Dynatrace metrics: {e}")
            return []

    def get_schema(self) -> Dict[str, Any]:
        """Get Dynatrace connector schema."""

        return {
            "type": "object",
            "properties": {
                "environment_id": {
                    "type": "string",
                    "description": "Dynatrace environment ID",
                },
                "api_token": {
                    "type": "string",
                    "description": "Dynatrace API token",
                },
                "environment_url": {
                    "type": "string",
                    "description": "Dynatrace environment URL",
                },
                "metric_selector": {
                    "type": "string",
                    "description": "Dynatrace metric selector",
                    "default": "builtin:host.cpu.usage",
                },
            },
            "required": ["environment_id", "api_token", "environment_url"],
        }

    async def transform_record(self, record: DataRecord) -> Dict[str, Any]:
        """Transform Dynatrace metric to internal format."""

        data_point = record.data

        return {
            "external_id": record.external_id,
            "timestamp": data_point.get("timestamp"),
            "value": data_point.get("values", [None])[0],
            "dimensions": data_point.get("dimensions", {}),
            "raw_data": data_point,
        }

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""

        return {
            "Authorization": f"Api-Token {self.api_token}",
            "Content-Type": "application/json",
        }
