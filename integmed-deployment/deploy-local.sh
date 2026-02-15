#!/bin/bash

# IntegMed - One-Click Local Deployment Script
# This script sets up the entire stack locally using Docker Compose

set -e

echo "🏥 IntegMed - Local Deployment"
echo "=============================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker found"

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker Compose found"

echo ""
echo "📦 Setting up project structure..."

# Create directory structure
mkdir -p backend frontend nginx/ssl

# Copy backend code
if [ -d "../integmed-backend" ]; then
    echo "Copying backend code..."
    cp -r ../integmed-backend/* backend/ 2>/dev/null || true
else
    echo -e "${YELLOW}⚠️  Backend code not found. Please extract integmed-backend.tar.gz${NC}"
fi

# Copy frontend code
if [ -d "../integmed-frontend" ]; then
    echo "Copying frontend code..."
    cp -r ../integmed-frontend/* frontend/ 2>/dev/null || true
else
    echo -e "${YELLOW}⚠️  Frontend code not found. Please set up frontend first${NC}"
fi

# Copy Dockerfiles
cp backend/Dockerfile backend/Dockerfile 2>/dev/null || echo "Backend Dockerfile in place"
cp frontend/Dockerfile frontend/Dockerfile 2>/dev/null || echo "Frontend Dockerfile in place"

echo ""
echo "🔧 Generating SSL certificates (self-signed for local development)..."
if [ ! -f nginx/ssl/cert.pem ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/privkey.pem \
        -out nginx/ssl/fullchain.pem \
        -subj "/C=IN/ST=Karnataka/L=Bengaluru/O=IntegMed/CN=localhost" \
        2>/dev/null || echo -e "${YELLOW}⚠️  SSL generation failed (optional for local dev)${NC}"
else
    echo "SSL certificates already exist"
fi

echo ""
echo "🗄️  Starting database initialization..."

# Create init.sql for database
cat > backend/init.sql << 'EOF'
-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE integmed TO integmed;
EOF

echo ""
echo "🚀 Starting Docker containers..."
echo ""

# Stop any existing containers
docker-compose down 2>/dev/null || true

# Build and start services
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."

# Wait for postgres
echo -n "Waiting for PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U integmed &> /dev/null; do
    echo -n "."
    sleep 1
done
echo -e " ${GREEN}✓${NC}"

# Wait for backend
echo -n "Waiting for Backend API..."
until curl -s http://localhost:8000/health &> /dev/null; do
    echo -n "."
    sleep 1
done
echo -e " ${GREEN}✓${NC}"

# Wait for frontend
echo -n "Waiting for Frontend..."
until curl -s http://localhost:3000 &> /dev/null; do
    echo -n "."
    sleep 1
done
echo -e " ${GREEN}✓${NC}"

echo ""
echo "🔄 Running database migrations..."
docker-compose exec -T backend alembic upgrade head || echo -e "${YELLOW}⚠️  Migrations not run (run manually if needed)${NC}"

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Access IntegMed:"
echo ""
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/api/docs"
echo "   Nginx:     http://localhost (reverse proxy)"
echo ""
echo "🗄️  Database:"
echo "   PostgreSQL: localhost:5432"
echo "   Username:   integmed"
echo "   Password:   integmed_dev_password"
echo "   Database:   integmed"
echo ""
echo "📊 Monitoring:"
echo "   docker-compose logs -f         (all logs)"
echo "   docker-compose logs -f backend (backend only)"
echo "   docker-compose ps              (service status)"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 Happy coding!"
echo ""
