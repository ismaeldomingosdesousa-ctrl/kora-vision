# 📦 Provisionamento Final - Kora Vision MVP

**Data:** 27 de Março de 2026  
**Status:** ✅ Pronto para Deploy Local  
**Versão:** 1.0 - MVP

---

## 🎯 O que foi Provisionado

### Backend (Python 3.11)

**Dependências Principais:**
```
fastapi==0.104.1              # Framework Web
uvicorn[standard]==0.24.0     # Servidor ASGI
pydantic==2.5.0               # Validação de dados
pydantic-settings==2.1.0      # Configurações
sqlalchemy==2.0.23            # ORM
alembic==1.13.0               # Migrações de BD
psycopg2-binary==2.9.9        # Driver PostgreSQL
asyncpg==0.29.0               # Driver async PostgreSQL
python-jose[cryptography]==3.3.0  # JWT
passlib[bcrypt]==1.7.4        # Hash de senhas
python-multipart==0.0.6       # Upload de arquivos
PyJWT==2.12.1                 # Token JWT
cryptography==41.0.7          # Criptografia
httpx==0.25.2                 # Cliente HTTP async
requests==2.31.0              # Cliente HTTP sync
aiohttp==3.9.1                # Cliente HTTP async
redis==5.0.1                  # Cliente Redis
aioredis==2.0.1               # Cliente Redis async
python-json-logger==2.0.7     # Logging JSON
python-dotenv==1.0.0          # Variáveis de ambiente
pyyaml==6.0.1                 # YAML
click==8.1.7                  # CLI
typer==0.9.0                  # CLI moderno
pytest==7.4.3                 # Testes
pytest-asyncio==0.21.1        # Testes async
pytest-cov==4.1.0             # Cobertura de testes
black==23.12.0                # Formatação de código
flake8==6.1.0                 # Linting
isort==5.13.2                 # Ordenação de imports
mypy==1.7.1                   # Type checking
```

**Serviços FastAPI:**
1. **Core API** (porta 8000)
   - Autenticação
   - CRUD de operações
   - Gerenciamento de tenants
   - Health checks

2. **Webhook Ingestor** (porta 8001)
   - Recebe webhooks de integrações
   - Processa eventos
   - Armazena no banco

3. **Integration Worker** (porta 8002)
   - Sincronização em background
   - Processamento de jobs
   - Retry logic

4. **Real-time Service** (porta 8003)
   - WebSocket para atualizações em tempo real
   - Broadcast de eventos
   - Conexões persistentes

---

### Frontend (Node.js 22)

**Stack:**
- React 19
- TypeScript
- TailwindCSS 4
- shadcn/ui (componentes)
- Wouter (routing)
- Vite (build tool)
- pnpm (package manager)

**Dependências Principais:**
```json
{
  "react": "^19.0.0",
  "react-dom": "^19.0.0",
  "typescript": "^5.3.3",
  "tailwindcss": "^4.0.0",
  "@radix-ui/*": "latest",
  "wouter": "^3.7.1",
  "clsx": "^2.0.0",
  "tailwind-merge": "^2.2.0",
  "vite": "^7.1.9"
}
```

**Páginas:**
- Home (landing page)
- Dashboard (operações)
- Integrations (configuração de integrações)
- NotFound (404)

---

### Database (PostgreSQL 15)

**Schema:**
- Users (autenticação)
- Tenants (multi-tenant)
- Operations (dados principais)
- Integrations (configurações)
- Webhooks (histórico)
- Tasks (background jobs)
- Events (auditoria)
- Settings (configurações do tenant)

**Recursos:**
- Row-Level Security (RLS)
- Migrations com Alembic
- Índices otimizados
- Constraints de integridade

---

### Cache (Redis 7)

**Uso:**
- Cache de sessões
- Cache de operações
- Fila de jobs
- Pub/Sub para real-time

---

## 🐳 Docker Compose

**Serviços Orquestrados:**
1. PostgreSQL 15-alpine
2. Redis 7-alpine
3. Core API (FastAPI)
4. Webhook Ingestor (FastAPI)
5. Integration Worker (FastAPI)
6. Real-time Service (FastAPI)
7. Frontend (React)

