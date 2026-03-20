# PHASE 3 — Backend Core (Kora Vision)

## Overview

This phase implements the **backend core services** using FastAPI, including:

1. **Core API Service** — Main REST API for dashboard, user, and integration management
2. **Webhook Ingestor Service** — Receives and processes webhooks from external services
3. **Integration Worker Service** — Syncs data from external integrations
4. **Real-time Service** — WebSocket server for live dashboard updates

---

## Architecture Decisions

### 1. Framework: FastAPI
**Choice:** FastAPI for async Python backend
**Rationale:**
- High performance (async/await)
- Automatic OpenAPI documentation
- Built-in validation (Pydantic)
- Easy deployment with Uvicorn
- Great for microservices architecture

**Alternatives Rejected:**
- Django: Too heavy for microservices
- Flask: Lacks async support
- Go/Rust: Different language stack

### 2. Service Architecture: Microservices
**Choice:** 4 independent FastAPI services
**Rationale:**
- Independent scaling
- Fault isolation
- Different deployment strategies
- Clear separation of concerns

**Services:**
- **core-api** (Port 8000): REST API for CRUD operations
- **webhook-ingestor** (Port 8001): Webhook receiver
- **integration-worker** (Port 8002): Background sync jobs
- **realtime-service** (Port 8003): WebSocket server

### 3. Authentication: JWT + Cognito
**Choice:** JWT tokens with Cognito integration
**Rationale:**
- Stateless authentication
- Scalable across services
- AWS native integration
- Support for MFA

**Flow:**
1. User logs in via Cognito
2. Cognito returns JWT token
3. Client includes JWT in Authorization header
4. Backend validates JWT signature
5. Extract tenant_id and user_id from token

### 4. Database Access: SQLAlchemy ORM
**Choice:** SQLAlchemy with async support
**Rationale:**
- Type-safe queries
- Migration support (Alembic)
- Multi-database support
- Async support with asyncpg

### 5. Real-time Communication: WebSocket
**Choice:** WebSocket for live updates
**Rationale:**
- Low latency (< 500ms)
- Bidirectional communication
- Efficient for high-frequency updates
- Native browser support

---

## Service Details

### Core API Service

**Responsibilities:**
- User authentication and authorization
- Tenant management
- Dashboard CRUD operations
- Widget management
- Integration configuration
- Webhook registration

**Key Endpoints:**
```
GET    /health                          # Health check
POST   /auth/token                      # Login
GET    /auth/me                         # Current user
GET    /tenants                         # List tenants
GET    /tenants/{id}                    # Get tenant
GET    /users                           # List users
POST   /users                           # Create user
GET    /dashboards                      # List dashboards
POST   /dashboards                      # Create dashboard
GET    /dashboards/{id}                 # Get dashboard
GET    /integrations                    # List integrations
POST   /integrations                    # Create integration
POST   /webhooks/register               # Register webhook
```

### Webhook Ingestor Service

**Responsibilities:**
- Receive webhooks from external services
- Validate webhook signatures
- Deduplicate events
- Publish to event queue
- Return immediate acknowledgment

**Key Endpoints:**
```
GET    /health                          # Health check
POST   /webhooks/{tenant_id}/{integration_id}  # Receive webhook
POST   /webhooks/test                   # Test webhook
```

### Integration Worker Service

**Responsibilities:**
- Sync data from external integrations
- Schedule periodic syncs
- Handle retry logic
- Transform and store data
- Update sync status

**Key Endpoints:**
```
GET    /health                          # Health check
POST   /sync/{integration_id}           # Trigger sync
GET    /sync/{integration_id}/status    # Get sync status
GET    /connectors                      # List connectors
POST   /connectors/{type}/test          # Test connector
```

### Real-time Service

**Responsibilities:**
- Accept WebSocket connections
- Broadcast events to clients
- Manage subscriptions
- Handle connection lifecycle
- Send keep-alive pings

