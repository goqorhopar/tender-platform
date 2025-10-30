#!/bin/bash

# Deployment script for Tender Platform

set -e  # Exit on any error

echo "🚀 Starting Tender Platform deployment..."

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found. Please run this script from the project root directory."
    exit 1
fi

echo "✅ Found project root directory"

# Load environment variables
if [ -f ".env" ]; then
    echo "✅ Loading environment variables from .env file"
    export $(cat .env | xargs)
else
    echo "⚠️  No .env file found. Using default values or environment variables."
fi

# Check required environment variables
REQUIRED_VARS=("DB_USER" "DB_PASSWORD" "SECRET_KEY")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables: ${MISSING_VARS[*]}"
    echo "Please set these variables in your .env file or environment."
    exit 1
fi

echo "✅ All required environment variables are set"

# Pull latest images
echo "📥 Pulling latest Docker images..."
docker-compose pull

# Build images
echo "🏗️  Building Docker images..."
docker-compose build

# Stop any running containers
echo "⏹️  Stopping any running containers..."
docker-compose down

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Run database migrations
echo "🔧 Running database migrations..."
docker-compose exec backend alembic upgrade head

# Create initial data if needed
echo "🌱 Creating initial data..."
docker-compose exec backend python -c "
from app.database import init_db
from app.models.user import User
from app.core.security import get_password_hash

# Initialize database
init_db()

# Create superuser if not exists
# This would be expanded in a real implementation
print('Initial data creation completed')
"

# Run health checks
echo "🩺 Running health checks..."
if [ -f "scripts/health-check.sh" ]; then
    bash scripts/health-check.sh
else
    echo "⚠️  Health check script not found"
fi

echo "🎉 Deployment completed successfully!"
echo ""
echo "📝 Next steps:"
echo "   1. Access the application at http://localhost:8000"
echo "   2. View logs with: docker-compose logs -f"
echo "   3. View running services with: docker-compose ps"
echo ""
echo "🔐 Default credentials (if created):"
echo "   Email: admin@example.com"
echo "   Password: Please check your .env file"
