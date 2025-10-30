#!/bin/bash
# Infrastructure testing script for Tender Platform

set -e

echo "=========================================="
echo "Tender Platform Infrastructure Test"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check Docker
echo "Checking Docker..."
if command -v docker &> /dev/null; then
    print_success "Docker is installed"
    docker --version
else
    print_error "Docker is not installed"
    exit 1
fi
echo ""

# Check Docker Compose
echo "Checking Docker Compose..."
if command -v docker compose &> /dev/null; then
    print_success "Docker Compose is installed"
    docker compose version
else
    print_error "Docker Compose is not installed"
    exit 1
fi
echo ""

# Validate docker-compose.yml
echo "Validating docker-compose.yml..."
if docker compose config > /dev/null 2>&1; then
    print_success "docker-compose.yml is valid"
else
    print_error "docker-compose.yml has errors"
    exit 1
fi
echo ""

# Check if services are running
echo "Checking running services..."
if docker compose ps | grep -q "Up"; then
    print_info "Some services are already running"
    docker compose ps
else
    print_info "No services are currently running"
fi
echo ""

# Start services
echo "Starting services..."
print_info "This may take a few minutes on first run..."
docker compose up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check PostgreSQL
echo ""
echo "Testing PostgreSQL connection..."
if docker compose exec -T postgres pg_isready -U tender_user -d tender_platform > /dev/null 2>&1; then
    print_success "PostgreSQL is healthy"
else
    print_error "PostgreSQL is not responding"
fi

# Check Redis
echo "Testing Redis connection..."
if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is healthy"
else
    print_error "Redis is not responding"
fi

# Check Backend API
echo "Testing Backend API..."
sleep 5  # Give backend time to start
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend API is responding"
    echo "Response:"
    curl -s http://localhost:8000/health | python -m json.tool
else
    print_error "Backend API is not responding"
fi

# Check API root endpoint
echo ""
echo "Testing API root endpoint..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    print_success "API root endpoint is responding"
    echo "Response:"
    curl -s http://localhost:8000/ | python -m json.tool
else
    print_error "API root endpoint is not responding"
fi

# Check Celery Worker
echo ""
echo "Checking Celery Worker..."
if docker compose logs celery_worker | grep -q "ready"; then
    print_success "Celery Worker is running"
else
    print_info "Celery Worker may still be starting..."
fi

# Check Celery Beat
echo "Checking Celery Beat..."
if docker compose logs celery_beat | grep -q "beat"; then
    print_success "Celery Beat is running"
else
    print_info "Celery Beat may still be starting..."
fi

# Show service status
echo ""
echo "=========================================="
echo "Service Status:"
echo "=========================================="
docker compose ps

# Show logs summary
echo ""
echo "=========================================="
echo "Recent Logs (last 20 lines):"
echo "=========================================="
docker compose logs --tail=20

echo ""
echo "=========================================="
echo "Infrastructure Test Complete!"
echo "=========================================="
echo ""
print_info "Access points:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Health Check: http://localhost:8000/health"
echo ""
print_info "To view logs: docker compose logs -f"
print_info "To stop services: docker compose down"
echo ""
