#!/bin/bash
set -e

echo "🚀 Iniciando setup do Kora Vision..."

# Update system
apt-get update
apt-get upgrade -y

# Install Python 3.11
apt-get install -y python3.11 python3.11-venv python3-pip

# Install Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
apt-get install -y nodejs

# Install PostgreSQL client
apt-get install -y postgresql-client

# Install Git
apt-get install -y git

# Install Docker
apt-get install -y docker.io
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone repository
cd /home/ubuntu
git clone https://github.com/ismaeldomingosdesousa-ctrl/kora-vision.git
cd kora-vision

# Setup backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup environment variables
cat > .env << EOF
DATABASE_URL=postgresql://admin:${db_password}@${db_host}/koravision
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=kora-vision-secret-key-change-in-production
COGNITO_USER_POOL_ID=us-east-1_xxxxx
COGNITO_CLIENT_ID=xxxxx
COGNITO_CLIENT_SECRET=xxxxx
EOF

# Run migrations
cd migrations
alembic upgrade head
cd ..

echo "✅ Setup concluído!"
echo "📝 Próximos passos:"
echo "1. SSH para a instância: ssh -i ~/.ssh/id_rsa ubuntu@${ec2_ip}"
echo "2. Iniciar backend: cd /home/ubuntu/kora-vision/backend && source venv/bin/activate && python -m uvicorn core-api.main:app --host 0.0.0.0 --port 8000"
echo "3. Frontend: npm run build && npm run preview"
