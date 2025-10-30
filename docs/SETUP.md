# Tender Platform - Setup Guide

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine + Docker Compose (Linux)
- Git
- Python 3.11+ (optional, for local development)
- Node.js 18+ (optional, for frontend development)

## Quick Setup

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd tender-platform

# Copy environment file
cp backend/.env.example backend/.env
```

### 2. Configure Environment Variables

Edit `backend/.env` and update the following critical settings:

```bash
# Generate a secure secret key (use this command):
# openssl rand -hex 32

SECRET_KEY=your-generated-secret-key-here

# For production, set:
ENVIRONMENT=production
DEBUG=false
```

### 3. Start Services

```bash
# Start all services in detached mode
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f
```

### 4. Verify Installation

```bash
# Run verification script
python scripts/verify-setup.py

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/
```

### 5. Access Services

- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Service Architecture

The platform consists of the following services:

1. **postgres** - PostgreSQL 15 database
2. **redis** - Redis cache and message broker
3. **backend** - FastAPI application server
4. **celery_worker** - Background task processor
5. **celery_beat** - Periodic task scheduler

## Development Workflow

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally (without Docker)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
# Create a new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker compose exec backend alembic upgrade head

# Rollback migration
docker compose exec backend alembic downgrade -1
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f celery_worker
docker compose logs -f postgres

# Last 100 lines
docker compose logs --tail=100 backend
```

### Accessing Service Shells

```bash
# Backend Python shell
docker compose exec backend python

# PostgreSQL shell
docker compose exec postgres psql -U tender_user -d tender_platform

# Redis CLI
docker compose exec redis redis-cli
```

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker version

# Check for port conflicts
netstat -an | findstr "8000 5432 6379"  # Windows
lsof -i :8000,5432,6379  # Linux/Mac

# Remove old containers and volumes
docker compose down -v
docker compose up -d
```

### Database Connection Issues

```bash
# Check PostgreSQL is healthy
docker compose exec postgres pg_isready -U tender_user

# View PostgreSQL logs
docker compose logs postgres

# Restart PostgreSQL
docker compose restart postgres
```

### Redis Connection Issues

```bash
# Test Redis connection
docker compose exec redis redis-cli ping

# View Redis logs
docker compose logs redis

# Restart Redis
docker compose restart redis
```

### Backend Application Errors

```bash
# View detailed logs
docker compose logs -f backend

# Check application logs file
docker compose exec backend cat logs/app.log

# Restart backend
docker compose restart backend
```

### Celery Worker Issues

```bash
# Check worker status
docker compose logs celery_worker

# Restart worker
docker compose restart celery_worker

# Check Celery Beat scheduler
docker compose logs celery_beat
```

## Stopping Services

```bash
# Stop all services
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove containers + volumes (WARNING: deletes data)
docker compose down -v
```

## Configuration Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Application environment | `development` |
| `DEBUG` | Debug mode | `true` |
| `SECRET_KEY` | JWT secret key | (must be set) |
| `POSTGRES_HOST` | PostgreSQL host | `postgres` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_USER` | PostgreSQL user | `tender_user` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `tender_password` |
| `POSTGRES_DB` | PostgreSQL database | `tender_platform` |
| `REDIS_HOST` | Redis host | `redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FILE` | Log file path | `logs/app.log` |
| `LOG_MAX_BYTES` | Max log file size | `10485760` (10MB) |
| `LOG_BACKUP_COUNT` | Number of log backups | `5` |

### Docker Compose Services

All services are connected via the `tender_network` bridge network.

**Volumes:**
- `postgres_data` - PostgreSQL data persistence
- `redis_data` - Redis data persistence
- `backend_logs` - Application logs

**Health Checks:**
- PostgreSQL: `pg_isready` command
- Redis: `redis-cli ping` command

## Next Steps

After successful setup:

1. **Run Database Migrations**: Create initial database schema
2. **Create Admin User**: Set up first administrator account
3. **Configure AI Services**: Add API keys for OpenAI/Claude/Gemini
4. **Set Up Integrations**: Configure ЕИС and ЭТП credentials
5. **Test Core Features**: Verify tender search and monitoring

See the main [README.md](../README.md) for feature documentation.

## Support

For issues and questions:
- Check logs: `docker compose logs -f`
- Run verification: `python scripts/verify-setup.py`
- Review documentation in `docs/` directory
