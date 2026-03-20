# 🚀 Kora Vision - Deployment com CloudFormation

Este guia descreve como fazer deploy do Kora Vision usando **AWS CloudFormation** (sem precisar instalar Terraform ou AWS CLI).

## 📋 Pré-requisitos

- ✅ Conta AWS (Free-Tier elegível)
- ✅ Acesso ao console AWS
- ✅ Uma EC2 Key Pair criada

## 🎯 Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    AWS Free-Tier                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  CloudFront CDN (Free)                           │   │
│  │  - 50GB/mês transferência                        │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │  S3 Bucket (Free)                                │   │
│  │  - 5GB storage                                   │   │
│  │  - Frontend React build                          │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  EC2 t2.micro (Free 12 meses)                   │   │
│  │  - Backend FastAPI                              │   │
│  │  - 1GB RAM, 1 vCPU                              │   │
│  │  - 750 horas/mês                                │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │  RDS PostgreSQL t3.micro (Free 12 meses)        │   │
│  │  - 20GB storage                                  │   │
│  │  - 750 horas/mês                                │   │
│  │  - Backup 7 dias                                │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘

Custo: R$ 0 por 12 meses!
```

## 🔑 Passo 1: Criar EC2 Key Pair

Se você não tem uma key pair:

1. Acesse: https://console.aws.amazon.com/ec2/
2. No menu esquerdo, clique em **"Key Pairs"**
3. Clique em **"Create key pair"**
4. Nome: `kora-vision`
5. Formato: `pem` (para Mac/Linux) ou `ppk` (para Windows)
6. Clique em **"Create key pair"**
7. O arquivo será baixado automaticamente

## 📦 Passo 2: Fazer Upload do Template CloudFormation

### Opção A: Via Console AWS (Mais Fácil)

1. Acesse: https://console.aws.amazon.com/cloudformation/
2. Clique em **"Create stack"**
3. Selecione **"Upload a template file"**
4. Clique em **"Choose file"**
5. Selecione: `infrastructure/cloudformation/kora-vision-free-tier.yaml`
6. Clique em **"Next"**

### Opção B: Via URL (Rápido)

1. Acesse: https://console.aws.amazon.com/cloudformation/
2. Clique em **"Create stack"**
3. Selecione **"Amazon S3 URL"**
4. Cole a URL (você precisa fazer upload do arquivo para S3 primeiro)

## ⚙️ Passo 3: Configurar Parâmetros

Na tela de parâmetros, preencha:

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| **KeyPairName** | `kora-vision` | Nome da EC2 Key Pair que você criou |
| **DBMasterUsername** | `admin` | Usuário do banco (deixar padrão) |
| **DBMasterPassword** | `SenhaForte123!` | Senha do banco (mínimo 8 caracteres) |

Clique em **"Next"**

## 🏷️ Passo 4: Configurar Tags (Opcional)

Você pode adicionar tags para organizar seus recursos:

```
Key: Project
Value: kora-vision

Key: Environment
Value: mvp
```

Clique em **"Next"**

## ✅ Passo 5: Revisar e Criar

1. Revise todas as configurações
2. Marque a caixa: **"I acknowledge that AWS CloudFormation might create IAM resources"**
3. Clique em **"Create stack"**

## ⏳ Passo 6: Aguardar Criação

O CloudFormation vai criar todos os recursos. Isso pode levar **10-15 minutos**.

Você pode acompanhar o progresso:
- Abra a aba **"Events"** para ver o que está sendo criado
- Quando terminar, o status será **"CREATE_COMPLETE"**

## 📊 Passo 7: Obter Informações de Acesso

Após a criação, clique na aba **"Outputs"** para ver:

| Output | Descrição |
|--------|-----------|
| **EC2PublicIP** | IP público da instância |
| **RDSEndpoint** | Endpoint do banco de dados |
| **S3BucketName** | Nome do bucket S3 |
| **CloudFrontDomainName** | URL pública do frontend |
| **SSHCommand** | Comando para conectar via SSH |
| **PSQLCommand** | Comando para conectar ao banco |

## 🔗 Passo 8: Conectar ao EC2

```bash
# Substitua /path/to/key.pem pelo caminho da sua key pair
ssh -i /path/to/kora-vision.pem ec2-user@<EC2PublicIP>