**Key Endpoints:**
```
GET    /health                          # Health check
WS     /ws/{tenant_id}                  # WebSocket connection
POST   /broadcast/{tenant_id}           # Broadcast message
GET    /stats                           # Service statistics
```

---

## File Structure

```
backend/
├── shared/
│   ├── __init__.py
│   ├── config.py                       # Configuration management
│   ├── auth.py                         # JWT and Cognito integration
│   ├── database.py                     # Database connection
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py                     # Base SQLAlchemy models
│   └── schemas/
│       ├── __init__.py
│       ├── tenant.py                   # Tenant schemas
│       └── user.py                     # User schemas
│
├── core-api/
│   ├── __init__.py
│   └── main.py                         # Core API application
│
├── webhook-ingestor/
│   ├── __init__.py
│   └── main.py                         # Webhook ingestor application
│
├── integration-worker/
│   ├── __init__.py
│   └── main.py                         # Integration worker application
│
├── realtime-service/
│   ├── __init__.py
│   └── main.py                         # Real-time service application
│
├── migrations/
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   ├── schema.sql
│   └── versions/
│       └── 001_initial_schema.py
│
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variables template
└── docker-compose.yml                  # Local development setup
```

---

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
nano .env
```

**Key environment variables:**
```
# Database
DATABASE_URL=postgresql://admin:password@localhost:5432/unifiedopshub

# Redis
REDIS_URL=redis://localhost:6379/0

# Cognito
COGNITO_USER_POOL_ID=us-east-1_xxxxx
COGNITO_CLIENT_ID=xxxxx
COGNITO_CLIENT_SECRET=xxxxx

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
```

### Step 3: Run Migrations

```bash
cd migrations

# Apply migrations
alembic upgrade head

# Verify
alembic current
```

### Step 4: Start Services (Development)

**Option A: Using Docker Compose**

```bash
# Build images
docker-compose build

# Start all services
docker-compose up

# Services will be available at:
# - Core API: http://localhost:8000
# - Webhook Ingestor: http://localhost:8001
# - Integration Worker: http://localhost:8002
# - Real-time Service: http://localhost:8003
```

**Option B: Manual (for development)**

```bash
# Terminal 1: Core API
python -m uvicorn core-api.main:app --reload --port 8000

# Terminal 2: Webhook Ingestor
python -m uvicorn webhook-ingestor.main:app --reload --port 8001

# Terminal 3: Integration Worker
python -m uvicorn integration-worker.main:app --reload --port 8002

# Terminal 4: Real-time Service
python -m uvicorn realtime-service.main:app --reload --port 8003 --workers 1
```

### Step 5: Verify Services

```bash
# Check health of all services
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health

# View API documentation
# - Core API: http://localhost:8000/docs
# - Webhook Ingestor: http://localhost:8001/docs
# - Integration Worker: http://localhost:8002/docs
# - Real-time Service: http://localhost:8003/docs
```

---

## Docker Deployment

### Build Docker Images

```bash
# Build core-api image
docker build -f infrastructure/docker/core-api.Dockerfile -t unified-ops-hub/core-api:latest .

# Build webhook-ingestor image
docker build -f infrastructure/docker/webhook-ingestor.Dockerfile -t unified-ops-hub/webhook-ingestor:latest .

# Build integration-worker image
docker build -f infrastructure/docker/integration-worker.Dockerfile -t unified-ops-hub/integration-worker:latest .

# Build realtime-service image
docker build -f infrastructure/docker/realtime-service.Dockerfile -t unified-ops-hub/realtime-service:latest .
```

### Push to ECR

```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag images
docker tag unified-ops-hub/core-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/unified-ops-hub/core-api:latest

# Push images
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/unified-ops-hub/core-api:latest
```

---

## API Examples

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}

# Use token in subsequent requests
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

### Create Dashboard

```bash
curl -X POST http://localhost:8000/dashboards \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Dashboard",
    "description": "Dashboard for monitoring"
  }'
```

### Create Integration

```bash
curl -X POST http://localhost:8000/integrations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "connector_type": "google_calendar",
    "name": "My Calendar",
    "credentials": {
      "access_token": "..."
    }
  }'
