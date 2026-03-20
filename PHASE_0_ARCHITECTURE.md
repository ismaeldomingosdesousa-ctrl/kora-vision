# PHASE 0 — Architecture Definition

## Unified Personal Operations Hub — SaaS Platform

**Project Objective:** Create a multi-tenant SaaS platform that aggregates integrations (WhatsApp, Jira, Google Calendar, Datadog, Dynatrace, etc.) into customizable dashboards accessible via Web and Mobile.

---

## 1. System Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  Web (Next.js + TypeScript)  │  Mobile (Expo React Native)      │
│  ├─ Dashboard                │  ├─ Dashboard                    │
│  ├─ Widget System            │  ├─ Widget System                │
│  ├─ Settings                 │  ├─ Settings                     │
│  └─ Real-time Updates        │  └─ Real-time Updates            │
└──────────────┬────────────────────────────────┬──────────────────┘
               │                                │
        ┌──────▼────────────────────────────────▼──────┐
        │         API GATEWAY (ALB + CloudFront)       │
        │  ├─ TLS/SSL Termination                      │
        │  ├─ Request Routing                          │
        │  └─ Rate Limiting                            │
        └──────┬────────────────────────────────┬──────┘
               │                                │
        ┌──────▼──────────────────────────────▼───────────────────┐
        │           BACKEND SERVICES (ECS Fargate)                │
        ├────────────────────────────────────────────────────────┤
        │  Core API Service                                       │
        │  ├─ Tenant Management                                   │
        │  ├─ User Authentication (Cognito)                       │
        │  ├─ Dashboard CRUD                                      │
        │  ├─ Widget Configuration                                │
        │  └─ Webhook Registration                                │
        │                                                          │
        │  Integration Worker Service                             │
        │  ├─ Connector Orchestration                             │
        │  ├─ Sync Scheduling                                     │
        │  ├─ Data Transformation                                 │
        │  └─ Error Handling & Retry Logic                        │
        │                                                          │
        │  Webhook Ingestor Service                               │
        │  ├─ Event Reception                                     │
        │  ├─ Validation & Deduplication                          │
        │  ├─ Event Publishing (SQS/EventBridge)                  │
        │  └─ Acknowledgment                                      │
        │                                                          │
        │  Real-time Service (WebSocket/SSE)                      │
        │  ├─ Client Connection Management                        │
        │  ├─ Event Broadcasting                                  │
        │  └─ Presence Tracking                                   │
        └──────┬──────────────────────────────┬────────────────────┘
               │                              │
        ┌──────▼──────────────────────────────▼───────────────────┐
        │              DATA LAYER                                 │
        ├────────────────────────────────────────────────────────┤
        │  Aurora PostgreSQL Serverless v2                        │
        │  ├─ Tenants & Users                                     │
        │  ├─ Dashboards & Widgets                                │
        │  ├─ Integrations & Credentials                          │
        │  ├─ Events & Audit Logs                                 │
        │  └─ Multi-tenant Isolation (Row-Level Security)         │
        │                                                          │
        │  ElastiCache (Redis)                                    │
        │  ├─ Session Store                                       │
        │  ├─ Cache Layer                                         │
        │  ├─ Real-time Subscriptions                             │
        │  └─ Rate Limit Counters                                 │
        │                                                          │
        │  S3 Buckets                                             │
        │  ├─ Frontend Assets (CloudFront CDN)                    │
        │  ├─ Integration Logs & Backups                          │
        │  └─ User-generated Content                              │
        │                                                          │
        │  Secrets Manager                                        │
        │  └─ API Keys, Credentials, Encryption Keys              │
        └────────────────────────────────────────────────────────┘
               │
        ┌──────▼──────────────────────────────────────────────────┐
        │         EXTERNAL INTEGRATIONS                           │
        ├────────────────────────────────────────────────────────┤
        │  ├─ Google Calendar (OAuth 2.0)                         │
        │  ├─ Jira (API Token)                                    │
        │  ├─ Datadog (API Key)                                   │
        │  ├─ Dynatrace (API Token)                               │
        │  ├─ WhatsApp (Business API)                             │
        │  └─ [Extensible Connector Framework]                    │
        └────────────────────────────────────────────────────────┘