# Exemplo:
ssh -i ~/Downloads/kora-vision.pem ec2-user@54.123.45.67
```

## 🗄️ Passo 9: Conectar ao Banco de Dados

```bash
# Instale psql localmente (se não tiver)
# Mac: brew install postgresql
# Ubuntu: sudo apt-get install postgresql-client
# Windows: Download PostgreSQL

# Conecte ao banco
psql -h <RDSEndpoint> -U admin -d koravision
```

## 🌐 Passo 10: Deploy do Frontend

```bash
# Localmente, no seu computador

# 1. Build do frontend
cd frontend/kora-vision-frontend
npm install
npm run build

# 2. Upload para S3
aws s3 sync dist/ s3://<S3BucketName>/ --delete

# 3. Invalidar cache do CloudFront
aws cloudfront create-invalidation \
  --distribution-id <CloudFrontDistributionId> \
  --paths "/*"

# O frontend estará disponível em:
# https://<CloudFrontDomainName>
```

## 🚀 Passo 11: Iniciar Backend

```bash
# SSH para o EC2
ssh -i ~/Downloads/kora-vision.pem ec2-user@<EC2PublicIP>

# Dentro da instância
cd /home/ec2-user/kora-vision/backend

# Ativar venv
source venv/bin/activate

# Iniciar serviços
python -m uvicorn core-api.main:app --host 0.0.0.0 --port 8000
```

## 📝 Variáveis de Ambiente

O arquivo `.env` foi criado automaticamente no EC2 com:

```bash
DATABASE_URL=postgresql://admin:SENHA@<RDSEndpoint>:5432/koravision
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=kora-vision-secret-key-change-in-production
```

Para mudar, edite:
```bash
nano /home/ec2-user/kora-vision/backend/.env
```

## 💰 Custos

| Serviço | Free-Tier | Custo |
|---------|-----------|-------|
| EC2 t2.micro | 750 horas/mês | **R$ 0** |
| RDS PostgreSQL t3.micro | 750 horas/mês | **R$ 0** |
| S3 | 5GB storage | **R$ 0** |
| CloudFront | 50GB/mês | **R$ 0** |
| **TOTAL** | - | **R$ 0/mês** |

> ⚠️ Válido por 12 meses. Após isso, será cobrado conforme uso.

## 🧹 Deletar Stack (Remover Tudo)

Se quiser remover todos os recursos:

1. Acesse: https://console.aws.amazon.com/cloudformation/
2. Selecione o stack `kora-vision`
3. Clique em **"Delete"**
4. Confirme

⚠️ Isso vai deletar EC2, RDS, S3, CloudFront e tudo mais!

## 🐛 Troubleshooting

### Erro: "Key pair does not exist"
- Verifique se criou a key pair com o nome correto
- A key pair deve estar na mesma região (us-east-1)

### Erro: "Insufficient capacity"
- Tente outra availability zone
- Ou aguarde alguns minutos e tente novamente

### EC2 não inicializa
- Verifique os logs: https://console.aws.amazon.com/ec2/ → Instances → Select instance → Status checks
- Veja o user data log: `tail -f /var/log/cloud-init-output.log`

### Não consigo conectar ao RDS
- Aguarde 5 minutos após a criação
- Verifique se o security group permite conexão do EC2
- Teste: `psql -h <endpoint> -U admin -d koravision`

### Frontend não carrega
- Verifique se o build foi feito: `npm run build`
- Confirme upload para S3: `aws s3 ls s3://<bucket>/`
- Invalide cache CloudFront

## 📚 Próximos Passos

1. ✅ Stack criado
2. ✅ EC2 e RDS rodando
3. ✅ S3 e CloudFront configurados
4. 📝 Customizar backend (adicionar autenticação, etc.)
5. 📝 Deploy do frontend
6. 📝 Configurar domínio customizado

---

**Pronto! Seu Kora Vision está rodando na AWS Free-Tier! 🎉**

Para mais informações, veja:
- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [Kora Vision Architecture](./PHASE_0_ARCHITECTURE.md)
- [Deployment com Terraform](./DEPLOYMENT_FREE_TIER.md)
