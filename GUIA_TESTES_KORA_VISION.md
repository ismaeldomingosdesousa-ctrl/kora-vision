# 🧪 Guia Completo de Testes - Kora Vision

**Status:** ✅ Todos os Serviços Rodando  
**Objetivo:** Validar funcionamento de todos os componentes  
**Tempo Estimado:** 15-20 minutos  

---

## 📋 Índice

1. [Teste 1: Verificar Containers](#teste-1-verificar-containers)
2. [Teste 2: Testar PostgreSQL](#teste-2-testar-postgresql)
3. [Teste 3: Testar Redis](#teste-3-testar-redis)
4. [Teste 4: Testar Core API](#teste-4-testar-core-api)
5. [Teste 5: Testar Webhook Ingestor](#teste-5-testar-webhook-ingestor)
6. [Teste 6: Testar Integration Worker](#teste-6-testar-integration-worker)
7. [Teste 7: Testar Real-time Service](#teste-7-testar-real-time-service)
8. [Teste 8: Testar Frontend](#teste-8-testar-frontend)
9. [Teste 9: Executar Migrations](#teste-9-executar-migrations)
10. [Teste 10: Testes de Integração](#teste-10-testes-de-integração)

---

## ✅ Teste 1: Verificar Containers

### 1.1: Listar Containers

```bash
docker-compose ps
```

**Esperado:**
```
NAME                            STATUS
kora-vision-postgres            Up (healthy)
kora-vision-redis               Up (healthy)
kora-vision-core-api            Up
kora-vision-webhook-ingestor    Up
kora-vision-integration-worker  Up
kora-vision-realtime-service    Up
kora-vision-frontend            Up
```

✅ **Todos os 7 containers devem estar `Up`**

### 1.2: Verificar Recursos

```bash
docker stats --no-stream
```

Você verá o uso de CPU e memória de cada container.

---

## ✅ Teste 2: Testar PostgreSQL

### 2.1: Conectar ao PostgreSQL

```bash
docker-compose exec postgres psql -U admin -d koravision -c "SELECT version();"
```

**Esperado:**
```
                                                   version
-------------------------------------------------------------------------------------------------------------
 PostgreSQL 15.17 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
(1 row)
```

✅ **PostgreSQL está rodando corretamente**

### 2.2: Listar Tabelas

```bash
docker-compose exec postgres psql -U admin -d koravision -c "\dt"
```

**Esperado:**
```
Did not find any relations.
```

(Sem tabelas ainda, pois não rodamos migrations)

### 2.3: Verificar Conexão

```bash
docker-compose exec postgres pg_isready -U admin
```

**Esperado:**
```
accepting connections
```

✅ **Banco de dados está aceitando conexões**

---

## ✅ Teste 3: Testar Redis

### 3.1: Conectar ao Redis

```bash
docker-compose exec redis redis-cli ping
```

**Esperado:**
```
PONG
```

✅ **Redis está respondendo**

### 3.2: Testar Set/Get

```bash
docker-compose exec redis redis-cli SET test_key "Hello Redis"
docker-compose exec redis redis-cli GET test_key
```

**Esperado:**
```
OK
"Hello Redis"
```

✅ **Redis está armazenando dados**

### 3.3: Listar Chaves

```bash
docker-compose exec redis redis-cli KEYS "*"
```

**Esperado:**
```
1) "test_key"
```

---

## ✅ Teste 4: Testar Core API

### 4.1: Health Check

```bash
curl http://localhost:8000/health
```

**Esperado:**
```json
{"status":"ok"}
```

✅ **Core API está respondendo**

### 4.2: Documentação Swagger

Abra no navegador:
```
http://localhost:8000/docs
```

Você deve ver o **Swagger UI** com toda a documentação da API.

### 4.3: Testar Endpoint de Operações

```bash
curl -X GET http://localhost:8000/api/v1/operations \
  -H "Content-Type: application/json"
```

**Esperado:**
```json
[]
```

(Lista vazia, pois não há dados ainda)

### 4.4: Ver Logs da API

```bash
docker-compose logs -f core-api
```

Você verá os logs em tempo real. Pressione `Ctrl+C` para sair.

---

## ✅ Teste 5: Testar Webhook Ingestor

### 5.1: Health Check

```bash
curl http://localhost:8001/health
```

**Esperado:**
```json
{"status":"ok"}
```

✅ **Webhook Ingestor está respondendo**

### 5.2: Documentação Swagger

Abra no navegador:
```
http://localhost:8001/docs
```

### 5.3: Ver Logs

```bash
docker-compose logs -f webhook-ingestor
```

---

## ✅ Teste 6: Testar Integration Worker

### 6.1: Health Check

```bash
curl http://localhost:8002/health
```

**Esperado:**
```json
{"status":"ok"}
```

✅ **Integration Worker está respondendo**

### 6.2: Documentação Swagger

Abra no navegador:
```
http://localhost:8002/docs
```

### 6.3: Ver Logs

```bash
docker-compose logs -f integration-worker
```

---

## ✅ Teste 7: Testar Real-time Service

### 7.1: Health Check

```bash
curl http://localhost:8003/health
```

**Esperado:**
```json
{"status":"ok"}
```

✅ **Real-time Service está respondendo**

### 7.2: Documentação Swagger

Abra no navegador:
```
http://localhost:8003/docs
```

### 7.3: Ver Logs

```bash
docker-compose logs -f realtime-service
```

---

## ✅ Teste 8: Testar Frontend

### 8.1: Acessar Dashboard

Abra no navegador:
```
http://localhost:3000
```

Você deve ver o **Kora Vision Dashboard**!

### 8.2: Verificar Resposta HTTP

```bash
curl -I http://localhost:3000
```

**Esperado:**
```
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: xxxx
```

✅ **Frontend está servindo corretamente**

### 8.3: Ver Logs

```bash
docker-compose logs -f frontend
```

---

## ✅ Teste 9: Executar Migrations

### 9.1: Conectar ao Container

```bash
docker-compose exec core-api bash
```

Você verá um novo prompt:
```
root@xxxxxxx:/app#
```

### 9.2: Entrar em Migrations

```bash
cd migrations
```

### 9.3: Verificar Migrações Disponíveis

```bash
alembic current
```

**Esperado:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl with target metadata
INFO  [alembic.runtime.migration] Will assume transactional DDL is supported by the backend
(head)
```

### 9.4: Executar Todas as Migrações

```bash
alembic upgrade head
```

**Esperado:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl with target metadata
INFO  [alembic.runtime.migration] Will assume transactional DDL is supported by the backend
INFO  [alembic.runtime.migration] Running upgrade  -> xxxxx, create initial schema
INFO  [alembic.runtime.migration] Running upgrade xxxxx -> xxxxx, add users table
...
```

### 9.5: Verificar Tabelas Criadas

```bash
psql -U admin -d koravision -c "\dt"
```

**Esperado:**
```
                 List of relations
 Schema |         Name         | Type  | Owner
--------+----------------------+-------+-------
 public | alembic_version      | table | admin
 public | users                | table | admin
 public | tenants              | table | admin
 public | operations           | table | admin
 public | integrations         | table | admin
 public | webhooks             | table | admin
 public | tasks                | table | admin
 public | events               | table | admin
 public | settings             | table | admin
(9 rows)
```

✅ **Todas as tabelas foram criadas**

### 9.6: Sair do Container

```bash
exit
```

---

## ✅ Teste 10: Testes de Integração

### 10.1: Criar um Usuário

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "SecurePassword123!"
  }'
```

**Esperado:**
```json
{
  "id": "uuid-xxx",
  "email": "test@example.com",
  "name": "Test User",
  "created_at": "2026-03-27T22:30:00Z"
}
```

### 10.2: Listar Usuários

```bash
curl -X GET http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json"
```

**Esperado:**
```json
[
  {
    "id": "uuid-xxx",
    "email": "test@example.com",
    "name": "Test User",
    "created_at": "2026-03-27T22:30:00Z"
  }
]
```

### 10.3: Criar uma Operação

```bash
curl -X POST http://localhost:8000/api/v1/operations \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Operation",
    "description": "This is a test operation",
    "status": "pending",
    "priority": "high"
  }'
```

**Esperado:**
```json
{
  "id": "uuid-xxx",
  "title": "Test Operation",
  "description": "This is a test operation",
  "status": "pending",
  "priority": "high",
  "created_at": "2026-03-27T22:30:00Z"
}
```

### 10.4: Listar Operações

```bash
curl -X GET http://localhost:8000/api/v1/operations \
  -H "Content-Type: application/json"
```

**Esperado:**
```json
[
  {
    "id": "uuid-xxx",
    "title": "Test Operation",
    "description": "This is a test operation",
    "status": "pending",
    "priority": "high",
    "created_at": "2026-03-27T22:30:00Z"
  }
]
```

---

## 📊 Resumo de Testes

| Teste | Componente | Status | Comando |
|-------|-----------|--------|---------|
| 1 | Containers | ✅ | `docker-compose ps` |
| 2 | PostgreSQL | ✅ | `psql -U admin -d koravision` |
| 3 | Redis | ✅ | `redis-cli ping` |
| 4 | Core API | ✅ | `curl http://localhost:8000/health` |
| 5 | Webhook | ✅ | `curl http://localhost:8001/health` |
| 6 | Worker | ✅ | `curl http://localhost:8002/health` |
| 7 | Real-time | ✅ | `curl http://localhost:8003/health` |
| 8 | Frontend | ✅ | `http://localhost:3000` |
| 9 | Migrations | ✅ | `alembic upgrade head` |
| 10 | Integração | ✅ | `curl http://localhost:8000/api/v1/...` |

---

## 🎯 Checklist Final

- [ ] Todos os 7 containers estão `Up`
- [ ] PostgreSQL está respondendo
- [ ] Redis está respondendo
- [ ] Core API está respondendo (porta 8000)
- [ ] Webhook Ingestor está respondendo (porta 8001)
- [ ] Integration Worker está respondendo (porta 8002)
- [ ] Real-time Service está respondendo (porta 8003)
- [ ] Frontend está acessível (http://localhost:3000)
- [ ] Migrations foram executadas com sucesso
- [ ] Tabelas foram criadas no banco de dados
- [ ] Consegui criar um usuário via API
- [ ] Consegui criar uma operação via API
- [ ] Consegui listar usuários via API
- [ ] Consegui listar operações via API

---

## 🛑 Se Tiver Problemas

### Container Exited

```bash
docker-compose logs <nome-do-container>
```

### API não responde

```bash
docker-compose restart <nome-do-serviço>
```

### Banco de dados vazio

```bash
docker-compose exec core-api bash
cd migrations
alembic upgrade head
exit
```

### Limpar tudo e começar do zero

```bash
docker-compose down -v
docker system prune -a -f
docker-compose build --no-cache
docker-compose up -d
sleep 20
```

---

## 📚 Próximas Etapas

1. ✅ Todos os testes passaram?
2. ✅ Explorar o dashboard em http://localhost:3000
3. ✅ Testar mais endpoints da API
4. ✅ Configurar integrações
5. ✅ Adicionar dados de teste
6. ✅ Monitorar os logs em tempo real

---

## 💡 Dicas

### Ver Todos os Logs em Tempo Real

```bash
docker-compose logs -f
```

Pressione `Ctrl+C` para sair.

### Ver Logs de um Serviço Específico

```bash
docker-compose logs -f <nome-do-serviço>
```

### Ver Últimas 50 Linhas

```bash
docker-compose logs --tail=50 <nome-do-serviço>
```

### Executar Comando no Container

```bash
docker-compose exec <nome-do-serviço> <comando>
```

---

**Parabéns! Você agora tem o Kora Vision totalmente funcional! 🚀**

Qualquer dúvida, é só chamar! 💪