```

---

## 2. Service Boundaries

### Core Services

| Service | Responsibility | Technology | Scaling |
|---------|---|---|---|
| **Core API** | User auth, tenant mgmt, dashboard CRUD, webhooks | FastAPI + Python | Horizontal (ECS) |
| **Integration Worker** | Connector sync, data transformation, scheduling | FastAPI + Celery | Horizontal (ECS + SQS) |
| **Webhook Ingestor** | Event reception, validation, publishing | FastAPI + async | Horizontal (ECS) |
| **Real-time Service** | WebSocket/SSE, event broadcasting | FastAPI + WebSocket | Horizontal (ECS) |
| **Frontend Web** | Dashboard UI, widget management | Next.js + TypeScript | Static (S3 + CloudFront) |
| **Mobile App** | Dashboard UI for iOS/Android | Expo React Native | App Store/Play Store |

### Service Communication Patterns

- **Synchronous:** REST API (Core API ↔ Clients)
- **Asynchronous:** AWS SQS/EventBridge (Services ↔ Event Processing)
- **Real-time:** WebSocket (Real-time Service ↔ Clients)
- **Scheduled:** EventBridge Rules (Connector Sync Scheduling)

---

## 3. AWS Services Mapping

| Component | AWS Service | Purpose |
|-----------|---|---|
| **Compute** | ECS Fargate | Containerized backend services |
| **Container Registry** | ECR | Docker image storage |
| **Load Balancing** | ALB | Request routing, TLS termination |
| **CDN** | CloudFront | Frontend asset delivery |
| **Storage** | S3 | Frontend assets, logs, backups |
| **Database** | Aurora PostgreSQL Serverless v2 | Multi-tenant data store |
| **Cache** | ElastiCache (Redis) | Session store, cache layer |
| **Secrets** | Secrets Manager | Credential management |
| **Authentication** | Cognito | User identity & access |
| **DNS** | Route53 | Domain management |
| **SSL/TLS** | ACM | Certificate management |
| **Messaging** | SQS | Async task queues |
| **Events** | EventBridge | Event routing & scheduling |
| **Monitoring** | CloudWatch | Logs, metrics, alarms |
| **Infrastructure** | Terraform | IaC provisioning |

---

## 4. Multi-Tenant Strategy

### Tenant Isolation Model: **Row-Level Security (RLS)**

**Approach:** Database-level isolation using PostgreSQL Row-Level Security policies.

**Benefits:**
- Strong isolation guarantee at the database layer
- Efficient resource sharing (single database instance)
- Simplified backup/restore per tenant
- Cost-effective for thousands of tenants

**Implementation:**
- Every table includes `tenant_id` column
- PostgreSQL RLS policies enforce `tenant_id` filtering
- Application sets `app.current_tenant_id` context variable
- Queries automatically filtered by tenant context

**Tables with RLS:**
- `users` (tenant_id)
- `dashboards` (tenant_id)
- `widgets` (tenant_id)
- `integrations` (tenant_id)
- `events` (tenant_id)
- `audit_logs` (tenant_id)

### Tenant Onboarding Flow

1. **Sign-up** → Cognito creates user
2. **Tenant Creation** → API creates tenant record
3. **Workspace Setup** → Default dashboard + widgets created
4. **Integration Configuration** → User connects external services
5. **Dashboard Customization** → User arranges widgets

---

## 5. Event Model Definition

### Event Types

```
EventType (enum):
├─ INTEGRATION_SYNC_STARTED
├─ INTEGRATION_SYNC_COMPLETED
├─ INTEGRATION_SYNC_FAILED
├─ WEBHOOK_RECEIVED
├─ DASHBOARD_UPDATED
├─ WIDGET_ADDED
├─ WIDGET_REMOVED
├─ USER_INVITED
├─ TENANT_SETTINGS_CHANGED
└─ ALERT_TRIGGERED
```

### Event Schema

```json
{
  "event_id": "uuid",
  "event_type": "INTEGRATION_SYNC_COMPLETED",
  "tenant_id": "uuid",
  "user_id": "uuid",
  "timestamp": "2026-03-20T10:30:00Z",
  "source": "integration-worker",
  "data": {
    "integration_id": "uuid",
    "connector_type": "google_calendar",
    "sync_duration_ms": 1234,
    "records_synced": 42,
    "status": "success"
  },
  "metadata": {
    "trace_id": "uuid",
    "request_id": "uuid"
  }
}
```

### Event Flow

```
External Service (Webhook)
        ↓
Webhook Ingestor Service
        ↓
Validate & Deduplicate
        ↓
AWS SQS / EventBridge
        ↓
Event Processing (Workers)
        ↓
Database Update
        ↓
Real-time Service (WebSocket)
        ↓
