# PHASE 4 — Integration Framework (Kora Vision)

## Overview

This phase implements the **integration framework** for connecting external services, including:

1. **Base Connector Class** — Abstract interface for all integrations
2. **5 Connector Implementations** — Google Calendar, Jira, Datadog, Dynatrace, WhatsApp
3. **Connector Factory** — Dynamic connector instantiation
4. **Retry & Circuit Breaker** — Resilience patterns
5. **Rate Limiting** — API call throttling

---

## Architecture Decisions

### 1. Connector Pattern: Abstract Base Class
**Choice:** Abstract base class with concrete implementations
**Rationale:**
- Consistent interface across all connectors
- Easy to add new connectors
- Type-safe with Python typing
- Clear contract for implementations

**Base Methods:**
```python
class BaseConnector(ABC):
    async def test_connection() -> bool
    async def validate_credentials() -> bool
    async def sync(since: datetime) -> SyncResult
    async def get_records(limit, offset, since) -> List[DataRecord]
    def get_schema() -> Dict[str, Any]
    async def transform_record(record) -> Dict[str, Any]
```

### 2. Resilience: Retry + Circuit Breaker
**Choice:** Exponential backoff retry + circuit breaker pattern
**Rationale:**
- Handles transient failures
- Prevents cascading failures
- Configurable retry strategies
- Half-open state for recovery

**Retry Strategy:**
- Max 3 attempts
- Initial delay: 1 second
- Exponential backoff: 2x multiplier
- Max delay: 60 seconds
- Random jitter to prevent thundering herd

### 3. Rate Limiting: Token Bucket
**Choice:** Token bucket algorithm
**Rationale:**
- Smooth API call distribution
- Respects API rate limits
- Prevents throttling errors
- Fair request scheduling

### 4. Data Transformation: Record-based
**Choice:** Transform each record individually
**Rationale:**
- Flexible transformation logic
- Handles partial failures
- Easy to debug
- Supports streaming

---

## Connectors

### 1. Google Calendar Connector

**Purpose:** Sync calendar events

**Configuration:**
```json
{
  "access_token": "Google OAuth2 token",
  "calendar_id": "primary"
}
```

**Synced Data:**
- Event title, description
- Start/end times
- Location
- Attendees
- Recurrence rules

**API:** Google Calendar API v3

### 2. Jira Connector

**Purpose:** Sync issues and tasks

**Configuration:**
```json
{
  "host": "https://company.atlassian.net",
  "email": "user@company.com",
  "api_token": "Jira API token",
  "jql": "assignee = currentUser()"
}
```

**Synced Data:**
- Issue key and title
- Status, priority, type
- Assignee, reporter
- Created/updated timestamps
- Description

**API:** Jira REST API v3

### 3. Datadog Connector

**Purpose:** Fetch monitoring metrics

**Configuration:**
```json
{
  "api_key": "Datadog API key",
  "app_key": "Datadog app key",
  "site": "datadoghq.com",
  "query": "host:*"
}
```

**Synced Data:**
- Metric name
- Timestamp
- Value
- Tags
- Host information

**API:** Datadog Metrics API

### 4. Dynatrace Connector

**Purpose:** Fetch APM metrics

**Configuration:**
```json
{
  "environment_id": "Dynatrace environment ID",
  "api_token": "Dynatrace API token",
  "environment_url": "https://xxx.live.dynatrace.com",
  "metric_selector": "builtin:host.cpu.usage"
}
```

**Synced Data:**
- Metric name
- Timestamp
- Value
- Dimensions
- Entity information

**API:** Dynatrace Metrics API v2

### 5. WhatsApp Connector

**Purpose:** Sync messages from WhatsApp Business

**Configuration:**
```json
{
  "phone_number_id": "WhatsApp phone number ID",
  "access_token": "WhatsApp Business API token",
  "business_account_id": "Business account ID"
}
```

**Synced Data:**
- Message ID, from/to
- Timestamp
- Message type (text, image, etc.)
- Message content
- Status

**API:** WhatsApp Business API (Graph API)

---

## File Structure

