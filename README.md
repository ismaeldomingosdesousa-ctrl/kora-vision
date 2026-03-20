# Kora Vision

Um **SaaS multi-tenant** completo para centralizar e gerenciar operações pessoais, integrando calendários, tarefas, métricas e notificações em um único dashboard inteligente.

---

## 📋 Visão Geral do Projeto

O **Kora Vision** é uma plataforma SaaS que permite aos usuários:

- **Unificar serviços** — Integre Google Calendar, Jira, Datadog, Dynatrace e WhatsApp
- **Criar dashboards** — Customize dashboards com widgets personalizados
- **Sincronizar dados** — Sincronização automática e em tempo real
- **Monitorar operações** — Acompanhe métricas, tarefas e eventos
- **Receber notificações** — Alertas via WhatsApp e outros canais

---

## 🏗️ Arquitetura

### Stack Tecnológico

| Camada | Tecnologia | Componentes |
|--------|-----------|-------------|
| **Frontend** | React 19 + TypeScript | Landing, Dashboard, Integrations |
| **Backend** | FastAPI + Python | Core API, Webhook, Worker, Real-time |
| **Database** | PostgreSQL + Alembic | Multi-tenant com RLS |
| **Cache** | Redis | Session, rate limiting |
| **Infraestrutura** | AWS + Terraform | VPC, ECS, RDS, ElastiCache, CloudFront |
| **Integrações** | 5 Conectores | Google Calendar, Jira, Datadog, Dynatrace, WhatsApp |

### Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│  Landing Page │ Dashboard │ Integrations │ Settings          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────────────────┐
│              API Gateway (ALB)                               │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼─────────┐ ┌───▼──────────┐
│  Core API      │ │ Webhook      │ │ Real-time    │
│  (8000)        │ │ Ingestor     │ │ Service      │
│                │ │ (8001)       │ │ (8003)       │
└────────────────┘ └──────────────┘ └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼──────────┐ ┌──▼────────────┐
│  PostgreSQL    │ │  Redis        │ │ Integration   │
│  (RLS)         │ │  (Cache)      │ │ Worker        │
└────────────────┘ └───────────────┘ └───────────────┘
        │
        └─ External APIs (Google, Jira, Datadog, etc.)
```

---

## 📁 Estrutura de Diretórios

```
kora-vision/
├── PHASE_0_ARCHITECTURE.md              # Definição arquitetural
├── PHASE_1_INFRASTRUCTURE.md            # Terraform
├── PHASE_2_DATA_LAYER.md                # Schema PostgreSQL
├── PHASE_3_BACKEND_CORE.md              # FastAPI services
├── PHASE_4_INTEGRATION_FRAMEWORK.md     # Conectores
├── PHASE_5_FRONTEND_DASHBOARD.md        # React frontend
│
├── infrastructure/
│   ├── terraform/                       # IaC
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── modules/
│   │       ├── vpc/
│   │       ├── security_groups/
│   │       ├── alb/
│   │       ├── ecs/
│   │       ├── rds/
│   │       ├── elasticache/
│   │       ├── s3/
│   │       ├── cloudfront/
│   │       ├── route53/
│   │       ├── secrets/
│   │       └── cloudwatch/
│   │
│   └── docker/
│       ├── core-api.Dockerfile
│       ├── webhook-ingestor.Dockerfile
│       ├── integration-worker.Dockerfile
│       └── realtime-service.Dockerfile
│
├── backend/
│   ├── requirements.txt
│   ├── migrations/
│   │   ├── alembic.ini
│   │   ├── env.py
│   │   ├── schema.sql
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   │
│   ├── shared/
│   │   ├── config.py
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   └── base.py
│   │   ├── schemas/
│   │   │   ├── tenant.py
│   │   │   └── user.py
│   │   └── connectors/
│   │       ├── base.py
│   │       ├── factory.py
│   │       ├── retry.py
│   │       ├── google_calendar.py
│   │       ├── jira.py
│   │       ├── datadog.py
│   │       ├── dynatrace.py
│   │       └── whatsapp.py
│   │
│   ├── core-api/
│   │   └── main.py
│   ├── webhook-ingestor/
│   │   └── main.py
│   ├── integration-worker/
│   │   └── main.py
│   └── realtime-service/
│       └── main.py
│
└── frontend/
    └── kora-vision-frontend/            # Projeto React (separado)
        ├── client/
        │   ├── src/
        │   │   ├── components/
        │   │   │   ├── DashboardLayout.tsx
        │   │   │   ├── DashboardCard.tsx
        │   │   │   └── ui/
        │   │   ├── pages/
        │   │   │   ├── Home.tsx
        │   │   │   ├── Dashboard.tsx
        │   │   │   ├── Integrations.tsx
        │   │   │   └── NotFound.tsx
        │   │   ├── hooks/
        │   │   ├── lib/
        │   │   ├── contexts/
        │   │   ├── App.tsx
        │   │   └── index.css
        │   └── index.html
        └── package.json