Client Dashboard (Live Update)
```

---

## 6. Repository Structure

```
unified-ops-hub/
├── infrastructure/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── terraform.tfvars
│   │   ├── modules/
│   │   │   ├── vpc/
│   │   │   ├── ecs/
│   │   │   ├── rds/
│   │   │   ├── elasticache/
│   │   │   ├── s3/
│   │   │   ├── alb/
│   │   │   ├── cloudfront/
│   │   │   ├── route53/
│   │   │   └── secrets/
│   │   └── environments/
│   │       ├── dev/
│   │       ├── staging/
│   │       └── prod/
│   └── docker/
│       ├── core-api.Dockerfile
│       ├── integration-worker.Dockerfile
│       ├── webhook-ingestor.Dockerfile
│       └── realtime-service.Dockerfile
│
├── backend/
│   ├── core-api/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── routes/
│   │   │   ├── services/
│   │   │   ├── middleware/
│   │   │   └── utils/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── integration-worker/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── connectors/
│   │   │   │   ├── base.py
│   │   │   │   ├── google_calendar.py
│   │   │   │   ├── jira.py
│   │   │   │   ├── datadog.py
│   │   │   │   └── dynatrace.py
│   │   │   ├── tasks/
│   │   │   ├── services/
│   │   │   └── utils/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── webhook-ingestor/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── handlers/
│   │   │   ├── services/
│   │   │   └── utils/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── realtime-service/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── websocket/
│   │   │   ├── services/
│   │   │   └── utils/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── shared/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── utils/
│   │   └── requirements.txt
│   │
│   └── migrations/
│       ├── versions/
│       ├── env.py
│       └── script.py.mako
│
├── frontend/
│   ├── web/
│   │   ├── app/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── styles/
│   │   ├── lib/
│   │   ├── public/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── next.config.js
│   │   └── .env.local
│   │
│   └── mobile/
│       ├── app/
│       ├── components/
│       ├── screens/
│       ├── navigation/
│       ├── package.json
│       ├── app.json
│       └── eas.json
│
├── .github/
│   └── workflows/
│       ├── backend-ci.yml
│       ├── frontend-ci.yml
│       ├── mobile-ci.yml
│       └── terraform-apply.yml
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── CONNECTOR_GUIDE.md
│
├── docker-compose.yml (local development)
├── .env.example
├── .gitignore
└── README.md
```

---

## 7. Key Architectural Decisions

### Decision 1: Multi-Tenant Isolation Strategy
**Choice:** Row-Level Security (RLS) at database layer
**Rationale:** Provides strong isolation guarantee, cost-effective for thousands of tenants, simplified operations.
**Alternative Rejected:** Separate databases per tenant (operational complexity, cost scaling).

### Decision 2: Real-time Communication
**Choice:** WebSocket for real-time dashboard updates
**Rationale:** Low-latency, bidirectional communication, suitable for live event streaming.
**Alternative Rejected:** Server-Sent Events (SSE) — less efficient for high-frequency updates.

### Decision 3: Asynchronous Task Processing
**Choice:** AWS SQS + EventBridge for event-driven architecture
**Rationale:** Decouples services, enables horizontal scaling, built-in retry logic.
**Alternative Rejected:** Direct service-to-service calls (tight coupling, less resilient).

### Decision 4: Container Orchestration
**Choice:** ECS Fargate (serverless containers)
**Rationale:** No infrastructure management, auto-scaling, cost-effective for variable workloads.
**Alternative Rejected:** Kubernetes (operational overhead for this scale).

### Decision 5: Frontend Deployment
**Choice:** Static hosting (S3 + CloudFront) for Next.js
**Rationale:** High availability, low latency, cost-effective CDN distribution.
**Alternative Rejected:** EC2-based deployment (higher operational overhead).

---

## 8. Scalability Assumptions

- **Target:** Thousands of tenants, millions of events/day
- **Concurrent Users:** 10,000+ concurrent dashboard viewers
- **Event Throughput:** 100,000+ events/day
- **Integration Sync Frequency:** Every 5-60 minutes per connector
- **Real-time Latency SLA:** <500ms event-to-dashboard update

---

## 9. Security Considerations

- **Authentication:** AWS Cognito (OAuth 2.0, MFA support)
- **Authorization:** JWT tokens + RLS policies
- **Encryption:** TLS in transit, KMS encryption at rest
- **Secrets Management:** AWS Secrets Manager (no hardcoded credentials)
- **Audit Logging:** All user actions logged to audit_logs table
- **Rate Limiting:** API Gateway + Redis-based rate limiter
- **CORS:** Configured per environment
- **DDoS Protection:** AWS Shield + WAF rules

---

## 10. Monitoring & Observability

- **Logs:** CloudWatch Logs (centralized)
- **Metrics:** CloudWatch Metrics (custom dashboards)
- **Tracing:** X-Ray (distributed tracing)
- **Alerting:** CloudWatch Alarms (SNS notifications)
- **Health Checks:** ECS task health checks + ALB target health

---

## Summary

This architecture provides:

✅ **Scalability:** Horizontal scaling via ECS, database auto-scaling via Aurora Serverless  
✅ **Reliability:** Multi-AZ deployment, auto-recovery, event-driven resilience  
✅ **Security:** Multi-tenant isolation at DB layer, encryption, secrets management  
✅ **Cost-Efficiency:** Serverless components, pay-per-use pricing, resource optimization  
✅ **Developer Experience:** Clear service boundaries, async patterns, local development support  

---

## Next Steps

**Phase 0 Complete.** Awaiting approval to proceed to **Phase 1 — Infrastructure Foundation (Terraform)**.

Please confirm:
1. ✅ Architecture approach is acceptable?
2. ✅ Service boundaries are clear?
3. ✅ Multi-tenant strategy aligns with requirements?
4. ✅ Ready to proceed with Terraform provisioning?

**Reply "APPROVED" or provide feedback for adjustments.**
