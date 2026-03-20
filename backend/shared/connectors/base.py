"""Base connector class for all integrations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConnectorConfig:
    """Configuration for a connector."""

    connector_type: str
    name: str
    credentials: Dict[str, Any]
    settings: Dict[str, Any] = None
    sync_interval_minutes: int = 30


@dataclass
class SyncResult:
    """Result of a sync operation."""

    success: bool
    records_synced: int
    error_message: Optional[str] = None
    started_at: datetime = None
    completed_at: datetime = None
    duration_seconds: float = 0


@dataclass
class DataRecord:
    """A single record synced from external service."""

    external_id: str
    data: Dict[str, Any]
    synced_at: datetime = None
    source: str = None


class BaseConnector(ABC):
    """Base class for all connectors."""

    def __init__(self, config: ConnectorConfig):
        """Initialize connector with configuration."""

        self.config = config
        self.connector_type = config.connector_type
        self.name = config.name
        self.credentials = config.credentials
        self.settings = config.settings or {}

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if connector can connect to external service.

        Returns:
            bool: True if connection successful, False otherwise
        """

        pass

    @abstractmethod
    async def sync(self, since: Optional[datetime] = None) -> SyncResult:
        """Sync data from external service.

        Args:
            since: Only sync data modified since this datetime

        Returns:
            SyncResult: Result of sync operation
        """

        pass

    @abstractmethod
    async def get_records(
        self,
        limit: int = 100,
        offset: int = 0,
        since: Optional[datetime] = None
    ) -> List[DataRecord]:
        """Get records from external service.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            since: Only get records modified since this datetime

        Returns:
            List[DataRecord]: List of records
        """

        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate connector credentials.

        Returns:
            bool: True if credentials are valid, False otherwise
        """

        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get JSON schema for connector configuration.

        Returns:
            Dict: JSON schema describing required fields
        """

        pass

    async def transform_record(self, record: DataRecord) -> Dict[str, Any]:
        """Transform external record to internal format.

        Override in subclass for custom transformation.

        Args:
            record: External record

        Returns:
            Dict: Transformed record
        """

        return record.data

    async def handle_error(self, error: Exception) -> None:
        """Handle connector error.

        Override in subclass for custom error handling.

        Args:
            error: Exception that occurred
        """

        logger.error(f"Connector error: {error}", exc_info=True)

    def get_config(self) -> Dict[str, Any]:
        """Get connector configuration.

        Returns:
            Dict: Configuration
        """

        return {
            "connector_type": self.connector_type,
            "name": self.name,
            "settings": self.settings,
        }