**Volumes:**
- `postgres_data` - Persistência do banco
- `redis_data` - Persistência do cache
- `./backend` - Code mounting (desenvolvimento)
- `./frontend` - Code mounting (desenvolvimento)

**Network:**
- `kora-vision-network` (bridge)

**Health Checks:**
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- APIs: HTTP health endpoints

---

## 🚀 Instruções de Deploy Local

### Pré-requisitos

```bash
# Ubuntu 24.04
sudo apt update
sudo apt upgrade -y

# Instalar Docker
sudo apt install -y docker.io docker-compose

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Verificar instalação
docker --version
docker-compose --version
```

### Clone e Configure

```bash
# Clone
git clone https://github.com/ismaeldomingosdesousa-ctrl/kora-vision.git
cd kora-vision

# Configure ambiente
cp .env.example .env

# Valores padrão (funcionam para desenvolvimento):
# DB_USER=admin
# DB_PASSWORD=changeme
# DB_NAME=koravision
# JWT_SECRET=your-secret-key-change-in-production
# ENVIRONMENT=development
```

### Build e Deploy

```bash
# Build das imagens
docker-compose build

# Inicie os serviços
docker-compose up -d

# Aguarde 20 segundos
sleep 20

# Verifique status
docker-compose ps

# Execute migrations
docker-compose exec core-api bash
cd migrations
alembic upgrade head
exit
```

### Acesse

```
Frontend: http://localhost:3000
API Docs: http://localhost:8000/docs
```

---

## 📊 Recursos Necessários

| Recurso | Mínimo | Recomendado |
|---------|--------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 4GB | 8GB |
| Disco | 20GB | 50GB |
| Conexão | 10Mbps | 100Mbps |

---

## 🔧 Troubleshooting

### Build falha

```bash
# Limpe tudo
docker-compose down -v
docker system prune -a -f

# Tente novamente
docker-compose build --no-cache
```

### Porta em uso

```bash
# Mude no docker-compose.yml ou mate o processo
lsof -i :3000
kill -9 <PID>
```

### Banco não conecta

```bash
# Reinicie PostgreSQL
docker-compose restart postgres
sleep 10
docker-compose ps
```

---

## 📝 Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| `docker-compose.yml` | Orquestração de serviços |
| `backend/requirements.txt` | Dependências Python |
| `frontend/package.json` | Dependências Node.js |
| `infrastructure/docker/*.Dockerfile` | Dockerfiles dos serviços |
| `backend/migrations/` | Migrations do banco |
| `.env.example` | Variáveis de ambiente |
| `GUIA_COMPLETO_KORA_VISION.md` | Guia detalhado |

---

## ✅ Checklist de Deploy

- [ ] Docker instalado e rodando
- [ ] Repositório clonado
- [ ] `.env` configurado
- [ ] `docker-compose build` executado com sucesso
- [ ] `docker-compose up -d` iniciou todos os serviços
- [ ] `docker-compose ps` mostra todos os containers `Up`
- [ ] Migrations executadas com sucesso
- [ ] Frontend acessível em http://localhost:3000
- [ ] API acessível em http://localhost:8000/docs

---

## 🎯 Próximas Etapas (Pós-MVP)

1. Adicionar observabilidade (OpenTelemetry)
2. Adicionar autenticação OAuth (Google, Microsoft)
3. Adicionar mais integrações
4. Implementar alertas
5. Adicionar testes E2E
6. Configurar CI/CD
7. Deploy em produção (AWS, Manus Cloud, etc)

---

## 📞 Suporte

Se tiver problemas:

1. Verifique os logs: `docker-compose logs -f`
2. Reinicie os serviços: `docker-compose restart`
3. Limpe tudo: `docker system prune -a -f`
4. Consulte `GUIA_COMPLETO_KORA_VISION.md`

---

**Tudo está pronto para você! 🚀**

Qualquer dúvida, é só chamar!
