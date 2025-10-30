# Tender Platform Documentation

Welcome to the Tender Platform documentation. This guide will help you understand, install, configure, and use the Tender Platform for managing government and commercial tenders.

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Deployment](#deployment)
6. [API Documentation](#api-documentation)
7. [Features Guide](#features-guide)
8. [Development](#development)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)

## Overview

The Tender Platform is a comprehensive solution for managing tenders, including:

- Automated monitoring of government and commercial electronic trading platforms (ETPs)
- Advanced analytics and forecasting
- AI-powered document analysis and generation
- Risk management and legal compliance checking
- Supplier management and evaluation
- Collaboration tools for teams
- Calendar and planning features
- Comprehensive reporting and dashboards

### Key Features

- **Tender Monitoring**: Real-time monitoring of EIS and commercial ETPs
- **AI Integration**: Advanced AI for document analysis and application generation
- **Analytics**: Comprehensive analytics with forecasting capabilities
- **Risk Management**: Automated risk identification and mitigation
- **Collaboration**: Team collaboration tools with commenting and task management
- **Legal Compliance**: Automated legal compliance checking
- **Supplier Management**: Supplier registry with performance evaluation
- **Document Management**: Template-based document generation

## System Architecture

The Tender Platform follows a microservices architecture with the following components:

### Backend Services

1. **API Service** - FastAPI-based REST API
2. **Database** - PostgreSQL with TimescaleDB extensions
3. **Cache** - Redis for caching and session management
4. **Message Queue** - Redis with Celery for background tasks
5. **AI Services** - Integration with OpenAI, Anthropic, and Google Gemini
6. **File Storage** - Local storage or S3-compatible storage
7. **Notification Service** - Email, SMS, and Telegram notifications

### Frontend

1. **Web Application** - React-based SPA with responsive design
2. **Mobile Application** - React Native mobile app (optional)

### External Integrations

1. **Government Systems** - Integration with EIS (zakupki.gov.ru)
2. **Commercial ETPs** - Integration with major Russian ETPs (Sberbank-AST, RTS-Tender, B2B-Center)
3. **AI Providers** - Integration with OpenAI, Anthropic, and Google Gemini
4. **Accounting Systems** - Optional integration with 1C, Moysklad, Bitrix24

## Installation

### Prerequisites

- Docker and Docker Compose
- Git
- At least 8GB RAM and 20GB free disk space
- Internet connection for downloading dependencies

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/your-org/tender-platform.git
cd tender-platform
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env file with your configuration
```

3. Start the platform:
```bash
docker-compose up -d
```

4. Access the platform at http://localhost:8000

### Detailed Installation

#### Docker Installation

For Ubuntu/Debian:
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
# Logout and login again
```

For other operating systems, refer to the official Docker documentation.

#### Repository Setup

```bash
git clone https://github.com/your-org/tender-platform.git
cd tender-platform
```

#### Environment Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
```bash
# Database configuration
DB_USER=tender_user
DB_PASSWORD=your_secure_password
DB_NAME=tender_platform

# Secret key for JWT tokens
SECRET_KEY=your_very_secret_key_here_change_this

# AI API keys (optional but recommended)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key

# Email configuration
SMTP_HOST=smtp.your-email-provider.com
SMTP_PORT=587
SMTP_USER=your_email@domain.com
SMTP_PASSWORD=your_email_password
EMAILS_FROM_EMAIL=noreply@your-domain.com

# Telegram bot token (if using Telegram integration)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# File storage configuration
S3_BUCKET=your-s3-bucket-name
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DB_USER` | Database username | Yes |
| `DB_PASSWORD` | Database password | Yes |
| `SECRET_KEY` | JWT secret key | Yes |
| `OPENAI_API_KEY` | OpenAI API key | No (but recommended) |
| `ANTHROPIC_API_KEY` | Anthropic API key | No (but recommended) |
| `GOOGLE_GEMINI_API_KEY` | Google Gemini API key | No (but recommended) |
| `SMTP_HOST` | SMTP server hostname | No |
| `SMTP_PORT` | SMTP server port | No |
| `SMTP_USER` | SMTP username | No |
| `SMTP_PASSWORD` | SMTP password | No |
| `EMAILS_FROM_EMAIL` | Sender email address | No |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | No |

### Database Configuration

The platform uses PostgreSQL as its primary database. You can configure the database connection using the following environment variables:

- `DB_HOST` - Database host (default: postgres)
- `DB_PORT` - Database port (default: 5432)
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `DB_NAME` - Database name

### AI Configuration

The platform supports integration with multiple AI providers:

1. **OpenAI** - For GPT models
2. **Anthropic** - For Claude models
3. **Google Gemini** - For Gemini models

To enable AI features, you need to obtain API keys from the respective providers and configure them in the environment variables.

### Email Configuration

For email notifications, configure the following environment variables:

- `SMTP_HOST` - SMTP server hostname
- `SMTP_PORT` - SMTP server port (usually 587 for TLS)
- `SMTP_USER` - SMTP username
- `SMTP_PASSWORD` - SMTP password
- `EMAILS_FROM_EMAIL` - Sender email address

## Deployment

### Production Deployment

For production deployment, use the production docker-compose file:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

For Kubernetes deployment, use the provided Helm charts:

```bash
helm install tender-platform ./helm/tender-platform
```

### Scaling

The platform can be scaled horizontally by increasing the number of replicas for stateless services:

```bash
docker-compose up -d --scale backend=3 --scale celery_worker=2
```

### Monitoring

The platform includes built-in monitoring capabilities:

- Health checks at `/api/v1/health`
- Prometheus metrics at `/metrics`
- Logging to centralized logging solutions

### Backup and Recovery

Regular backups are essential for production deployments. The platform includes built-in backup functionality:

```bash
# Create a backup
docker-compose exec backend python -m app.scripts.backup create

# Restore from backup
docker-compose exec backend python -m app.scripts.backup restore <backup_file>
```

## API Documentation

The Tender Platform provides a comprehensive REST API with automatic documentation available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Authentication

Most API endpoints require authentication using JWT tokens. To obtain a token:

```bash
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password"
}
```

Include the token in subsequent requests:

```http
Authorization: Bearer <your_jwt_token>
```

### Core API Endpoints

#### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - User logout

#### Tenders
- `GET /api/v1/tenders` - List tenders
- `GET /api/v1/tenders/{id}` - Get tender details
- `POST /api/v1/tenders` - Create tender
- `PUT /api/v1/tenders/{id}` - Update tender
- `DELETE /api/v1/tenders/{id}` - Delete tender

#### Monitoring
- `GET /api/v1/monitoring` - List monitoring filters
- `POST /api/v1/monitoring` - Create monitoring filter
- `PUT /api/v1/monitoring/{id}` - Update monitoring filter
- `DELETE /api/v1/monitoring/{id}` - Delete monitoring filter

#### Analytics
- `GET /api/v1/analytics/price-statistics` - Get price statistics
- `POST /api/v1/analytics/win-probability` - Calculate win probability
- `GET /api/v1/analytics/reports` - List analytics reports

#### AI Integration
- `POST /api/v1/ai/analyze-tender` - Analyze tender
- `POST /api/v1/ai/generate-application` - Generate application
- `POST /api/v1/ai/generate-tz` - Generate technical specification

For detailed API documentation, visit http://localhost:8000/docs when the platform is running.

## Features Guide

### Tender Monitoring

The platform automatically monitors government and commercial ETPs for new tenders that match your criteria. You can set up monitoring filters based on:

- Keywords in tender titles and descriptions
- OKPD2 codes
- Regions
- Budget ranges
- Tender types
- Customer INNs

### AI-Powered Analysis

The platform uses AI to analyze tender documentation and generate insights:

- Risk identification
- Competitive analysis
- Document generation
- Price optimization

### Analytics and Reporting

Comprehensive analytics features include:

- Price statistics and trends
- Win probability forecasting
- Competitor analysis
- Performance reporting
- Custom report generation

### Risk Management

Automated risk identification and management:

- Legal compliance checking
- Financial risk assessment
- Operational risk identification
- Risk mitigation strategies

### Collaboration Tools

Team collaboration features:

- Commenting system
- Task management
- Calendar integration
- Notification system

### Supplier Management

Supplier registry with performance evaluation:

- Supplier profiles
- Performance ratings
- Contract history
- Reliability scoring

## Development

### Project Structure

```
tender-platform/
├── backend/                 # Backend API (FastAPI)
│   ├── app/                 # Application code
│   │   ├── api/             # API endpoints
│   │   ├── models/          # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── tasks/           # Celery tasks
│   │   ├── utils/           # Utility functions
│   │   └── main.py          # Application entry point
│   ├── tests/               # Unit and integration tests
│   ├── alembic/             # Database migrations
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Backend Dockerfile
├── frontend/                # Frontend application (React)
├── telegram-bot/            # Telegram bot service
├── nginx/                   # Nginx configuration
├── docker-compose.yml       # Development docker-compose
├── docker-compose.prod.yml  # Production docker-compose
├── .env.example             # Environment variables example
└── README.md                # This file
```

### Setting Up Development Environment

1. Install Python 3.9+
2. Install Docker and Docker Compose
3. Clone the repository
4. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
5. Install dependencies:
```bash
pip install -r backend/requirements.txt
```
6. Set up pre-commit hooks:
```bash
pre-commit install
```

### Running Tests

To run tests:
```bash
# Run all tests
docker-compose exec backend pytest

# Run specific test file
docker-compose exec backend pytest tests/test_auth.py

# Run tests with coverage
docker-compose exec backend pytest --cov=app
```

### Code Style

The project follows PEP 8 style guidelines and uses Black for code formatting. Pre-commit hooks are configured to automatically format code before committing.

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run tests to ensure nothing is broken
6. Commit your changes
7. Push to your fork
8. Create a pull request

## Troubleshooting

### Common Issues

#### Database Connection Failed

Ensure the database container is running:
```bash
docker-compose ps
docker-compose logs postgres
```

Check database credentials in `.env` file.

#### AI Integration Not Working

Verify API keys are correctly configured in `.env` file and that the AI provider is accessible from your network.

#### Email Notifications Not Sending

Check SMTP configuration in `.env` file and ensure your email provider allows SMTP access.

### Logs

View service logs:
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f
```

### Health Checks

Check service health:
```bash
# Run health check script
bash scripts/health-check.sh

# Manual health checks
curl http://localhost:8000/api/v1/health
docker-compose exec postgres pg_isready
docker-compose exec redis redis-cli ping
```

## Contributing

We welcome contributions to the Tender Platform! Here's how you can help:

### Ways to Contribute

1. **Bug Reports** - Report bugs using the GitHub issue tracker
2. **Feature Requests** - Suggest new features
3. **Code Contributions** - Submit pull requests with bug fixes or new features
4. **Documentation** - Improve documentation
5. **Testing** - Help test new features and report issues

### Development Guidelines

1. Follow the existing code style and conventions
2. Write tests for new functionality
3. Keep pull requests focused on a single feature or bug fix
4. Update documentation when making changes
5. Ensure all tests pass before submitting a pull request

### Code Review Process

All pull requests are reviewed by maintainers before merging. Reviews focus on:

- Code quality and maintainability
- Test coverage
- Documentation updates
- Security considerations
- Performance implications

Thank you for considering contributing to the Tender Platform!
