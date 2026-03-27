# 🐳 Guia Completo: Instalar Docker no Ubuntu e Rodar Kora Vision

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Instalar Docker](#instalar-docker)
3. [Instalar Docker Compose](#instalar-docker-compose)
4. [Clonar Kora Vision](#clonar-kora-vision)
5. [Configurar Ambiente](#configurar-ambiente)
6. [Iniciar Aplicação](#iniciar-aplicação)
7. [Verificar Status](#verificar-status)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 Pré-requisitos

### Requisitos Mínimos

- **Ubuntu 20.04+** (18.04 também funciona)
- **CPU:** 2+ cores
- **RAM:** 4GB mínimo (8GB recomendado)
- **Disco:** 20GB livres
- **Conexão com internet**

### Verificar Versão do Ubuntu

```bash
lsb_release -a
# ou
cat /etc/os-release
```

---

## 🐳 Instalar Docker

### Passo 1: Atualizar o Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### Passo 2: Instalar Dependências

```bash
sudo apt install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release
```

### Passo 3: Adicionar Chave GPG do Docker

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

### Passo 4: Adicionar Repositório do Docker

```bash
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### Passo 5: Instalar Docker

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Passo 6: Verificar Instalação

```bash
docker --version
# Saída esperada: Docker version 24.x.x (ou superior)
```

### Passo 7: Testar Docker

```bash
sudo docker run hello-world
```

Se vir "Hello from Docker!", está funcionando! ✅

---

## 👤 Configurar Permissões de Usuário

Por padrão, Docker requer `sudo`. Para usar sem `sudo`:

### Passo 1: Criar Grupo Docker

```bash
sudo groupadd docker
```

(Se o grupo já existe, ignore o erro)

### Passo 2: Adicionar Seu Usuário ao Grupo

```bash
sudo usermod -aG docker $USER
```

### Passo 3: Ativar as Mudanças

```bash
newgrp docker
```

### Passo 4: Verificar

```bash
docker run hello-world
# Sem sudo!
```

Se funcionar, você pode usar `docker` sem `sudo` agora! ✅

---

## 🔧 Instalar Docker Compose

### Passo 1: Download da Versão Mais Recente

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

### Passo 2: Dar Permissão de Execução

```bash
sudo chmod +x /usr/local/bin/docker-compose
```

### Passo 3: Verificar Instalação

```bash
docker-compose --version
# Saída esperada: Docker Compose version 2.x.x (ou superior)
```

---

## 📥 Clonar Kora Vision

### Passo 1: Instalar Git (se não tiver)

```bash
sudo apt install -y git
```

### Passo 2: Clonar o Repositório

```bash
git clone https://github.com/ismaeldomingosdesousa-ctrl/kora-vision.git
cd kora-vision
```

### Passo 3: Verificar Estrutura

```bash
ls -la
# Você deve ver:
# docker-compose.yml
# .env.example
# backend/
# unified-ops-hub-frontend/
# infrastructure/
```

---

## ⚙️ Configurar Ambiente

### Passo 1: Copiar Arquivo de Exemplo

```bash
cp .env.example .env
```

### Passo 2: Editar Variáveis (Opcional)

```bash
nano .env
```

Variáveis importantes:

```bash
# Database
DB_USER=admin
DB_PASSWORD=changeme
DB_NAME=koravision

# JWT Secret (mude isso em produção!)
JWT_SECRET=your-secret-key-change-in-production

# Environment
ENVIRONMENT=development
```

Salve com `Ctrl+X`, depois `Y`, depois `Enter`.

---

## 🚀 Iniciar Aplicação

### Passo 1: Build das Imagens

```bash
docker-compose build
```

**Primeira vez:** Pode levar 5-10 minutos (depende da internet)

**Próximas vezes:** Muito mais rápido (usa cache)

### Passo 2: Iniciar os Serviços

```bash
docker-compose up -d
```

O `-d` significa "detached" (roda em background)

### Passo 3: Aguardar Inicialização

```bash
sleep 10
docker-compose ps
```

Você deve ver todos os serviços com status `Up`:

```
NAME                        STATUS
kora-vision-postgres        Up 2 minutes
kora-vision-redis           Up 2 minutes
kora-vision-core-api        Up 2 minutes
kora-vision-webhook-ingestor Up 2 minutes
kora-vision-integration-worker Up 2 minutes
kora-vision-realtime-service Up 2 minutes
kora-vision-frontend        Up 2 minutes
```

### Passo 4: Executar Migrations (Primeira Vez)

```bash
docker-compose exec core-api bash
```

Dentro do container:

```bash
cd migrations
alembic upgrade head
exit
```

---

## ✅ Verificar Status

### Acessar a Aplicação

Abra no navegador:

```
http://localhost:3000
```

Você deve ver o **Kora Vision Dashboard**! 🎉

### Testar APIs

```bash
# Core API
curl http://localhost:8000/health

# Webhook Ingestor
curl http://localhost:8001/health

# Integration Worker
curl http://localhost:8002/health

# Real-time Service
curl http://localhost:8003/health
```

Todos devem retornar `200 OK`.

### Ver Logs

```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f core-api

# Últimas 100 linhas
docker-compose logs --tail=100 core-api
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

### Reiniciar um Serviço Específico

```bash
docker-compose restart core-api
```

---

## 🔧 Troubleshooting

### Erro: "Permission denied while trying to connect to Docker daemon"

**Solução:**

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Depois faça logout e login novamente.

### Erro: "Port 3000 is already allocated"

**Solução:** Encontre e mate o processo:

```bash
sudo lsof -i :3000
sudo kill -9 <PID>
```

Ou mude a porta no `docker-compose.yml`:

```yaml
ports:
  - "3001:3000"  # Mude 3000 para 3001
```

### Erro: "Cannot connect to PostgreSQL"

**Solução:**

```bash
# Reinicie o banco de dados
docker-compose restart postgres

# Verifique os logs
docker-compose logs postgres
```

### Erro: "Out of disk space"

**Solução:** Limpe imagens e containers não usados:

```bash
docker system prune -a
```

### Erro: "Build failed"

**Solução:** Limpe tudo e comece do zero:

```bash
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

### Containers não iniciam

**Solução:** Verifique os logs:

```bash
docker-compose logs
```

Procure por erros vermelhos.

---

## 📊 Monitorar Recursos

### Ver Uso de CPU e Memória

```bash
docker stats
```

Pressione `Ctrl+C` para sair.

### Ver Espaço em Disco

```bash
docker system df
```

---

## 🔐 Segurança (Importante!)

### Mudar Senhas Padrão

Edite o `.env`:

```bash
nano .env
```

Mude:

```bash
DB_PASSWORD=sua-senha-super-segura
JWT_SECRET=sua-chave-secreta-aleatoria
```

### Gerar Chave Segura

```bash
openssl rand -base64 32
```

---

## 📈 Próximos Passos

1. **Acessar Dashboard:** http://localhost:3000
2. **Explorar APIs:** http://localhost:8000/docs
3. **Configurar Integrações:** Google Calendar, Jira, etc
4. **Testar Webhooks:** Enviar dados para http://localhost:8001/webhooks
5. **Monitorar Logs:** `docker-compose logs -f`

---

## 💾 Backup do Banco de Dados

### Fazer Backup

```bash
docker-compose exec postgres pg_dump -U admin koravision > backup.sql
```

### Restaurar Backup

```bash
docker-compose exec -T postgres psql -U admin koravision < backup.sql
```

---

## 🆘 Precisa de Ajuda?

Se tiver problemas:

1. **Verifique os logs:** `docker-compose logs`
2. **Reinicie tudo:** `docker-compose down && docker-compose up -d`
3. **Limpe tudo:** `docker system prune -a` (cuidado!)
4. **Consulte a documentação:** Veja os arquivos PHASE_*.md

---

## ✨ Dicas Finais

- **Primeira inicialização:** Pode levar 5-10 minutos
- **Próximas inicializações:** Muito mais rápidas (usa cache)
- **Desenvolvimento:** Use `docker-compose up` (sem `-d`) para ver logs em tempo real
- **Produção:** Use `docker-compose up -d` para rodar em background

---

**Parabéns! Você agora tem o Kora Vision rodando localmente! 🎉**

Para mais informações, consulte:
- https://docs.docker.com/
- https://docs.docker.com/compose/
- https://github.com/ismaeldomingosdesousa-ctrl/kora-vision
