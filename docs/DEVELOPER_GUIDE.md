# Developer Guide

This guide provides comprehensive information for developers working on the Tender Platform, including project structure, development workflow, testing, and contribution guidelines.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Development Environment](#development-environment)
3. [Code Standards](#code-standards)
4. [Database Migrations](#database-migrations)
5. [Testing](#testing)
6. [API Development](#api-development)
7. [Frontend Development](#frontend-development)
8. [Docker Development](#docker-development)
9. [Debugging](#debugging)
10. [Performance Optimization](#performance-optimization)
11. [Security Considerations](#security-considerations)
12. [Deployment](#deployment)
13. [Monitoring and Logging](#monitoring-and-logging)
14. [Contributing](#contributing)

## Project Structure

```
tender-platform/
├── backend/                 # Backend API (FastAPI)
│   ├── app/                 # Application code
│   │   ├── api/             # API endpoints
│   │   │   └── v1/          # API version 1
│   │   ├── models/          # Database models (SQLAlchemy)
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic services
│   │   ├── tasks/           # Celery tasks
│   │   ├── utils/           # Utility functions
│   │   ├── core/            # Core configurations and security
│   │   ├── database/        # Database connection and setup
│   │   └── main.py          # Application entry point
│   ├── tests/               # Unit and integration tests
│   ├── alembic/             # Database migrations
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Backend Dockerfile
│   └── ...
├── frontend/                 # Frontend application (React)
│   ├── public/              # Static assets
│   ├── src/                 # Source code
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── hooks/           # Custom hooks
│   │   ├── contexts/        # React contexts
│   │   ├── utils/           # Utility functions
│   │   ├── styles/          # Styling
│   │   ├── types/           # TypeScript types
│   │   └── App.tsx          # Main application component
│   ├── package.json         # Frontend dependencies
│   └── ...
├── telegram-bot/             # Telegram bot service
│   ├── bot/                 # Bot implementation
│   ├── handlers/           # Message handlers
│   └── Dockerfile          # Telegram bot Dockerfile
├── nginx/                   # Nginx configuration
│   ├── nginx.conf           # Nginx configuration file
│   └── ssl/                 # SSL certificates
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── docker-compose.yml       # Development docker-compose
├── docker-compose.prod.yml  # Production docker-compose
├── docker-compose.override.yml # Development overrides
├── .env.example             # Environment variables example
├── .gitignore               # Git ignore rules
├── Makefile                 # Development commands
└── README.md                # Project README
```

## Development Environment

### Prerequisites

Install the following tools:

1. **Python 3.9+**
2. **Docker and Docker Compose**
3. **Git**
4. **Node.js 16+** (for frontend development)
5. **PostgreSQL client** (psql)
6. **Redis client** (redis-cli)

### Setting Up Local Development

1. Clone the repository:
```bash
git clone https://github.com/your-org/tender-platform.git
cd tender-platform
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start development services:
```bash
docker-compose up -d
```

4. Install Python dependencies locally (optional but recommended):
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

5. Install frontend dependencies:
```bash
cd ../frontend
npm install
```

### IDE Setup

#### Visual Studio Code

Recommended extensions:
- Python
- Docker
- Prettier - Code formatter
- ESLint
- GitLens
- Thunder Client (for API testing)

#### PyCharm

Configure interpreter to use virtual environment:
1. File → Settings → Project → Python Interpreter
2. Add existing virtual environment or create new one

## Code Standards

### Python Code Style

Follow PEP 8 guidelines with these additional rules:

1. **Line Length**: Maximum 88 characters (Black default)
2. **Imports**: Use isort for import organization
3. **Type Hints**: Use type hints for all functions and classes
4. **Docstrings**: Use Google-style docstrings

#### Formatting Tools

The project uses Black for code formatting and isort for import sorting:

```bash
# Format code
black .
isort .

# Check formatting without changes
black --check .
isort --check-only .
```

#### Pre-commit Hooks

Pre-commit hooks automatically format code before committing:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

### JavaScript/TypeScript Code Style

Follow Airbnb JavaScript style guide with Prettier formatting:

```bash
# Format frontend code
cd frontend
npm run format

# Lint frontend code
npm run lint
```

### SQL Style Guide

1. **Keywords**: Uppercase (SELECT, FROM, WHERE)
2. **Identifiers**: snake_case for columns, plural for tables
3. **Indentation**: 4 spaces for nested queries
4. **Aliases**: Meaningful short aliases (u for users, t for tenders)

## Database Migrations

The project uses Alembic for database migrations.

### Creating Migrations

1. Modify models in `backend/app/models/`
2. Generate migration:
```bash
cd backend
alembic revision --autogenerate -m "Migration description"
```

3. Review generated migration in `backend/alembic/versions/`
4. Apply migration:
```bash
alembic upgrade head
```

### Migration Best Practices

1. **Always** review auto-generated migrations
2. **Never** modify existing migrations - create new ones
3. **Test** migrations on a copy of production data
4. **Document** complex migration logic
5. **Handle** backward compatibility carefully

### Downgrading Migrations

To rollback a migration:
```bash
alembic downgrade -1  # Downgrade one revision
alembic downgrade base  # Downgrade to initial state
```

## Testing

### Test Structure

Tests are organized in `backend/tests/`:

```
tests/
├── conftest.py          # Test fixtures and configuration
├── test_auth.py         # Authentication tests
├── test_tenders.py      # Tender management tests
├── test_monitoring.py   # Monitoring filter tests
├── test_analytics.py    # Analytics tests
├── test_ai.py          # AI integration tests
└── utils/              # Test utilities
```

### Running Tests

```bash
# Run all tests
docker-compose exec backend pytest

# Run specific test file
docker-compose exec backend pytest tests/test_auth.py

# Run tests with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run tests in watch mode (during development)
docker-compose exec backend ptw
```

### Writing Tests

Follow pytest conventions:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db
from app.models.user import User

@pytest.fixture
def client():
    return TestClient(app)

def test_create_user(client, db: Session):
    """Test creating a new user"""
    response = client.post("/api/v1/users/", json={
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    })
    
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

### Test Fixtures

Common test fixtures are defined in `conftest.py`:

- `db`: Database session fixture
- `client`: FastAPI TestClient fixture
- `test_user`: Sample user fixture
- `auth_headers`: Authenticated headers fixture

### Test Coverage

Aim for the following coverage targets:

- **Unit Tests**: 80% coverage
- **Integration Tests**: 90% coverage for API endpoints
- **Edge Cases**: Test error conditions and boundary values

## API Development

### Adding New Endpoints

1. Create schema in `backend/app/schemas/`
2. Create service in `backend/app/services/`
3. Add route in `backend/app/api/v1/`
4. Add tests in `backend/tests/`

### Schema Design

Use Pydantic models for request/response validation:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class TenderCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(None, max_length=5000)
    budget: Decimal = Field(..., gt=0)
    submission_deadline: datetime

class TenderResponse(TenderCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### Service Layer

Keep business logic in service classes:

```python
from sqlalchemy.orm import Session
from app.models.tender import Tender
from app.schemas.tender import TenderCreate

class TenderService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_tender(self, tender_data: TenderCreate) -> Tender:
        tender = Tender(**tender_data.dict())
        self.db.add(tender)
        self.db.commit()
        self.db.refresh(tender)
        return tender
```

### Error Handling

Use HTTPException for API errors:

```python
from fastapi import HTTPException, status

def get_tender(self, tender_id: UUID) -> Tender:
    tender = self.db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tender not found"
        )
    return tender
```

## Frontend Development

### Component Structure

Follow React best practices:

```tsx
// components/TenderCard.tsx
import React from 'react';
import { Tender } from '../types';

interface TenderCardProps {
  tender: Tender;
  onFavorite?: (tenderId: string) => void;
}

const TenderCard: React.FC<TenderCardProps> = ({ tender, onFavorite }) => {
  return (
    <div className="tender-card">
      <h3>{tender.title}</h3>
      <p>{tender.description}</p>
      <div className="tender-meta">
        <span>Budget: {tender.budget}</span>
        <span>Deadline: {tender.submission_deadline}</span>
      </div>
      <button onClick={() => onFavorite?.(tender.id)}>
        {tender.is_favorite ? '★' : '☆'}
      </button>
    </div>
  );
};

export default TenderCard;
```

### State Management

Use React Context for global state and React Query for server state:

```tsx
// contexts/AuthContext.tsx
import React, { createContext, useContext, useState } from 'react';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    // Login logic
    const userData = await api.login(email, password);
    setUser(userData);
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

### API Integration

Use React Query for data fetching:

```tsx
// services/api.ts
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
});

export const useTenders = (filters: any) => {
  return useQuery(['tenders', filters], () => 
    api.get('/tenders', { params: filters }).then(res => res.data)
  );
};

export const useCreateTender = () => {
  const queryClient = useQueryClient();
  return useMutation(
    (tenderData: any) => api.post('/tenders', tenderData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('tenders');
      }
    }
  );
};
```

## Docker Development

### Development Workflow

1. **Build Images**:
```bash
docker-compose build
```

2. **Start Services**:
```bash
docker-compose up -d
```

3. **View Logs**:
```bash
docker-compose logs -f
```

4. **Execute Commands**:
```bash
docker-compose exec backend bash
```

### Customizing Docker Compose

Use override files for development:

```yaml
# docker-compose.override.yml
version: '3.8'

services:
  backend:
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=true
    command: >
      sh -c "pip install -e . &&
             uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
```

### Debugging in Containers

1. **Attach to Running Container**:
```bash
docker attach tender_backend
```

2. **Run Commands in Container**:
```bash
docker-compose exec backend bash
```

3. **Check Container Status**:
```bash
docker-compose ps
```

## Debugging

### Backend Debugging

1. **Add Debug Breakpoints**:
```python
import pdb; pdb.set_trace()
```

2. **Use Logging**:
```python
from app.utils.logger import get_logger

logger = get_logger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

3. **Remote Debugging**:
```bash
# In Docker container
pip install debugpy
python -m debugpy --listen 0.0.0.0:5678 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Database Debugging

1. **Connect to PostgreSQL**:
```bash
docker-compose exec postgres psql -U tender_user -d tender_platform
```

2. **Check Running Queries**:
```sql
SELECT pid, query FROM pg_stat_activity WHERE state = 'active';
```

3. **Explain Query Plans**:
```sql
EXPLAIN ANALYZE SELECT * FROM tenders WHERE budget > 1000000;
```

### Frontend Debugging

1. **Browser DevTools**:
   - Network tab to inspect API requests
   - Console tab for JavaScript errors
   - React DevTools for component inspection

2. **React Developer Tools**:
```bash
# Install React DevTools extension
# Use Components tab to inspect React tree
# Use Profiler tab to analyze performance
```

## Performance Optimization

### Database Optimization

1. **Indexing**:
```python
# In models
class Tender(Base):
    __tablename__ = "tenders"
    
    # Add indexes for frequently queried columns
    __table_args__ = (
        Index('ix_tenders_budget_deadline', 'budget', 'submission_deadline'),
        Index('ix_tenders_customer_name', 'customer_name'),
    )
```

2. **Query Optimization**:
```python
# Use select() with specific columns instead of *
query = select(Tender.id, Tender.title, Tender.budget).where(
    Tender.budget > 1000000
)

# Use joins instead of multiple queries
query = select(Tender, User).join(User, Tender.user_id == User.id)
```

3. **Pagination**:
```python
def get_tenders_paginated(skip: int = 0, limit: int = 20):
    query = select(Tender).offset(skip).limit(limit)
    return db.execute(query).scalars().all()
```

### Caching

Use Redis for caching:

```python
from app.utils.redis_client import redis_client

# Cache expensive computations
async def get_cached_tender_stats(tender_id: str):
    cache_key = f"tender_stats:{tender_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Compute stats
    stats = compute_tender_stats(tender_id)
    
    # Cache for 1 hour
    await redis_client.setex(cache_key, 3600, json.dumps(stats))
    return stats
```

### Async Operations

Use async/await for I/O-bound operations:

```python
import aiohttp
import asyncio

async def fetch_external_data(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

## Security Considerations

### Authentication and Authorization

1. **JWT Tokens**:
```python
from app.core.security import create_access_token

token_data = {
    "sub": str(user.id),
    "email": user.email,
    "role": user.role
}
token = create_access_token(token_data)
```

2. **Role-Based Access Control**:
```python
from fastapi import Depends
from app.api.deps import get_current_user

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
```

### Input Validation

1. **Pydantic Validation**:
```python
class TenderCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    budget: Decimal = Field(..., gt=0, le=1000000000)
    email: EmailStr
```

2. **Sanitization**:
```python
import bleach

def sanitize_html(html_content: str) -> str:
    return bleach.clean(html_content, tags=['p', 'br', 'strong', 'em'])
```

### Secure Headers

Configure security headers in Nginx:

```nginx
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
```

## Deployment

### Production Checklist

Before deploying to production:

1. [ ] Set strong SECRET_KEY
2. [ ] Configure SSL/TLS certificates
3. [ ] Set up monitoring and alerting
4. [ ] Configure backup and recovery
5. [ ] Set up logging aggregation
6. [ ] Configure rate limiting
7. [ ] Set up CDN for static assets
8. [ ] Configure database replication
9. [ ] Set up load balancing
10. [ ] Configure health checks

### Environment Variables

Production environment variables:

```bash
# Security
SECRET_KEY=your_production_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DB_USER=production_user
DB_PASSWORD=strong_password
DB_HOST=production_db_host
DB_PORT=5432

# Email
SMTP_HOST=smtp.production.com
SMTP_PORT=587
SMTP_USER=production_user
SMTP_PASSWORD=strong_password
EMAILS_FROM_EMAIL=noreply@your-domain.com

# AI Providers
OPENAI_API_KEY=your_production_openai_key
ANTHROPIC_API_KEY=your_production_anthropic_key
GOOGLE_GEMINI_API_KEY=your_production_gemini_key

# Telegram
TELEGRAM_BOT_TOKEN=your_production_bot_token
```

### Scaling

Scale horizontally with multiple replicas:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=3 --scale celery_worker=2
```

## Monitoring and Logging

### Health Checks

Implement health check endpoints:

```python
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "healthy",
            "redis": "healthy",
            "api": "healthy"
        }
    }
```

### Logging Configuration

Structured logging with context:

```python
import structlog

logger = structlog.get_logger()

def log_tender_action(action: str, tender_id: str, user_id: str):
    logger.info(
        "tender_action",
        action=action,
        tender_id=tender_id,
        user_id=user_id,
        timestamp=datetime.utcnow().isoformat()
    )
```

### Metrics Collection

Expose Prometheus metrics:

```python
from prometheus_client import Counter, Histogram

TENDERS_PROCESSED = Counter('tenders_processed_total', 'Total tenders processed')
TENDER_PROCESSING_TIME = Histogram('tender_processing_seconds', 'Time spent processing tenders')

@app.post("/tenders/")
async def create_tender(tender_data: TenderCreate):
    start_time = time.time()
    
    # Process tender
    tender = await TenderService.create_tender(tender_data)
    
    # Record metrics
    TENDERS_PROCESSED.inc()
    TENDER_PROCESSING_TIME.observe(time.time() - start_time)
    
    return tender
```

## Contributing

### Git Workflow

1. **Fork the repository**
2. **Create feature branch**:
```bash
git checkout -b feature/new-feature
```

3. **Commit changes**:
```bash
git add .
git commit -m "Add new feature"
```

4. **Push and create PR**:
```bash
git push origin feature/new-feature
```

### Pull Request Guidelines

1. **Title**: Clear, descriptive title
2. **Description**: Explain what changed and why
3. **Tests**: Include tests for new functionality
4. **Documentation**: Update docs when needed
5. **Review**: Request review from maintainers

### Code Review Process

1. **Automated Checks**: CI pipeline runs tests and linting
2. **Manual Review**: Maintainers review code quality
3. **Security Review**: Security-sensitive changes get extra scrutiny
4. **Merge**: Approved PRs are merged to main branch

### Release Process

1. **Version Bump**: Update version in `setup.py` and `package.json`
2. **Changelog**: Update CHANGELOG.md
3. **Tag Release**: Create Git tag
4. **Deploy**: Deploy to production

By following this developer guide, you'll be able to contribute effectively to the Tender Platform and maintain code quality and consistency across the project.