# 🚀 Guia Completo: Kora Vision Local com Docker

**Status:** ✅ Testado e Validado  
**Data:** 27 de Março de 2026  
**Versão:** 1.0

---

## 📋 Pré-requisitos

Você precisa ter instalado na sua máquina Ubuntu:

- ✅ **Docker** (versão 24+)
- ✅ **Docker Compose** (versão 2.20+)
- ✅ **Git**
- ✅ **4GB RAM mínimo** (8GB recomendado)
- ✅ **20GB de espaço em disco**

---

## 🎯 Passo 1: Verificar Instalações

```bash
# Verificar Docker
docker --version
# Esperado: Docker version 24.x.x ou superior

# Verificar Docker Compose
docker-compose --version
# Esperado: Docker Compose version 2.x.x ou superior

# Verificar Git
git --version
# Esperado: git version 2.x.x ou superior
```

Se algum comando não funcionar, instale conforme o manual `INSTALL_DOCKER_UBUNTU.md`.

---

## 🎯 Passo 2: Clonar o Repositório

```bash
# Clonar o repositório
git clone https://github.com/ismaeldomingosdesousa-ctrl/kora-vision.git
cd kora-vision

# Verificar que está na branch main
git branch
# Deve mostrar: * main
```

---

## 🎯 Passo 3: Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar (opcional - valores padrão funcionam para desenvolvimento)
nano .env
```

**Valores padrão (funcionam para desenvolvimento):**

```bash
DB_USER=admin
DB_PASSWORD=changeme
DB_NAME=koravision
JWT_SECRET=your-secret-key-change-in-production
ENVIRONMENT=development
```

Se quiser mudar senhas, edite o arquivo `.env`.

---

## 🎯 Passo 4: Limpar Ambiente (Primeira Vez)

```bash
# Parar containers antigos (se houver)
docker-compose down -v 2>/dev/null || true

# Limpar imagens e cache
docker system prune -a -f
```

---

## 🎯 Passo 5: Build das Imagens

```bash
# Build de todas as imagens
docker-compose build

# Isso pode levar 10-15 minutos na primeira vez
# Próximas vezes será muito mais rápido (usa cache)
```

**Se tiver erro de conexão:**

```bash
# Tente novamente com --no-cache
docker-compose build --no-cache
```

---

## 🎯 Passo 6: Iniciar os Serviços

```bash
# Iniciar todos os containers
docker-compose up -d

# Aguarde 15-20 segundos para tudo inicializar
sleep 20

# Verificar status
docker-compose ps
```

**Você deve ver algo assim:**

```
NAME                            STATUS
kora-vision-postgres            Up 20 seconds
kora-vision-redis               Up 20 seconds
kora-vision-core-api            Up 20 seconds
kora-vision-webhook-ingestor    Up 20 seconds
kora-vision-integration-worker  Up 20 seconds
kora-vision-realtime-service    Up 20 seconds
kora-vision-frontend            Up 20 seconds
```

Se algum estiver `Exited`, veja os logs:

```bash
docker-compose logs <nome-do-serviço>
```

---

## 🎯 Passo 7: Executar Migrations (Primeira Vez)

```bash
# Conectar ao container do backend
docker-compose exec core-api bash

# Dentro do container:
cd migrations
alembic upgrade head

# Sair do container
exit
```

---

## ✅ Passo 8: Verificar se Tudo Está Funcionando

### Acessar o Frontend

Abra no navegador:

```
http://localhost:3000
```

Você deve ver o **Kora Vision Dashboard**! 🎉

### Testar as APIs

```bash
# Core API
curl http://localhost:8000/health
# Resposta esperada: {"status":"ok"} ou similar

# Webhook Ingestor
curl http://localhost:8001/health

# Integration Worker
curl http://localhost:8002/health

# Real-time Service
curl http://localhost:8003/health
```

### Ver Documentação da API

```
http://localhost:8000/docs
```

---

## 📊 Monitorar Logs

### Ver Todos os Logs em Tempo Real

```bash
docker-compose logs -f
```

Pressione `Ctrl+C` para sair.

### Ver Logs de um Serviço Específico

```bash
# Frontend
docker-compose logs -f frontend

# Core API
docker-compose logs -f core-api

# PostgreSQL
docker-compose logs -f postgres