```

---

## 🚀 Começando

### Pré-requisitos

- **AWS Account** com credenciais configuradas
- **Terraform** >= 1.0
- **Docker** e **Docker Compose**
- **Python** 3.11+
- **Node.js** 22+
- **PostgreSQL** 15+

### 1. Provisionar Infraestrutura

```bash
cd infrastructure/terraform

# Inicializar Terraform
terraform init

# Copiar arquivo de exemplo
cp terraform.tfvars.example terraform.tfvars

# Editar variáveis
nano terraform.tfvars

# Planejar e aplicar
terraform plan
terraform apply
```

### 2. Executar Migrations

```bash
cd backend/migrations

# Configurar variáveis de ambiente
export DATABASE_URL="postgresql://admin:password@host:5432/unifiedopshub"

# Aplicar migrations
alembic upgrade head
```

### 3. Iniciar Backend Services

```bash
cd backend

# Instalar dependências
pip install -r requirements.txt

# Iniciar serviços (em terminais separados)
python -m uvicorn core-api.main:app --reload --port 8000
python -m uvicorn webhook-ingestor.main:app --reload --port 8001
python -m uvicorn integration-worker.main:app --reload --port 8002
python -m uvicorn realtime-service.main:app --reload --port 8003
```

### 4. Iniciar Frontend

```bash
cd frontend/unified-ops-hub-frontend

# Instalar dependências
npm install

# Iniciar dev server
npm run dev

# Acessar em http://localhost:3000
```

---

## 🔌 Conectores Suportados

### 1. Google Calendar

**Sincroniza:** Eventos, horários, participantes

**Configuração:**
```json
{
  "access_token": "Google OAuth2 token",
  "calendar_id": "primary"
}
```

### 2. Jira

**Sincroniza:** Issues, status, assignee

**Configuração:**
```json
{
  "host": "https://company.atlassian.net",
  "email": "user@company.com",
  "api_token": "Jira API token",
  "jql": "assignee = currentUser()"
}
```

### 3. Datadog

**Sincroniza:** Métricas, tags, hosts

**Configuração:**
```json
{
  "api_key": "Datadog API key",
  "app_key": "Datadog app key",
  "site": "datadoghq.com",
  "query": "host:*"
}
```

### 4. Dynatrace

**Sincroniza:** Métricas APM, dimensões

**Configuração:**
```json
{
  "environment_id": "Dynatrace environment ID",
  "api_token": "Dynatrace API token",
  "environment_url": "https://xxx.live.dynatrace.com",
  "metric_selector": "builtin:host.cpu.usage"
}
```

### 5. WhatsApp

**Sincroniza:** Mensagens, status

**Configuração:**
```json
{
  "phone_number_id": "WhatsApp phone number ID",
  "access_token": "WhatsApp Business API token",
  "business_account_id": "Business account ID"
}
```

---

## 🔐 Segurança

### Multi-tenant Isolation

- **Row-Level Security (RLS)** no PostgreSQL
- Isolamento automático por tenant_id
- Queries filtradas automaticamente

### Autenticação

- **JWT tokens** com Cognito
- Validação em cada request
- Refresh tokens com TTL

### Criptografia

- **TLS 1.3** em trânsito
- **KMS** para dados em repouso
- **HMAC-SHA256** para webhooks

### Rate Limiting

- Token bucket algorithm
- Configurável por endpoint
- Proteção contra DDoS

---

## 📊 Monitoramento

### CloudWatch Logs

```bash
# Ver logs do Core API
aws logs tail /ecs/unified-ops-hub-core-api-dev --follow

# Filtrar por erro
aws logs filter-log-events \
  --log-group-name /ecs/unified-ops-hub-core-api-dev \
  --filter-pattern "ERROR"