```
backend/shared/connectors/
├── __init__.py                         # Package exports
├── base.py                             # Base connector class
├── factory.py                          # Connector factory
├── retry.py                            # Retry & circuit breaker
├── google_calendar.py                  # Google Calendar connector
├── jira.py                             # Jira connector
├── datadog.py                          # Datadog connector
├── dynatrace.py                        # Dynatrace connector
└── whatsapp.py                         # WhatsApp connector
```

---

## Usage Examples

### Creating a Connector

```python
from shared.connectors import ConnectorFactory, ConnectorConfig

# Create configuration
config = ConnectorConfig(
    connector_type="google_calendar",
    name="My Calendar",
    credentials={
        "access_token": "..."
    },
    settings={
        "calendar_id": "primary"
    }
)

# Create connector instance
connector = ConnectorFactory.create(config)

# Test connection
is_valid = await connector.validate_credentials()

# Sync data
result = await connector.sync()
print(f"Synced {result.records_synced} records")
```

### Getting Records

```python
from datetime import datetime, timedelta

# Get records from last hour
since = datetime.utcnow() - timedelta(hours=1)

records = await connector.get_records(
    limit=100,
    offset=0,
    since=since
)

for record in records:
    transformed = await connector.transform_record(record)
    print(transformed)
```

### Retry with Circuit Breaker

```python
from shared.connectors.retry import retry_on_exception, CircuitBreaker, RetryConfig

# Configure retry
retry_config = RetryConfig(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=60.0,
)

# Create circuit breaker
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60.0,
)

# Apply decorators
@retry_on_exception(retry_config)
@circuit_breaker
async def sync_with_resilience():
    result = await connector.sync()
    return result
```

### Rate Limiting

```python
from shared.connectors.retry import RateLimiter

# Create rate limiter (10 requests per 60 seconds)
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

# Apply decorator
@rate_limiter
async def fetch_data():
    return await connector.get_records()
```

---

## Integration Worker Implementation

### Scheduled Sync

```python
# In integration-worker/main.py

async def background_sync_loop():
    """Background loop for scheduled integration syncs."""
    
    while True:
        try:
            # Get integrations due for sync
            integrations = await get_due_integrations()
            
            for integration in integrations:
                # Create connector
                config = ConnectorConfig(
                    connector_type=integration.connector_type,
                    name=integration.name,
                    credentials=integration.credentials,
                    settings=integration.settings,
                )
                
                connector = ConnectorFactory.create(config)
                
                # Sync with retry logic
                result = await sync_with_retry(connector)
                
                # Update integration status
                await update_integration_status(integration, result)
                
                # Store records
                await store_records(integration, result)
            
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Sync loop error: {e}")
            await asyncio.sleep(60)
```

### Error Handling

```python
async def sync_with_retry(connector):
    """Sync with comprehensive error handling."""
    
    try:
        result = await connector.sync()
        
        if result.success:
            logger.info(f"Sync successful: {result.records_synced} records")
        else:
            logger.error(f"Sync failed: {result.error_message}")
            
        return result
        
    except Exception as e:
        logger.error(f"Sync exception: {e}", exc_info=True)
        return SyncResult(
            success=False,
            records_synced=0,
            error_message=str(e),
        )
```

---

## Testing Connectors

### Unit Tests

```python
import pytest
from shared.connectors import ConnectorFactory, ConnectorConfig

@pytest.mark.asyncio
async def test_google_calendar_connector():
    """Test Google Calendar connector."""
    
    config = ConnectorConfig(
        connector_type="google_calendar",
        name="Test Calendar",
        credentials={
            "access_token": "test-token"
        }
    )
    
    connector = ConnectorFactory.create(config)
    
    # Test validation
    is_valid = await connector.validate_credentials()
    assert isinstance(is_valid, bool)
    
    # Test schema
    schema = connector.get_schema()
    assert "properties" in schema
    assert "access_token" in schema["properties"]
```

### Integration Tests

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_google_calendar_sync():
    """Test Google Calendar sync with real API."""
    
    config = ConnectorConfig(
        connector_type="google_calendar",
        name="Test Calendar",
        credentials={
            "access_token": os.getenv("GOOGLE_CALENDAR_TOKEN")
        }
    )
    
    connector = ConnectorFactory.create(config)
    result = await connector.sync()
    
    assert result.success
    assert result.records_synced > 0
