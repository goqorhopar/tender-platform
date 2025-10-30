#!/bin/bash

# Health check script for Tender Platform services

echo "Checking Tender Platform services health..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "❌ docker-compose is not available"
    exit 1
fi

echo "✅ docker-compose is available"

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Containers are running"
else
    echo "⚠️  No containers are currently running"
fi

# Check PostgreSQL
if docker-compose exec postgres pg_isready >/dev/null 2>&1; then
    echo "✅ PostgreSQL is healthy"
else
    echo "❌ PostgreSQL is not responding"
fi

# Check Redis
if docker-compose exec redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis is not responding"
fi

# Check backend API
if curl -s http://localhost:8000/api/v1/health | grep -q '"status":"healthy"'; then
    echo "✅ Backend API is healthy"
else
    echo "❌ Backend API is not responding"
fi

# Check if required environment variables are set
REQUIRED_VARS=("DB_USER" "DB_PASSWORD" "SECRET_KEY")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    echo "✅ All required environment variables are set"
else
    echo "❌ Missing required environment variables: ${MISSING_VARS[*]}"
fi

echo "Health check completed."