```

### CloudWatch Alarms

- CPU > 70% → Scale up
- Memory > 80% → Alert
- Error rate > 1% → Alert
- Latency > 1s → Alert

### Métricas

```bash
# Ver métricas do ECS
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=unified-ops-hub-core-api \
  --start-time 2026-03-20T00:00:00Z \
  --end-time 2026-03-20T23:59:59Z \
  --period 300 \
  --statistics Average
```

---

## 🧪 Testes

### Unit Tests

```bash
cd backend
pytest tests/unit/

# Com coverage
pytest --cov=shared tests/unit/
```

### Integration Tests

```bash
pytest tests/integration/

# Apenas testes de conectores
pytest tests/integration/test_connectors.py
```

### E2E Tests

```bash
cd frontend
npm run test:e2e
```

---

## 📈 Performance

### Otimizações Implementadas

- **Connection pooling** — PgBouncer para PostgreSQL
- **Caching** — Redis para sessions e rate limits
- **CDN** — CloudFront para assets estáticos
- **Compression** — Gzip para respostas
- **Lazy loading** — Code splitting no React

### Benchmarks

- **API Response Time** — < 100ms (p99)
- **Dashboard Load** — < 2s (first paint)
- **WebSocket Latency** — < 50ms
- **Database Query** — < 10ms (p99)

---

## 🚢 Deployment

### Deploy para AWS

```bash
# 1. Build Docker images
docker build -f infrastructure/docker/core-api.Dockerfile -t core-api:latest .
docker build -f infrastructure/docker/webhook-ingestor.Dockerfile -t webhook-ingestor:latest .
docker build -f infrastructure/docker/integration-worker.Dockerfile -t integration-worker:latest .
docker build -f infrastructure/docker/realtime-service.Dockerfile -t realtime-service:latest .

# 2. Push para ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag core-api:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/core-api:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/core-api:latest

# 3. Update ECS services
aws ecs update-service --cluster unified-ops-hub-dev --service core-api --force-new-deployment

# 4. Build e deploy frontend
cd frontend/unified-ops-hub-frontend
npm run build
# Deploy para S3 + CloudFront
```

### Environment Variables

```bash
# Backend
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
JWT_SECRET=your-secret-key
COGNITO_CLIENT_ID=xxx
COGNITO_CLIENT_SECRET=xxx

# Frontend
VITE_API_URL=https://api.example.com
VITE_WS_URL=wss://ws.example.com
VITE_COGNITO_REGION=us-east-1
VITE_COGNITO_CLIENT_ID=xxx
```

---

## 🛠️ Troubleshooting

### Backend não conecta ao banco

```bash
# Verificar conexão
psql -h $DATABASE_HOST -U $DATABASE_USER -d $DATABASE_NAME

# Verificar security group
aws ec2 describe-security-groups --group-ids sg-xxx
```

### WebSocket connection failed

```bash
# Verificar serviço real-time
curl http://localhost:8003/health

# Verificar logs
docker logs unified-ops-hub-realtime-service
```

### Frontend não carrega

```bash
# Verificar build
npm run build

# Verificar assets
aws s3 ls s3://unified-ops-hub-frontend/

# Verificar CloudFront
aws cloudfront get-distribution --id XXXXX
```

---

## 📚 Documentação Detalhada

- [Phase 0 — Architecture Definition](./PHASE_0_ARCHITECTURE.md)
- [Phase 1 — Infrastructure Foundation](./PHASE_1_INFRASTRUCTURE.md)
- [Phase 2 — Data Layer](./PHASE_2_DATA_LAYER.md)
- [Phase 3 — Backend Core](./PHASE_3_BACKEND_CORE.md)
- [Phase 4 — Integration Framework](./PHASE_4_INTEGRATION_FRAMEWORK.md)
- [Phase 5 — Frontend & Dashboard](./PHASE_5_FRONTEND_DASHBOARD.md)

---

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está licenciado sob a MIT License — veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 📧 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.

---

## 🎯 Roadmap

### Phase 6 — Próximos Passos

- [ ] Mobile app (React Native)
- [ ] Advanced analytics
- [ ] Custom integrations API
- [ ] Team collaboration features
- [ ] Webhooks customizados
- [ ] Backup & disaster recovery
- [ ] Multi-language support
- [ ] Advanced permissions

---

**Kora Vision — Seu Centro de Operações Inteligente. Desenvolvido com ❤️ usando as melhores práticas de engenharia de software.**