# Redis
docker-compose logs -f redis
```

### Ver Últimas 50 Linhas

```bash
docker-compose logs --tail=50 core-api
```

---

## 🛑 Parar e Reiniciar

### Parar Tudo (Mantém Dados)

```bash
docker-compose down
```

### Parar e Remover Dados

```bash
docker-compose down -v
```

⚠️ **Cuidado:** Isso deleta o banco de dados!

### Reiniciar Tudo

```bash
docker-compose restart
```

### Reiniciar um Serviço Específico

```bash
docker-compose restart core-api
```

---

## 🔧 Troubleshooting

### Problema: "Port 3000 is already allocated"

**Solução 1:** Mude a porta no `docker-compose.yml`:

```yaml
frontend:
  ports:
    - "3001:3000"  # Mude 3000 para 3001
```

Depois reinicie:

```bash
docker-compose down
docker-compose up -d
```

**Solução 2:** Mate o processo que está usando a porta:

```bash
lsof -i :3000
kill -9 <PID>
```

### Problema: "Cannot connect to PostgreSQL"

```bash
# Reinicie o banco de dados
docker-compose restart postgres

# Verifique os logs
docker-compose logs postgres

# Aguarde 10 segundos e tente novamente
sleep 10
docker-compose ps
```

### Problema: "Build failed"

```bash
# Limpe tudo e comece do zero
docker-compose down -v
docker system prune -a -f
docker-compose build --no-cache
docker-compose up -d
```

### Problema: "Out of disk space"

```bash
# Verifique espaço
df -h

# Limpe imagens não usadas
docker system prune -a -f

# Remova volumes não usados
docker volume prune -f
```

### Problema: Container Exited

```bash
# Veja os logs
docker-compose logs <nome-do-serviço>

# Procure por erros em vermelho
# Compartilhe os erros para diagnóstico
```

---

## 💾 Backup do Banco de Dados

### Fazer Backup

```bash
docker-compose exec postgres pg_dump -U admin koravision > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restaurar Backup

```bash
docker-compose exec -T postgres psql -U admin koravision < backup_20260327_120000.sql
```

---

## 🌐 Acessar Serviços

| Serviço | URL | Descrição |
|---------|-----|-----------|
| Frontend | http://localhost:3000 | Dashboard React |
| Core API | http://localhost:8000 | FastAPI Principal |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Webhook | http://localhost:8001 | Receptor de Webhooks |
| Worker | http://localhost:8002 | Sync em Background |
| Real-time | http://localhost:8003 | WebSocket |
| PostgreSQL | localhost:5432 | Banco de Dados |
| Redis | localhost:6379 | Cache |

---

## 📈 Recursos Utilizados

- **CPU:** 2-4 cores
- **RAM:** 2-3GB
- **Disco:** ~5GB (imagens + dados)

---

## 🎯 Próximos Passos

1. ✅ Acessar http://localhost:3000
2. ✅ Explorar o dashboard
3. ✅ Testar as APIs em http://localhost:8000/docs
4. ✅ Configurar integrações (Google Calendar, Jira, etc)
5. ✅ Monitorar os logs

---

## 💡 Dicas Importantes

### Desenvolvimento

Se você vai modificar código:

```bash
# Ver logs em tempo real
docker-compose logs -f

# Os containers têm reload automático (--reload)
# Salve o arquivo e veja as mudanças em tempo real
```

### Produção

Para produção, use:

```bash
# Sem reload
docker-compose -f docker-compose.prod.yml up -d
```

(Arquivo a ser criado)

### Resetar Banco de Dados

```bash
# Parar tudo
docker-compose down -v

# Iniciar novamente
docker-compose up -d

# Executar migrations
docker-compose exec core-api bash
cd migrations
alembic upgrade head
exit
```

---

## 🆘 Precisa de Ajuda?

1. **Verifique os logs:** `docker-compose logs`
2. **Reinicie tudo:** `docker-compose down && docker-compose up -d`
3. **Limpe tudo:** `docker system prune -a -f`
4. **Consulte a documentação:** Veja os arquivos PHASE_*.md

---

## ✨ Resumo Rápido (Copiar e Colar)

```bash
# Clone
git clone https://github.com/ismaeldomingosdesousa-ctrl/kora-vision.git
cd kora-vision

# Configure
cp .env.example .env

# Build
docker-compose build

# Inicie
docker-compose up -d

# Aguarde
sleep 20

# Migrations
docker-compose exec core-api bash
cd migrations
alembic upgrade head
exit

# Acesse
# http://localhost:3000
```

---

**Pronto! Seu Kora Vision está rodando localmente! 🎉**

Para mais informações, consulte:
- INSTALL_DOCKER_UBUNTU.md - Instalação do Docker
- README.md - Visão geral do projeto
- PHASE_*.md - Documentação técnica detalhada
