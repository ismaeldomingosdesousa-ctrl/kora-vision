"""Factory for creating connector instances."""

from typing import Dict, Type
import logging

from .base import BaseConnector, ConnectorConfig
from .google_calendar import GoogleCalendarConnector
from .jira import JiraConnector
from .datadog import DatadogConnector
from .dynatrace import DynatraceConnector
from .whatsapp import WhatsAppConnector

logger = logging.getLogger(__name__)


class ConnectorFactory:
    """Factory for creating connector instances."""

    _connectors: Dict[str, Type[BaseConnector]] = {
        "google_calendar": GoogleCalendarConnector,
        "jira": JiraConnector,
        "datadog": DatadogConnector,
        "dynatrace": DynatraceConnector,
        "whatsapp": WhatsAppConnector,
    }

    @classmethod
    def create(cls, config: ConnectorConfig) -> BaseConnector:
        """Create connector instance.

        Args:
            config: Connector configuration

        Returns:
            BaseConnector: Connector instance

        Raises:
            ValueError: If connector type not supported
        """

        connector_type = config.connector_type

        if connector_type not in cls._connectors:
            raise ValueError(
                f"Unsupported connector type: {connector_type}. "
                f"Supported types: {', '.join(cls._connectors.keys())}"
            )

        connector_class = cls._connectors[connector_type]
        logger.info(f"Creating connector: {connector_type}")

        return connector_class(config)

    @classmethod
    def get_supported_connectors(cls) -> Dict[str, str]:
        """Get list of supported connectors.

        Returns:
            Dict: Connector types and names
        """

        return {
            "google_calendar": "Google Calendar",
            "jira": "Jira",
            "datadog": "Datadog",
            "dynatrace": "Dynatrace",
            "whatsapp": "WhatsApp",
        }

    @classmethod
    def register_connector(
        cls,
        connector_type: str,
        connector_class: Type[BaseConnector]
    ) -> None:
        """Register new connector type.

        Args:
            connector_type: Connector type identifier
            connector_class: Connector class
        """

        cls._connectors[connector_type] = connector_class
        logger.info(f"Registered connector: {connector_type}")

    @classmethod
    def is_supported(cls, connector_type: str) -> bool:
        """Check if connector type is supported.

        Args:
            connector_type: Connector type identifier

        Returns:
            bool: True if supported, False otherwise
        """

        return connector_type in cls._connectors
