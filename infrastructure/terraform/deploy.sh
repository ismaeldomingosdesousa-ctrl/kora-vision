#!/bin/bash

set -e

echo "🚀 Kora Vision - AWS Free-Tier Deployment"
echo "=========================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar pré-requisitos
echo "📋 Verificando pré-requisitos..."

if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform não está instalado${NC}"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI não está instalado${NC}"
    exit 1
fi

if [ ! -f ~/.ssh/id_rsa.pub ]; then
    echo -e "${YELLOW}⚠️  SSH key não encontrada. Gerando...${NC}"
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
fi

echo -e "${GREEN}✅ Pré-requisitos OK${NC}"
echo ""

# Verificar credenciais AWS
echo "🔐 Verificando credenciais AWS..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ Credenciais AWS não configuradas${NC}"
    echo "Configure com: aws configure"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✅ Conectado à conta AWS: $ACCOUNT_ID${NC}"
echo ""

# Inicializar Terraform
echo "📦 Inicializando Terraform..."
terraform init

echo ""
echo "📊 Planejando deployment..."
terraform plan -out=tfplan

echo ""
echo -e "${YELLOW}⚠️  Revise o plano acima${NC}"
read -p "Deseja continuar com o deployment? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Deployment cancelado"
    exit 1
fi

echo ""
echo "🚀 Fazendo deploy..."
terraform apply tfplan

echo ""
echo -e "${GREEN}✅ Deployment concluído!${NC}"
echo ""

# Exibir outputs
echo "📊 Informações de acesso:"
echo "=========================="
terraform output -json | jq .

echo ""
echo "🔗 Próximos passos:"
echo "1. SSH para EC2: $(terraform output -raw ssh_command)"
echo "2. Aguarde 5-10 minutos para o EC2 inicializar"
echo "3. Conecte ao banco: psql -h $(terraform output -raw rds_endpoint | cut -d: -f1) -U admin -d koravision"
echo "4. Deploy frontend: aws s3 sync dist/ s3://$(terraform output -raw s3_bucket_name)/"
echo ""

echo -e "${GREEN}🎉 Kora Vision está sendo provisionado!${NC}"
