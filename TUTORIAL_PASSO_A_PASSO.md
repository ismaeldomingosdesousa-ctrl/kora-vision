# 🚀 Tutorial Passo-a-Passo: Kora Vision Local

**Para:** Ubuntu 24.04  
**Tempo Estimado:** 30-45 minutos  
**Dificuldade:** Fácil  

---

## 📋 Índice

1. [Passo 1: Atualizar Sistema](#passo-1-atualizar-sistema)
2. [Passo 2: Instalar Docker](#passo-2-instalar-docker)
3. [Passo 3: Instalar Docker Compose](#passo-3-instalar-docker-compose)
4. [Passo 4: Instalar Git](#passo-4-instalar-git)
5. [Passo 5: Clonar Repositório](#passo-5-clonar-repositório)
6. [Passo 6: Configurar Ambiente](#passo-6-configurar-ambiente)
7. [Passo 7: Build das Imagens](#passo-7-build-das-imagens)
8. [Passo 8: Iniciar Serviços](#passo-8-iniciar-serviços)
9. [Passo 9: Executar Migrations](#passo-9-executar-migrations)
10. [Passo 10: Verificar Funcionamento](#passo-10-verificar-funcionamento)

---

## ✅ Passo 1: Atualizar Sistema

Abra o terminal e execute:

```bash
sudo apt update
```

Você verá:
```
Hit:1 http://archive.ubuntu.com/ubuntu jammy InRelease
Get:2 http://archive.ubuntu.com/ubuntu jammy-updates InRelease
...
Reading package lists... Done
```

Depois atualize os pacotes:

```bash
sudo apt upgrade -y
```

Isso pode levar alguns minutos. Aguarde até ver:
```
Processing triggers for...
Done.
```

---

## ✅ Passo 2: Instalar Docker

### 2.1: Instalar Dependências

```bash
sudo apt install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release
```

Você verá:
```
Reading package lists... Done
Building dependency tree... Done
...
Setting up curl (7.x.x-1ubuntu1) ...
Done.
```

### 2.2: Adicionar Chave GPG do Docker

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

Não deve retornar nada (silencioso = sucesso ✅)

### 2.3: Adicionar Repositório do Docker

```bash
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Você verá:
```
deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu jammy stable
```

### 2.4: Atualizar Lista de Pacotes

```bash
sudo apt update
```

### 2.5: Instalar Docker

```bash
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Você verá:
```
Reading package lists... Done
Building dependency tree... Done
...
Setting up docker-ce (24.x.x~3-0~ubuntu-jammy) ...
Done.
```

### 2.6: Verificar Instalação

```bash
docker --version
```

Você deve ver:
```
Docker version 24.0.x, build xxxxxxx
```

✅ **Docker instalado com sucesso!**

---

## ✅ Passo 3: Instalar Docker Compose

### 3.1: Baixar Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

Você verá:
```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 50.2M  100 50.2M    0     0  5.2M      0  0:00:09  0:00:09 --:--:--  0:00:09
```

### 3.2: Dar Permissão de Execução

```bash
sudo chmod +x /usr/local/bin/docker-compose
```

Não retorna nada (silencioso = sucesso ✅)

### 3.3: Verificar Instalação

```bash
docker-compose --version
```

Você deve ver:
```
Docker Compose version 2.x.x, build xxxxxxx
```

✅ **Docker Compose instalado com sucesso!**

---

## ✅ Passo 4: Instalar Git

```bash
sudo apt install -y git
```

Você verá:
```
Reading package lists... Done
...
Setting up git (1:2.x.x-1ubuntu1) ...
Done.
```

Verificar:

```bash
git --version
```

Você deve ver:
```
git version 2.x.x
```

✅ **Git instalado com sucesso!**

---

## ✅ Passo 5: Clonar Repositório

### 5.1: Criar Diretório (Opcional)

```bash
mkdir -p ~/projetos
cd ~/projetos
```

### 5.2: Clonar Repositório

```bash
git clone https://github.com/ismaeldomingosdesousa-ctrl/kora-vision.git
```

Você verá:
```
Cloning into 'kora-vision'...
remote: Enumerating objects: 345, done.
remote: Counting objects: 100% (345/345), done.
remote: Compressing objects: 100% (274/274), done.
remote: Total 345 (delta 88), reused 314 (delta 57), pack-reused 0
Receiving objects: 100% (345/345), 270.57 KiB | 20.81 MiB/s, done.
Resolving deltas: 100% (88/done.
```

### 5.3: Entrar no Diretório

```bash
cd kora-vision
```

### 5.4: Verificar Estrutura

```bash
ls -la
```

Você deve ver:
```
total 204
drwxrwxr-x  6 ubuntu ubuntu  4096 Mar 27 17:50 .
drwxrwxrwt 20 root   root    4096 Mar 27 17:50 ..
-rw-rw-r--  1 ubuntu ubuntu   770 Mar 27 17:50 .env.example
drwxrwxr-x  8 ubuntu ubuntu  4096 Mar 27 17:50 .git
-rw-rw-r--  1 ubuntu ubuntu   486 Mar 27 17:50 .gitignore
drwxrwxr-x  8 ubuntu ubuntu  4096 Mar 27 17:50 backend
drwxrwxr-x  6 ubuntu ubuntu  4096 Mar 27 17:50 frontend
drwxrwxr-x  5 ubuntu ubuntu  4096 Mar 27 17:50 infrastructure
-rw-rw-r--  1 ubuntu ubuntu  4033 Mar 27 17:50 docker-compose.yml
```

✅ **Repositório clonado com sucesso!**

---

## ✅ Passo 6: Configurar Ambiente

### 6.1: Copiar Arquivo de Exemplo

```bash
cp .env.example .env
```

Não retorna nada (silencioso = sucesso ✅)

### 6.2: Verificar Arquivo

```bash
cat .env
```

Você deve ver:
```
DB_USER=admin
DB_PASSWORD=changeme
DB_NAME=koravision
JWT_SECRET=your-secret-key-change-in-production
ENVIRONMENT=development
```

✅ **Ambiente configurado com sucesso!**

---

## ✅ Passo 7: Build das Imagens

### 7.1: Limpar Ambiente (Primeira Vez)

```bash
docker-compose down -v 2>/dev/null || true
```

Você pode ver:
```
No such file or directory
```

Isso é normal (primeira vez).

### 7.2: Limpar Cache

```bash
docker system prune -a -f
```

Você verá:
```
Deleted Images:
Deleted build cache objects:
Total reclaimed space: 0B
```

### 7.3: Build das Imagens

```bash
docker-compose build
```

**ISSO VAI LEVAR 10-15 MINUTOS NA PRIMEIRA VEZ!**

Você verá algo como:

```
[+] Building 45.3s (34/56)
 => [internal] load local bake definitions                                0.0s
 => [postgres:15-alpine] Pulled                                          18.5s
 => [redis:7-alpine] Pulled                                               6.4s
 => [core-api builder 1/5] FROM python:3.11-slim                          7.5s
 => [core-api builder 2/5] WORKDIR /app                                   0.1s
 => [core-api builder 3/5] RUN apt-get update && apt-get install...      28.6s
 => [core-api builder 4/5] COPY requirements.txt .                        0.0s
 => [core-api builder 5/5] RUN pip install --user --no-cache-dir...      15.2s
 => [frontend builder 1/7] FROM node:22-alpine                           13.5s
 => [frontend builder 2/7] WORKDIR /app                                   0.1s
 => [frontend builder 3/7] COPY package.json pnpm-lock.yaml ./            0.0s
 => [frontend builder 4/7] RUN npm install -g pnpm && pnpm install...    45.3s
 => [frontend builder 5/7] COPY . .                                       0.1s
 => [frontend builder 6/7] RUN pnpm run build                             8.2s
 => [frontend builder 7/7] RUN pnpm start                                 0.0s
...
```

**Aguarde até ver:**
```
[+] build complete
```

✅ **Build concluído com sucesso!**

---

## ✅ Passo 8: Iniciar Serviços

### 8.1: Iniciar Containers

```bash
docker-compose up -d
```

Você verá:
```
[+] Running 7/7
 ✔ Network kora-vision-network  Created                                   0.1s
 ✔ Container kora-vision-postgres            Started                      1.2s
 ✔ Container kora-vision-redis               Started                      1.3s
 ✔ Container kora-vision-core-api            Started                      2.1s
 ✔ Container kora-vision-webhook-ingestor    Started                      2.2s
 ✔ Container kora-vision-integration-worker  Started                      2.3s
 ✔ Container kora-vision-realtime-service    Started                      2.4s
 ✔ Container kora-vision-frontend            Started                      2.5s
```

### 8.2: Aguardar Inicialização

```bash
sleep 20
```

Isso aguarda 20 segundos para tudo inicializar.

### 8.3: Verificar Status

```bash
docker-compose ps
```

Você deve ver:
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

✅ **Todos os serviços rodando!**

---

## ✅ Passo 9: Executar Migrations

### 9.1: Conectar ao Container

```bash
docker-compose exec core-api bash
```

Você verá um novo prompt:
```
root@xxxxxxx:/app#
```

### 9.2: Entrar na Pasta de Migrations

```bash
cd migrations
```

### 9.3: Executar Migrations

```bash
alembic upgrade head
```

Você verá:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl with target metadata
INFO  [alembic.runtime.migration] Will assume transactional DDL is supported by the backend
INFO  [alembic.runtime.migration] Running upgrade  -> xxxxx, create initial schema
INFO  [alembic.runtime.migration] Running upgrade xxxxx -> xxxxx, add users table
...
```

### 9.4: Sair do Container

```bash
exit
```

Você voltará ao prompt normal:
```
ubuntu@hostname:~/projetos/kora-vision$
```

✅ **Migrations executadas com sucesso!**

---

## ✅ Passo 10: Verificar Funcionamento

### 10.1: Testar Frontend

Abra seu navegador e acesse:

```
http://localhost:3000
```

Você deve ver o **Kora Vision Dashboard**! 🎉

### 10.2: Testar Core API

```bash
curl http://localhost:8000/health
```

Você deve ver:
```json
{"status":"ok"}
```

### 10.3: Testar Webhook Ingestor

```bash
curl http://localhost:8001/health
```

Você deve ver:
```json
{"status":"ok"}
```

### 10.4: Testar Integration Worker

```bash
curl http://localhost:8002/health
```

Você deve ver:
```json
{"status":"ok"}
```

### 10.5: Testar Real-time Service

```bash
curl http://localhost:8003/health
```

Você deve ver:
```json
{"status":"ok"}
```

### 10.6: Ver Documentação da API

Abra seu navegador e acesse:

```
http://localhost:8000/docs
```

Você verá o **Swagger UI** com toda a documentação da API! 📚

✅ **Tudo funcionando perfeitamente!**

---

## 🎯 Resumo Rápido (Se Quiser Repetir)

```bash
# 1. Atualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar Docker
sudo apt install -y docker.io docker-compose

# 3. Instalar Git
sudo apt install -y git

# 4. Clonar repositório
git clone https://github.com/ismaeldomingosdesousa-ctrl/kora-vision.git
cd kora-vision

# 5. Configurar
cp .env.example .env

# 6. Build
docker-compose build

# 7. Iniciar
docker-compose up -d
sleep 20

# 8. Migrations
docker-compose exec core-api bash
cd migrations
alembic upgrade head
exit

# 9. Acessar
# http://localhost:3000
```

---

## 🛑 Se Tiver Problemas

### Porta em Uso

```bash
# Encontre o processo
lsof -i :3000

# Mate o processo
kill -9 <PID>
```

### Container Exited

```bash
# Veja os logs
docker-compose logs <nome-do-container>

# Reinicie
docker-compose restart <nome-do-container>
```

### Build Falha

```bash
# Limpe tudo
docker-compose down -v
docker system prune -a -f

# Tente novamente
docker-compose build --no-cache
```

### Banco Não Conecta

```bash
# Reinicie PostgreSQL
docker-compose restart postgres
sleep 10
docker-compose ps
```

---

## 📊 Monitorar Logs

### Ver Todos os Logs

```bash
docker-compose logs -f
```

Pressione `Ctrl+C` para sair.

### Ver Logs de um Serviço

```bash
docker-compose logs -f core-api
docker-compose logs -f frontend
docker-compose logs -f postgres
```

---

## 🎁 Próximas Etapas

1. ✅ Acessar http://localhost:3000
2. ✅ Explorar o dashboard
3. ✅ Testar as APIs em http://localhost:8000/docs
4. ✅ Configurar integrações
5. ✅ Monitorar os logs

---

## 📞 Precisa de Ajuda?

Se tiver dúvidas em algum passo:

1. **Verifique os logs:** `docker-compose logs`
2. **Reinicie tudo:** `docker-compose down && docker-compose up -d`
3. **Limpe tudo:** `docker system prune -a -f`
4. **Consulte a documentação:** Veja os arquivos *.md no repositório

---

**Parabéns! Você agora tem o Kora Vision rodando localmente! 🚀**

Qualquer dúvida, é só chamar! 💪