```

---

## Adding New Connectors

### Step 1: Create Connector Class

```python
# backend/shared/connectors/my_service.py

from .base import BaseConnector, ConnectorConfig, SyncResult, DataRecord

class MyServiceConnector(BaseConnector):
    """Connector for My Service."""
    
    CONNECTOR_TYPE = "my_service"
    
    async def test_connection(self) -> bool:
        # Implement connection test
        pass
    
    async def validate_credentials(self) -> bool:
        # Implement credential validation
        pass
    
    async def sync(self, since: Optional[datetime] = None) -> SyncResult:
        # Implement sync logic
        pass
    
    async def get_records(self, limit, offset, since) -> List[DataRecord]:
        # Implement record retrieval
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        # Return JSON schema for configuration
        pass
```

### Step 2: Register Connector

```python
# In shared/connectors/__init__.py

from .my_service import MyServiceConnector

ConnectorFactory.register_connector("my_service", MyServiceConnector)
```

### Step 3: Test Connector

```bash
# Run tests
pytest tests/test_my_service_connector.py

# Test manually
python -c "
from shared.connectors import ConnectorFactory, ConnectorConfig

config = ConnectorConfig(
    connector_type='my_service',
    name='Test',
    credentials={'api_key': 'xxx'}
)

connector = ConnectorFactory.create(config)
print(connector.get_schema())
"
```

---

## Monitoring & Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("shared.connectors")
```

### Monitor Sync Status

```bash
# Get sync status for integration
curl http://localhost:8002/sync/{integration_id}/status

# Response
{
  "integration_id": "uuid",
  "status": "idle",
  "last_sync_at": "2026-03-20T10:30:00Z",
  "next_sync_at": "2026-03-20T11:00:00Z",
  "records_synced": 42,
  "error_message": null
}
```

### View Connector Logs

```bash
# View logs for connector
aws logs tail /ecs/unified-ops-hub-integration-worker-dev --follow

# Filter for specific connector
aws logs filter-log-events \
  --log-group-name /ecs/unified-ops-hub-integration-worker-dev \
  --filter-pattern "google_calendar"
```

---

## Performance Optimization

### Batch Processing

```python
# Process records in batches
batch_size = 100
for i in range(0, len(records), batch_size):
    batch = records[i:i + batch_size]
    await store_batch(batch)
```

### Parallel Syncs

```python
# Sync multiple integrations in parallel
import asyncio

tasks = [
    sync_with_retry(connector)
    for connector in connectors
]

results = await asyncio.gather(*tasks)
```

### Caching

```python
# Cache connector instances
connector_cache = {}

def get_connector(integration_id):
    if integration_id not in connector_cache:
        config = load_config(integration_id)
        connector_cache[integration_id] = ConnectorFactory.create(config)
    return connector_cache[integration_id]
```

---

## Validation Checklist

After Phase 4 deployment:

- [ ] **All connectors created**
  ```bash
  python -c "from shared.connectors import ConnectorFactory; print(ConnectorFactory.get_supported_connectors())"
  ```

- [ ] **Connector factory works**
  ```bash
  python -c "from shared.connectors import ConnectorFactory, ConnectorConfig; c = ConnectorFactory.create(ConnectorConfig('google_calendar', 'test', {}))"
  ```

- [ ] **Retry logic functions**
  ```bash
  pytest tests/test_retry.py
  ```

- [ ] **Circuit breaker works**
  ```bash
  pytest tests/test_circuit_breaker.py
  ```

- [ ] **Rate limiter works**
  ```bash
  pytest tests/test_rate_limiter.py
  ```

- [ ] **Integration worker syncs**
  ```bash
  curl -X POST http://localhost:8002/sync/{integration_id}
  ```

- [ ] **Connector tests pass**
  ```bash
  pytest tests/test_connectors.py
  ```

---

## Next Steps

**Phase 4 Complete.** Awaiting approval to proceed to **Phase 5 — Frontend & Dashboard**.

Please confirm:
1. ✅ All 5 connectors implemented correctly?
2. ✅ Retry and circuit breaker patterns working?
3. ✅ Rate limiting functional?
4. ✅ Integration worker can sync data?
5. ✅ Ready to proceed with React frontend?

**Reply "APROVADO" or provide feedback for adjustments.**
