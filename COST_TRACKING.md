# 💰 Kora Vision - Cost Tracking Guide

Este guia descreve como acompanhar e gerenciar os custos da infraestrutura Kora Vision usando tags AWS.

## 🏷️ Tags de Custo Implementadas

O template CloudFormation agora inclui as seguintes tags para rastreamento de custos:

| Tag | Descrição | Exemplo |
|-----|-----------|---------|
| **CostCenter** | Centro de custo para faturamento | `kora-vision` |
| **Environment** | Ambiente (dev, staging, mvp, production) | `mvp` |
| **Project** | Nome do projeto | `kora-vision` |
| **Owner** | Proprietário/Time responsável | `admin` |
| **ResourceType** | Tipo de recurso (compute, database, storage, cdn) | `compute` |
| **CreatedDate** | Data de criação (stack name) | `kora-vision-stack` |

## 📊 Configurar Cost Allocation Tags

### Passo 1: Ativar Tags no AWS Billing

1. Acesse: https://console.aws.amazon.com/billing/
2. No menu esquerdo, clique em **"Cost Allocation Tags"**
3. Na aba **"User-Defined Tags"**, você verá as tags criadas
4. Para cada tag, clique em **"Activate"**

Tags ativadas:
- ✅ CostCenter
- ✅ Environment
- ✅ Project
- ✅ Owner
- ✅ ResourceType

### Passo 2: Aguardar Ativação

- As tags levam **até 24 horas** para aparecer nos relatórios de custo
- Após ativação, você pode usar nos relatórios do Cost Explorer

## 📈 Usar Cost Explorer para Acompanhar Custos

### Acessar Cost Explorer

1. Acesse: https://console.aws.amazon.com/cost-management/home
2. Clique em **"Cost Explorer"**
3. No painel esquerdo, clique em **"Cost Explorer"**

### Filtrar por Tags

1. Clique em **"Add Filter"**
2. Selecione **"Tag"**
3. Escolha uma tag (ex: `CostCenter`)
4. Selecione o valor (ex: `kora-vision`)

### Exemplos de Análise

#### Custo Total do Projeto
```
Filter: Project = kora-vision
Período: Últimos 30 dias
Granularidade: Diária
```

#### Custo por Ambiente
```
Filter: Environment = mvp
Período: Últimos 30 dias
Agrupar por: Resource Type
```

#### Custo por Tipo de Recurso
```
Filter: Project = kora-vision
Período: Últimos 30 dias
Agrupar por: Resource Type
```

## 💾 Criar Alertas de Orçamento

### Passo 1: Acessar Budgets

1. Acesse: https://console.aws.amazon.com/billing/
2. No menu esquerdo, clique em **"Budgets"**
3. Clique em **"Create budget"**

### Passo 2: Configurar Orçamento

1. **Budget Type**: Selecione "Cost budget"
2. **Budget Name**: `kora-vision-monthly`
3. **Period**: Monthly
4. **Budget Amount**: R$ 50 (ou o valor que preferir)
5. **Start Month**: Selecione o mês atual

### Passo 3: Configurar Alertas

1. Clique em **"Add an alert threshold"**
2. **Alert threshold**: 80% of budgeted amount
3. **Email recipients**: Seu email
4. Clique em **"Create budget"**

## 📋 Exemplo de Parâmetros no Deploy

Quando você fizer deploy do CloudFormation, preencha:

```
KeyPairName: kora-vision
DBMasterUsername: admin
DBMasterPassword: SenhaForte123!
CostCenter: kora-vision
Environment: mvp
Project: kora-vision
Owner: seu-nome
```

## 🔍 Visualizar Custos por Recurso

### Via AWS Console

1. Acesse: https://console.aws.amazon.com/ec2/
2. Selecione um recurso (EC2, RDS, etc.)
3. Na aba **"Tags"**, você verá todas as tags aplicadas

### Via AWS CLI

```bash
# Listar tags de uma instância EC2
aws ec2 describe-tags \
  --filters "Name=resource-id,Values=i-1234567890abcdef0" \
  --region us-east-1

# Listar recursos com uma tag específica
aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=kora-vision" \
  --region us-east-1
```

## 📊 Relatório de Custos Esperados (Free-Tier)

| Recurso | Custo Mensal | Observação |
|---------|-------------|-----------|
| EC2 t2.micro | R$ 0 | 750 horas/mês grátis por 12 meses |
| RDS PostgreSQL t3.micro | R$ 0 | 750 horas/mês grátis por 12 meses |
| S3 | R$ 0 | 5GB grátis por mês |
| CloudFront | R$ 0 | 50GB/mês grátis por 12 meses |
| **TOTAL** | **R$ 0** | **Válido por 12 meses** |

### Após 12 Meses

| Recurso | Custo Estimado/mês |
|---------|------------------|
| EC2 t2.micro | ~R$ 40-60 |
| RDS PostgreSQL t3.micro | ~R$ 80-100 |
| S3 (5GB) | ~R$ 1-2 |
| CloudFront (50GB) | ~R$ 10-15 |
| **TOTAL** | **~R$ 130-180/mês** |

## ⚠️ Dicas para Reduzir Custos

1. **Usar Reserved Instances** — Economize até 70% em EC2/RDS
2. **Usar Savings Plans** — Desconto em uso de computação
3. **Monitorar uso** — Desligar recursos não utilizados
4. **Usar Auto-scaling** — Escalar conforme demanda
5. **Otimizar storage** — Usar S3 Intelligent-Tiering

## 🧹 Limpar Recursos

Se quiser remover tudo para economizar:

```bash
# Via AWS Console
# 1. CloudFormation → Stacks → Select stack → Delete

# Via AWS CLI
aws cloudformation delete-stack \
  --stack-name kora-vision \
  --region us-east-1
```

## 📚 Recursos Adicionais

- [AWS Cost Explorer Documentation](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html)
- [AWS Budgets Documentation](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
- [AWS Tagging Best Practices](https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html)
- [AWS Free-Tier](https://aws.amazon.com/free/)

---

**Agora você pode acompanhar todos os custos da Kora Vision! 💰**
