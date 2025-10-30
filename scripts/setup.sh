#!/bin/bash

# Tender Platform Setup Script

echo "🚀 Setting up Tender Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating .env file from example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env and set your SECRET_KEY before running in production!"
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p backend/logs

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
docker-compose ps

# Show logs
echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Services status:"
docker-compose ps
echo ""
echo "🌐 Access the application:"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/health"
echo ""
echo "📝 View logs:"
echo "   docker-compose logs -f backend"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
