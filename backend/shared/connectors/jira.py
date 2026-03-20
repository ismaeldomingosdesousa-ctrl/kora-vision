"""Jira connector."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import logging
from base64 import b64encode

from .base import BaseConnector, ConnectorConfig, SyncResult, DataRecord

logger = logging.getLogger(__name__)


class JiraConnector(BaseConnector):
    """Connector for Jira."""

    CONNECTOR_TYPE = "jira"

    def __init__(self, config: ConnectorConfig):
        """Initialize Jira connector."""

        super().__init__(config)
        self.host = self.credentials.get("host")
        self.email = self.credentials.get("email")
        self.api_token = self.credentials.get("api_token")
        self.jql = self.settings.get("jql", "assignee = currentUser()")

    async def test_connection(self) -> bool:
        """Test connection to Jira."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.host}/rest/api/3/myself",
                    headers=self._get_headers(),
                    timeout=10,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Jira connection test failed: {e}")
            return False

    async def validate_credentials(self) -> bool:
        """Validate Jira credentials."""

        if not all([self.host, self.email, self.api_token]):
            logger.error("Missing Jira credentials")
            return False

        return await self.test_connection()

    async def sync(self, since: Optional[datetime] = None) -> SyncResult:
        """Sync issues from Jira."""

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
            logger.error(f"Jira sync failed: {e}")
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
        """Get issues from Jira."""

        try:
            issues = []
            jql = self.jql

            # Add updated date filter if provided
            if since:
                jql += f" AND updated >= {since.strftime('%Y-%m-%d %H:%M')}"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.host}/rest/api/3/search",
                    headers=self._get_headers(),
                    params={
                        "jql": jql,
                        "startAt": offset,
                        "maxResults": limit,
                        "expand": "changelog",
                    },
                    timeout=10,
                )

                if response.status_code != 200:
                    logger.error(f"Failed to get Jira issues: {response.text}")
                    return []

                data = response.json()

                for item in data.get("issues", []):
                    issues.append(
                        DataRecord(
                            external_id=item["key"],
                            data=item,
                            synced_at=datetime.utcnow(),
                            source="jira",
                        )
                    )

            return issues

        except Exception as e:
            logger.error(f"Failed to get Jira issues: {e}")
            return []

    def get_schema(self) -> Dict[str, Any]:
        """Get Jira connector schema."""

        return {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "description": "Jira instance URL (e.g., https://company.atlassian.net)",
                },
                "email": {
                    "type": "string",
                    "description": "Jira user email",
                },
                "api_token": {
                    "type": "string",
                    "description": "Jira API token",
                },
                "jql": {
                    "type": "string",
                    "description": "JQL query to filter issues",
                    "default": "assignee = currentUser()",
                },
            },
            "required": ["host", "email", "api_token"],
        }

    async def transform_record(self, record: DataRecord) -> Dict[str, Any]:
        """Transform Jira issue to internal format."""

        issue = record.data
        fields = issue.get("fields", {})

        return {
            "external_id": record.external_id,
            "title": fields.get("summary"),
            "description": fields.get("description"),
            "status": fields.get("status", {}).get("name"),
            "priority": fields.get("priority", {}).get("name"),
            "assignee": fields.get("assignee", {}).get("emailAddress"),
            "project": fields.get("project", {}).get("key"),
            "issue_type": fields.get("issuetype", {}).get("name"),
            "created_at": fields.get("created"),
            "updated_at": fields.get("updated"),
            "raw_data": issue,
        }

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""

        credentials = b64encode(f"{self.email}:{self.api_token}".encode()).decode()

        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        }
