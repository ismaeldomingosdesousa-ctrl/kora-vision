# 🚀 Kora Vision - Deployment AWS Free-Tier

Este guia descreve como fazer deploy do Kora Vision usando AWS Free-Tier com Terraform.

## 📋 Pré-requisitos

- ✅ Conta AWS (Free-Tier elegível)
- ✅ Terraform >= 1.0
- ✅ AWS CLI configurado
- ✅ SSH key pair gerado

## 🎯 Arquitetura Free-Tier

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

## 🔑 Passo 1: Preparar SSH Key

Se você não tem uma SSH key:

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
```

## 🔐 Passo 2: Configurar AWS Credentials

```bash
# Opção 1: Via AWS CLI
aws configure
# Insira:
# - Access Key ID: <seu-access-key-id>
# - Secret Access Key: <sua-secret-access-key>
# - Region: us-east-1
# - Output: json

# Opção 2: Via variáveis de ambiente
export AWS_ACCESS_KEY_ID=<seu-access-key-id>
export AWS_SECRET_ACCESS_KEY=<sua-secret-access-key>
export AWS_DEFAULT_REGION=us-east-1
```

## 📦 Passo 3: Inicializar Terraform

```bash
cd infrastructure/terraform

# Inicializar Terraform
terraform init

# Validar configuração
terraform validate

# Planejar deployment
terraform plan -out=tfplan
```

## 🚀 Passo 4: Fazer Deploy

```bash
# Aplicar configuração
terraform apply tfplan

# Aguarde 5-10 minutos...
# Terraform vai criar:
# - VPC com subnets
# - EC2 t2.micro
# - RDS PostgreSQL
# - S3 bucket
# - CloudFront distribution
```

## 📊 Passo 5: Verificar Outputs

Após o deploy, você verá outputs como:

```
ec2_public_ip = "54.123.45.67"
rds_endpoint = "kora-vision-db.c9akciq32.us-east-1.rds.amazonaws.com:5432"
s3_bucket_name = "kora-vision-frontend-123456789"
cloudfront_domain_name = "d1234567.cloudfront.net"
ssh_command = "ssh -i ~/.ssh/id_rsa ubuntu@54.123.45.67"
```

## 🔗 Passo 6: Conectar ao EC2

```bash
# SSH para a instância
ssh -i ~/.ssh/id_rsa ubuntu@54.123.45.67

# Verificar status
systemctl status docker
docker ps
```

## 🐳 Passo 7: Iniciar Backend

```bash
# Na instância EC2
cd /home/ubuntu/kora-vision/backend

# Ativar venv
source venv/bin/activate

# Iniciar serviços
python -m uvicorn core-api.main:app --host 0.0.0.0 --port 8000
```

## 🌐 Passo 8: Deploy Frontend

```bash
# Localmente
cd frontend/kora-vision-frontend

# Build
npm run build

# Upload para S3
aws s3 sync dist/ s3://kora-vision-frontend-123456789/ --delete

# Invalidar CloudFront cache
aws cloudfront create-invalidation --distribution-id D1234567 --paths "/*"
```

## 📝 Variáveis de Ambiente

Crie `.env` no EC2:

```bash
# Database
DATABASE_URL=postgresql://admin:PASSWORD@kora-vision-db.c9akciq32.us-east-1.rds.amazonaws.com:5432/koravision

# Redis (opcional - instalar no EC2)
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production

# Cognito (opcional)
COGNITO_USER_POOL_ID=us-east-1_xxxxx
COGNITO_CLIENT_ID=xxxxx
COGNITO_CLIENT_SECRET=xxxxx
```

## 🔍 Monitoramento

### Ver logs do EC2
```bash
ssh -i ~/.ssh/id_rsa ubuntu@54.123.45.67
tail -f /var/log/cloud-init-output.log
```

### Ver logs do RDS
```bash
aws rds describe-db-instances --db-instance-identifier kora-vision-db
```

### Ver status do S3
```bash
aws s3 ls s3://kora-vision-frontend-123456789/
```

## 💰 Custos

| Serviço | Free-Tier | Custo |
|---------|-----------|-------|
| EC2 t2.micro | 750 horas/mês | R$ 0 |
| RDS PostgreSQL t3.micro | 750 horas/mês | R$ 0 |
| S3 | 5GB storage | R$ 0 |
| CloudFront | 50GB/mês | R$ 0 |
| **Total** | - | **R$ 0** |

> ⚠️ Após 12 meses, será cobrado. Veja [AWS Free-Tier](https://aws.amazon.com/free/) para detalhes.

## 🧹 Destruir Infraestrutura

Se quiser remover tudo:

```bash
cd infrastructure/terraform
terraform destroy
```

## 🐛 Troubleshooting

### Erro: "Access Denied"
- Verifique se as credenciais AWS estão corretas
- Confirme se o usuário IAM tem permissões de admin

### Erro: "SSH key not found"
- Gere uma nova key: `ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa`
- Atualize o Terraform com o caminho correto

### Erro: "RDS connection failed"
- Aguarde 5 minutos após o deploy
- Verifique security groups
- Teste: `psql -h <rds-endpoint> -U admin -d koravision`

### EC2 não inicia
- Verifique logs: `aws ec2 describe-instances --instance-ids i-xxxxx`
- Veja user_data: `cat /var/log/cloud-init-output.log`

## 📚 Documentação Adicional

- [AWS Free-Tier](https://aws.amazon.com/free/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Kora Vision Architecture](./PHASE_0_ARCHITECTURE.md)

---

**Pronto! Seu Kora Vision está rodando na AWS Free-Tier! 🎉**
