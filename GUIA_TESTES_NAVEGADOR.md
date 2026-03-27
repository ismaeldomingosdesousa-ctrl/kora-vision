# 🌐 Guia de Testes via Navegador - Kora Vision

**Status:** ✅ API Funcionando  
**Objetivo:** Testar tudo via navegador  
**Tempo Estimado:** 10-15 minutos  

---

## 📋 Índice

1. [Teste 1: Acessar Frontend](#teste-1-acessar-frontend)
2. [Teste 2: Explorar Swagger UI](#teste-2-explorar-swagger-ui)
3. [Teste 3: Testar Endpoints da API](#teste-3-testar-endpoints-da-api)
4. [Teste 4: Criar Dados de Teste](#teste-4-criar-dados-de-teste)
5. [Teste 5: Verificar Dashboard](#teste-5-verificar-dashboard)

---

## ✅ Teste 1: Acessar Frontend

### 1.1: Abrir o Navegador

Abra seu navegador favorito (Chrome, Firefox, Safari, Edge, etc)

### 1.2: Acessar o Dashboard

Digite na barra de endereço:

```
http://localhost:3000
```

**Esperado:**
- Você verá o **Kora Vision Dashboard**
- Interface limpa e responsiva
- Menu lateral com opções
- Área principal com conteúdo

✅ **Frontend está funcionando!**

### 1.3: Explorar o Dashboard

Clique nos diferentes menus:
- Dashboard
- Operations
- Integrations
- Settings
- Etc.

---

## ✅ Teste 2: Explorar Swagger UI

### 2.1: Abrir Swagger

Abra em uma nova aba:

```
http://localhost:8000/docs
```

**Esperado:**
- Você verá a **documentação interativa da API**
- Lista de todos os endpoints
- Modelos de dados
- Opções para testar

✅ **Swagger UI está funcionando!**

### 2.2: Explorar Endpoints

Você verá seções como:
- **Operations** - Gerenciar operações
- **Users** - Gerenciar usuários
- **Integrations** - Gerenciar integrações
- **Webhooks** - Gerenciar webhooks
- **Health** - Verificar saúde da API

---

## ✅ Teste 3: Testar Endpoints da API

### 3.1: Testar Health Check

No Swagger UI, procure por **GET /health**

Clique em "Try it out" e depois "Execute"

**Esperado:**
```json
{
  "status": "ok"
}
```

✅ **Health check funcionando!**

### 3.2: Testar Listar Operações

Procure por **GET /api/v1/operations**

Clique em "Try it out" e depois "Execute"

**Esperado:**
```json
[]
```

(Lista vazia, pois não há dados ainda)

✅ **Endpoint funcionando!**

### 3.3: Testar Listar Usuários

Procure por **GET /api/v1/users**

Clique em "Try it out" e depois "Execute"

**Esperado:**
```json
[]
```

(Lista vazia, pois não há dados ainda)

✅ **Endpoint funcionando!**

---

## ✅ Teste 4: Criar Dados de Teste

### 4.1: Criar um Usuário

No Swagger UI, procure por **POST /api/v1/users**

Clique em "Try it out"

Você verá um formulário. Preencha com:

```json
{
  "email": "teste@example.com",
  "name": "Usuário Teste",
  "password": "SenhaSegura123!"
}
```

Clique em "Execute"

**Esperado:**
```json
{
  "id": "uuid-xxx",
  "email": "teste@example.com",
  "name": "Usuário Teste",
  "created_at": "2026-03-27T22:30:00Z"
}
```

✅ **Usuário criado com sucesso!**

### 4.2: Criar uma Operação

Procure por **POST /api/v1/operations**

Clique em "Try it out"

Preencha com:

```json
{
  "title": "Operação de Teste",
  "description": "Esta é uma operação de teste",
  "status": "pending",
  "priority": "high"
}
```

Clique em "Execute"

**Esperado:**
```json
{
  "id": "uuid-xxx",
  "title": "Operação de Teste",
  "description": "Esta é uma operação de teste",
  "status": "pending",
  "priority": "high",
  "created_at": "2026-03-27T22:30:00Z"
}
```

✅ **Operação criada com sucesso!**

### 4.3: Listar Dados Criados

Agora teste novamente:

**GET /api/v1/users**

**Esperado:**
```json
[
  {
    "id": "uuid-xxx",
    "email": "teste@example.com",
    "name": "Usuário Teste",
    "created_at": "2026-03-27T22:30:00Z"
  }
]
```

✅ **Usuário apareceu na lista!**

**GET /api/v1/operations**

**Esperado:**
```json
[
  {
    "id": "uuid-xxx",
    "title": "Operação de Teste",
    "description": "Esta é uma operação de teste",
    "status": "pending",
    "priority": "high",
    "created_at": "2026-03-27T22:30:00Z"
  }
]
```

✅ **Operação apareceu na lista!**

---

## ✅ Teste 5: Verificar Dashboard

### 5.1: Voltar ao Frontend

Volte para a aba do dashboard:

```
http://localhost:3000
```

### 5.2: Verificar se os Dados Aparecem

Navegue pelos menus e veja se:
- ✅ Os usuários aparecem na seção de usuários
- ✅ As operações aparecem na seção de operações
- ✅ Os dados estão sendo sincronizados

### 5.3: Testar Responsividade

Redimensione a janela do navegador:
- ✅ Interface se adapta em telas pequenas
- ✅ Menu fica responsivo
- ✅ Conteúdo se reorganiza

---

## 🎯 Checklist Final de Testes

- [ ] Frontend acessível em http://localhost:3000
- [ ] Swagger UI acessível em http://localhost:8000/docs
- [ ] Health check retorna status ok
- [ ] Listar operações retorna lista (vazia ou com dados)
- [ ] Listar usuários retorna lista (vazia ou com dados)
- [ ] Consegui criar um usuário via Swagger
- [ ] Consegui criar uma operação via Swagger
- [ ] Usuário criado aparece na lista
- [ ] Operação criada aparece na lista
- [ ] Dashboard mostra os dados criados
- [ ] Interface é responsiva

---

## 🌐 URLs Importantes

| Serviço | URL | Descrição |
|---------|-----|-----------|
| Frontend | http://localhost:3000 | Dashboard principal |
| API Docs | http://localhost:8000/docs | Documentação interativa |
| API ReDoc | http://localhost:8000/redoc | Documentação alternativa |
| Health Check | http://localhost:8000/health | Status da API |

---

## 💡 Dicas de Navegação

### No Swagger UI

1. **Expandir um endpoint:** Clique no endpoint para expandir
2. **Try it out:** Clique para ativar o modo de teste
3. **Execute:** Clique para enviar a requisição
4. **Response:** Veja a resposta abaixo

### No Frontend

1. **Menu Lateral:** Navegue pelos diferentes módulos
2. **Botões de Ação:** Crie, edite ou delete dados
3. **Busca:** Use a barra de busca para filtrar
4. **Filtros:** Use filtros para refinar resultados

---

## 🛑 Se Tiver Problemas

### Frontend não carrega

```bash
docker-compose logs frontend
curl http://localhost:3000
```

### API não responde

```bash
docker-compose logs core-api
curl http://localhost:8000/health
```

### Dados não aparecem

```bash
# Verifique o banco de dados
docker-compose exec postgres psql -U admin -d koravision -c "SELECT * FROM users;"
```

### Limpar dados e começar do zero

```bash
docker-compose exec postgres psql -U admin -d koravision -c "DELETE FROM users; DELETE FROM operations;"
```

---

## 📚 Próximas Etapas

1. ✅ Todos os testes passaram?
2. ✅ Explore mais endpoints no Swagger
3. ✅ Crie mais dados de teste
4. ✅ Teste as funcionalidades de edição e exclusão
5. ✅ Configure integrações
6. ✅ Monitore os logs em tempo real

---

## 🎁 Bônus: Testar com cURL

Se preferir testar via terminal:

### Criar usuário

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "name": "Usuário Teste",
    "password": "SenhaSegura123!"
  }'
```

### Listar usuários

```bash
curl http://localhost:8000/api/v1/users
```

### Criar operação

```bash
curl -X POST http://localhost:8000/api/v1/operations \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Operação de Teste",
    "description": "Esta é uma operação de teste",
    "status": "pending",
    "priority": "high"
  }'
```

### Listar operações

```bash
curl http://localhost:8000/api/v1/operations
```

---

**Parabéns! Você agora tem o Kora Vision totalmente funcional e testado! 🚀**

Qualquer dúvida, é só chamar! 💪
