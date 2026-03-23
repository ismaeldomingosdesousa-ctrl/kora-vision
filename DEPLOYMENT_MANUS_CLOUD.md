# Kora Vision - Deployment na Manus Cloud

## 📋 Visão Geral

Este documento descreve como fazer deploy do Kora Vision MVP na Manus Cloud (totalmente grátis).

## 🚀 Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    Manus Cloud                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Frontend   │  │   Core API   │  │   Webhooks   │  │
│  │   (React)    │  │  (FastAPI)   │  │  (FastAPI)   │  │
│  │   Port 3000  │  │  Port 8000   │  │  Port 8001   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Worker    │  │  Real-time   │  │  PostgreSQL  │  │
│  │  (FastAPI)  │  │  (FastAPI)   │  │   Database   │  │
│  │  Port 8002  │  │  Port 8003   │  │  Port 5432   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                         │
│  ┌──────────────┐                                       │
│  │    Redis     │                                       │
│  │    Cache     │                                       │
│  │  Port 6379   │                                       │
│  └──────────────┘                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 📦 Serviços

### Frontend (React)
- **Port:** 3000
- **Framework:** React 19 + TypeScript
- **Build:** Vite
- **Features:** Dashboard, Integrações, Configurações

### Backend Services

#### 1. Core API
- **Port:** 8000
- **Framework:** FastAPI
- **Features:** CRUD, Autenticação, Gestão de Tenants
- **Database:** PostgreSQL

#### 2. Webhook Ingestor
- **Port:** 8001
- **Framework:** FastAPI
- **Features:** Recebe webhooks, Validação HMAC
- **Queue:** Redis

#### 3. Integration Worker
- **Port:** 8002
- **Framework:** FastAPI
- **Features:** Sincronização de dados, Agendamento
- **Connectors:** Google Calendar, Jira, Datadog, Dynatrace, WhatsApp

#### 4. Real-time Service
- **Port:** 8003
- **Framework:** FastAPI + WebSocket
- **Features:** Atualizações em tempo real
- **Cache:** Redis

### Database
- **PostgreSQL 15**
- **Port:** 5432
- **Database:** koravision
- **Features:** Multi-tenant com RLS

### Cache
- **Redis 7**
- **Port:** 6379
- **Features:** Sessões, Cache, Fila de Mensagens

## 🚀 Como Fazer Deploy

### Passo 1: Preparar o Ambiente

```bash
# Clone o repositório
git clone https://github.com/ismaeldomingosdesousa-ctrl/kora-vision.git
cd kora-vision

# Copie o arquivo de exemplo
cp .env.example .env

# Configure as variáveis de ambiente
nano .env
```

### Passo 2: Configurar Variáveis de Ambiente

```bash
# Database
DB_USER=admin
DB_PASSWORD=seu-senha-segura
DB_NAME=koravision

# JWT
JWT_SECRET=sua-chave-secreta-super-segura

# Environment
ENVIRONMENT=production

# API URLs
VITE_API_URL=https://seu-dominio.manus.space/api
VITE_WEBSOCKET_URL=wss://seu-dominio.manus.space/ws
```

### Passo 3: Build e Deploy

```bash
# Build das imagens Docker
docker-compose build

# Iniciar os serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f
```

### Passo 4: Executar Migrations

```bash
# Conectar ao container do backend
docker-compose exec core-api bash

# Executar migrations
cd migrations
alembic upgrade head

# Sair
exit
```

### Passo 5: Verificar Saúde dos Serviços

```bash
# Core API
curl http://localhost:8000/health

# Webhook Ingestor
curl http://localhost:8001/health

# Integration Worker
curl http://localhost:8002/health

# Real-time Service
curl http://localhost:8003/health

# Frontend
curl http://localhost:3000
```

## 📊 Monitoramento

### Logs

```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f core-api

# Últimas 100 linhas
docker-compose logs --tail=100 core-api
```

### Health Checks

```bash
# Verificar saúde do banco de dados
docker-compose exec postgres pg_isready -U admin

# Verificar saúde do Redis
docker-compose exec redis redis-cli ping

# Verificar saúde da aplicação
curl http://localhost:8000/health
```

## 🔧 Troubleshooting

### Porta já em uso

```bash
# Encontrar processo usando a porta
lsof -i :8000

# Matar o processo
kill -9 <PID>
```

### Erro de conexão com banco de dados

```bash
# Verificar se o PostgreSQL está rodando
docker-compose ps postgres

# Verificar logs do PostgreSQL
docker-compose logs postgres

# Reiniciar o PostgreSQL
docker-compose restart postgres
```

### Erro de conexão com Redis

```bash
# Verificar se o Redis está rodando
docker-compose ps redis

# Verificar logs do Redis
docker-compose logs redis

# Reiniciar o Redis
docker-compose restart redis
```

## 💰 Custos

**Manus Cloud Free-Tier:**
- ✅ 1 aplicação
- ✅ 1GB RAM
- ✅ 1GB Storage
- ✅ Domínio grátis (*.manus.space)
- ✅ SSL/TLS automático
- ✅ Sem limite de requisições

**Custo:** R$ 0/mês

## 📈 Próximos Passos

1. **Configurar Autenticação:** Integrar com Manus OAuth
2. **Configurar Integrações:** Adicionar chaves de API
3. **Monitoramento:** Configurar alertas
4. **Backup:** Configurar backup automático do banco de dados
5. **Scaling:** Aumentar recursos conforme necessário

## 📞 Suporte

- **Documentação:** Veja os arquivos PHASE_*.md
- **GitHub:** https://github.com/ismaeldomingosdesousa-ctrl/kora-vision
- **Manus Help:** https://help.manus.im
