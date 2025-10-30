# Makefile for Tender Platform development

.PHONY: help install start stop restart logs test clean deploy health

# Default target
help:
	@echo "Tender Platform Development Commands"
	@echo "====================================="
	@echo "make install     - Install dependencies"
	@echo "make start       - Start all services"
	@echo "make stop        - Stop all services"
	@echo "make restart     - Restart all services"
	@echo "make logs        - View service logs"
	@echo "make test        - Run tests"
	@echo "make clean       - Clean up containers and volumes"
	@echo "make deploy      - Deploy the application"
	@echo "make health      - Check service health"
	@echo "make migrate     - Run database migrations"
	@echo "make shell       - Open backend shell"
	@echo "make db-shell    - Open database shell"

# Install dependencies
install:
	pip install -r backend/requirements.txt
	cd backend && pip install -e .

# Start services
start:
	docker-compose up -d

# Stop services
stop:
	docker-compose down

# Restart services
restart:
	docker-compose down
	docker-compose up -d

# View logs
logs:
	docker-compose logs -f

# Run tests
test:
	docker-compose exec backend pytest

# Clean up
clean:
	docker-compose down -v --remove-orphans

# Deploy application
deploy:
	bash scripts/deploy.sh

# Check health
health:
	bash scripts/health-check.sh

# Run database migrations
migrate:
	docker-compose exec backend alembic upgrade head

# Open backend shell
shell:
	docker-compose exec backend bash

# Open database shell
db-shell:
	docker-compose exec postgres psql -U tender_user -d tender_platform