```

### WebSocket Connection

```javascript
// JavaScript client
const ws = new WebSocket('ws://localhost:8003/ws/tenant-uuid');

ws.onopen = () => {
  console.log('Connected');
  ws.send(JSON.stringify({ type: 'ping' }));
};

ws.onmessage = (event) => {
  console.log('Message:', JSON.parse(event.data));
};

ws.onerror = (error) => {
  console.error('Error:', error);
};
```

---

## Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_create_access_token
```

### Integration Tests

```bash
# Run integration tests
pytest -m integration

# With verbose output
pytest -v -m integration
```

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# Using wrk
wrk -t4 -c100 -d30s http://localhost:8000/health
```

---

## Monitoring & Logging

### CloudWatch Logs

```bash
# View logs for core-api
aws logs tail /ecs/unified-ops-hub-core-api-dev --follow

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/unified-ops-hub-core-api-dev \
  --filter-pattern "ERROR"
```

### Metrics

```bash
# Get CPU utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --start-time 2026-03-20T00:00:00Z \
  --end-time 2026-03-20T23:59:59Z \
  --period 3600 \
  --statistics Average
```

---

## Troubleshooting

### Issue: Database Connection Failed

```bash
# Check database connectivity
psql -h $RDS_ENDPOINT -U admin -d unifiedopshub -c "SELECT 1"

# Check environment variable
echo $DATABASE_URL

# Verify credentials in Secrets Manager
aws secretsmanager get-secret-value --secret-id unified-ops-hub/db-password-dev
```

### Issue: JWT Validation Failed

```bash
# Check JWT secret
echo $JWT_SECRET_KEY

# Decode JWT (online tool or jwt-cli)
jwt decode <token>

# Verify token expiration
jwt decode <token> | grep exp
```

### Issue: WebSocket Connection Refused

```bash
# Check if realtime-service is running
curl http://localhost:8003/health

# Check port binding
netstat -tlnp | grep 8003

# Check firewall rules
sudo ufw status
```

---

## Performance Optimization

### Database Connection Pooling

```python
# Configured in shared/database.py
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
```

### Caching Strategy

```python
# Cache frequently accessed data
# - User roles and permissions
# - Tenant settings
# - Integration status
# Use Redis with TTL
```

### Query Optimization

```sql
-- Use indexes for common queries
SELECT * FROM users WHERE tenant_id = ? AND email = ?;

-- Use EXPLAIN to analyze queries
EXPLAIN ANALYZE SELECT * FROM dashboards WHERE tenant_id = ?;
```

---

## Validation Checklist

After Phase 3 deployment:

- [ ] **All services start successfully**
  ```bash
  curl http://localhost:8000/health
  curl http://localhost:8001/health
  curl http://localhost:8002/health
  curl http://localhost:8003/health
  ```

- [ ] **Database migrations applied**
  ```bash
  alembic current
  ```

- [ ] **JWT authentication works**
  ```bash
  curl -X POST http://localhost:8000/auth/token
  ```

- [ ] **WebSocket connection works**
  ```bash
  wscat -c ws://localhost:8003/ws/tenant-uuid
  ```

- [ ] **Docker images build successfully**
  ```bash
  docker build -f infrastructure/docker/core-api.Dockerfile .
  ```

- [ ] **Tests pass**
  ```bash
  pytest
  ```

- [ ] **API documentation accessible**
  - http://localhost:8000/docs
  - http://localhost:8001/docs
  - http://localhost:8002/docs
  - http://localhost:8003/docs

---

## Next Steps

**Phase 3 Complete.** Awaiting approval to proceed to **Phase 4 — Integration Framework**.

Please confirm:
1. ✅ All 4 backend services running successfully?
2. ✅ JWT authentication working?
3. ✅ WebSocket connections established?
4. ✅ Docker images build and run?
5. ✅ Ready to proceed with connector implementations?

**Reply "APROVADO" or provide feedback for adjustments.**
