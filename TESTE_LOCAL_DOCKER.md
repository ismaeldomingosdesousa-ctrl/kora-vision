# 🚀 Guia de Teste Local: Kora Vision com Docker

## ✅ Pré-requisitos

Você já tem:
- ✅ Docker instalado
- ✅ Docker Compose instalado
- ✅ Repositório clonado em `~/kora-vision`
- ✅ Frontend adicionado ao repositório

## 🎯 Passo-a-Passo para Testar

### Passo 1: Clonar a Versão Mais Recente

```bash
cd ~/kora-vision
git pull origin main
```

Isso garante que você tem o frontend mais recente!

### Passo 2: Verificar a Estrutura

```bash
ls -la ~/kora-vision/
```

Você deve ver:
```
backend/              ← Serviços FastAPI
frontend/             ← React (novo!)
infrastructure/       ← Dockerfiles
docker-compose.yml    ← Orquestração
.env                  ← Variáveis de ambiente
```

### Passo 3: Limpar Tudo (Primeira Vez)

```bash
cd ~/kora-vision
docker-compose down -v
docker system prune -a
```

### Passo 4: Build das Imagens

```bash
docker-compose build
```

**Isso pode levar 5-10 minutos** (primeira vez).

Se tiver erro, verifique:
- Espaço em disco: `df -h`
- Docker rodando: `docker ps`

### Passo 5: Iniciar os Serviços

```bash
docker-compose up -d
```

### Passo 6: Aguardar Inicialização

```bash
sleep 15
docker-compose ps
```

Você deve ver algo assim:

```
NAME                            STATUS
kora-vision-postgres            Up 15 seconds
kora-vision-redis               Up 15 seconds
kora-vision-core-api            Up 15 seconds
kora-vision-webhook-ingestor    Up 15 seconds
kora-vision-integration-worker  Up 15 seconds
kora-vision-realtime-service    Up 15 seconds
kora-vision-frontend            Up 15 seconds
```

Se algum estiver `Exited`, veja os logs:

```bash
docker-compose logs <nome-do-serviço>
```

### Passo 7: Executar Migrations (Primeira Vez)

```bash
docker-compose exec core-api bash
```

Dentro do container:

```bash
cd migrations
alembic upgrade head
exit
```

### Passo 8: Acessar a Aplicação

Abra no navegador:

```
http://localhost:3000
```

Você deve ver o **Kora Vision Dashboard**! 🎉

---

## 🧪 Testar os Serviços

### Testar Core API

```bash
curl http://localhost:8000/health
# Resposta esperada: {"status": "ok"}
```

### Testar Webhook Ingestor

```bash
curl http://localhost:8001/health
# Resposta esperada: {"status": "ok"}
```

### Testar Integration Worker

```bash
curl http://localhost:8002/health
# Resposta esperada: {"status": "ok"}
```

### Testar Real-time Service

```bash
curl http://localhost:8003/health
# Resposta esperada: {"status": "ok"}
```

### Ver Documentação da API

```
http://localhost:8000/docs
```

---

## 📊 Monitorar Logs

### Ver Todos os Logs

```bash
docker-compose logs -f
```

Pressione `Ctrl+C` para sair.

### Ver Logs de um Serviço Específico

```bash
docker-compose logs -f core-api
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Ver Últimas 50 Linhas

```bash
docker-compose logs --tail=50 core-api
```

---

## 🛑 Parar e Reiniciar

### Parar Tudo

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

### Reiniciar um Serviço

```bash
docker-compose restart core-api
```

---

## 🔧 Troubleshooting

### Erro: "Port 3000 is already allocated"

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

### Erro: "Cannot connect to PostgreSQL"

```bash
docker-compose restart postgres
docker-compose logs postgres
```

### Erro: "Build failed"

```bash
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

### Container Exited

```bash
docker-compose logs <nome-do-serviço>
```

Procure por erros em vermelho.

### Sem Espaço em Disco

```bash
docker system df
docker system prune -a
```

---

## 📈 Recursos Utilizados

- **CPU:** ~2-4 cores
- **RAM:** ~2-3GB
- **Disco:** ~5GB

---

## 🎯 Próximos Passos

1. ✅ Acessar http://localhost:3000
2. ✅ Explorar o dashboard
3. ✅ Testar as APIs em http://localhost:8000/docs
4. ✅ Configurar integrações (Google Calendar, Jira, etc)
5. ✅ Monitorar os logs

---

## 💡 Dicas

- **Desenvolvimento:** Use `docker-compose up` (sem `-d`) para ver logs em tempo real
- **Produção:** Use `docker-compose up -d` para rodar em background
- **Rebuild:** Se mudar código, rode `docker-compose build && docker-compose up -d`
- **Limpar:** Use `docker system prune -a` regularmente para liberar espaço

---

**Tudo pronto! Quer que eu ajude com algo mais? 🚀**
