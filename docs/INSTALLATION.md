# Installation Guide

This guide provides detailed instructions for installing and configuring the Tender Platform.

## System Requirements

### Minimum Requirements

- CPU: 2 cores
- RAM: 8 GB
- Disk Space: 20 GB free space
- OS: Linux, macOS, or Windows 10+
- Docker: 20.10+
- Docker Compose: 1.29+

### Recommended Requirements

- CPU: 4 cores
- RAM: 16 GB
- Disk Space: 50 GB free space
- SSD storage for better performance

## Prerequisites

Before installing the Tender Platform, ensure you have the following installed:

1. **Git** - For cloning the repository
2. **Docker** - Containerization platform
3. **Docker Compose** - Multi-container orchestration

### Installing Docker

#### Ubuntu/Debian

```bash
# Update package index
sudo apt update

# Install prerequisites
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index again
sudo apt update

# Install Docker Engine
sudo apt install docker-ce docker-ce-cli containerd.io

# Add your user to the docker group
sudo usermod -aG docker $USER

# Log out and back in for group membership to take effect
```

#### CentOS/RHEL

```bash
# Install prerequisites
sudo yum install -y yum-utils

# Set up the repository
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker Engine
sudo yum install docker-ce docker-ce-cli containerd.io

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to the docker group
sudo usermod -aG docker $USER
```

#### Windows

Download Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

#### macOS

Download Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

## Installation Steps

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-org/tender-platform.git

# Navigate to the project directory
cd tender-platform
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```bash
nano .env
```

### 3. Configure Essential Settings

At minimum, configure the following essential settings in your `.env` file:

```bash
# Database configuration
DB_USER=tender_user
DB_PASSWORD=your_secure_password  # Change this!

# Secret key for JWT tokens (generate a secure random key)
SECRET_KEY=your_very_secret_key_here_change_this  # Generate with: openssl rand -hex 32

# First superuser account
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=secure_password  # Change this!
```

### 4. Start the Platform

Start all services using Docker Compose:

```bash
# Start services in detached mode
docker-compose up -d

# View logs to monitor startup
docker-compose logs -f
```

### 5. Initialize the Database

The platform will automatically initialize the database on first startup. If you need to manually initialize or reset the database:

```bash
# Run database initialization
docker-compose exec backend python -c "from app.database import init_db; init_db()"

# Run database migrations
docker-compose exec backend alembic upgrade head
```

### 6. Create Superuser Account

If you didn't configure the superuser in the `.env` file, create one manually:

```bash
docker-compose exec backend python -c "
import asyncio
from app.models.user import User
from app.core.security import get_password_hash
from app.database import get_db

async def create_superuser():
    db = next(get_db())
    user = User(
        email='admin@example.com',
        hashed_password=get_password_hash('secure_password'),
        full_name='Admin User',
        role='admin',
        is_active=True,
        is_email_verified=True
    )
    db.add(user)
    db.commit()
    print('Superuser created successfully')

asyncio.run(create_superuser())
"
```

### 7. Access the Platform

Once all services are running and healthy:

- **API Documentation**: http://localhost:8000/docs
- **API Base URL**: http://localhost:8000/api/v1
- **Frontend** (when available): http://localhost:3000

## Configuration Options

### Database Configuration

The platform uses PostgreSQL as its primary database. You can configure the database connection using environment variables:

```bash
# Database connection settings
DB_HOST=postgres
DB_PORT=5432
DB_USER=tender_user
DB_PASSWORD=your_secure_password
DB_NAME=tender_platform
```

For external databases, update these values to point to your database server.

### Redis Configuration

Redis is used for caching and as a message broker for Celery:

```bash
# Redis connection settings
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

### AI Integration

To enable AI features, configure API keys for the AI providers you want to use:

```bash
# AI Provider API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key
```

### Email Configuration

Configure SMTP settings for email notifications:

```bash
# Email configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAILS_FROM_EMAIL=noreply@your-domain.com
```

### Telegram Bot Configuration

To enable Telegram bot functionality:

```bash
# Telegram bot settings
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

### File Storage Configuration

Configure file storage settings:

```bash
# File storage settings
S3_BUCKET=your-s3-bucket-name
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
STORAGE_TYPE=local  # or s3
UPLOAD_DIR=/app/uploads
```

## Production Configuration

For production deployments, use the production docker-compose file:

```bash
# Start with production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### SSL/TLS Configuration

For HTTPS, configure SSL certificates in the Nginx configuration:

1. Place SSL certificates in `nginx/ssl/` directory
2. Update `nginx/nginx.conf` with certificate paths
3. Ensure certificates have proper permissions

### Environment Variables for Production

Create a separate `.env.prod` file for production settings:

```bash
# Copy production env file
cp .env.example .env.prod

# Edit production settings
nano .env.prod
```

Start with production environment:

```bash
# Start with production environment
docker-compose --env-file .env.prod up -d
```

## Verification

After installation, verify that all services are running correctly:

### Check Service Status

```bash
# Check running containers
docker-compose ps

# Expected output should show all services as "Up"
```

### Check Health Endpoints

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Check database connectivity
docker-compose exec postgres pg_isready

# Check Redis connectivity
docker-compose exec redis redis-cli ping
```

### Test Authentication

Test the authentication system with the superuser account:

```bash
# Login with superuser credentials
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "secure_password"}'
```

## Troubleshooting

### Common Issues

#### Services Not Starting

Check logs for specific errors:

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs postgres
```

#### Database Connection Issues

Ensure database credentials are correct in `.env` file and that the database container is running:

```bash
# Check database container
docker-compose ps | grep postgres

# Check database logs
docker-compose logs postgres
```

#### Permission Errors

On Linux, ensure your user is in the docker group:

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in for changes to take effect
```

#### Port Conflicts

If ports are already in use, change them in `docker-compose.yml`:

```yaml
services:
  postgres:
    ports:
      - "5433:5432"  # Changed from 5432:5432
```

### Need Help?

If you encounter issues not covered in this guide:

1. Check the [GitHub Issues](https://github.com/your-org/tender-platform/issues)
2. Join our [Discord Community](https://discord.gg/your-discord-invite)
3. Contact support: support@your-domain.com

## Next Steps

After successful installation, consider:

1. [Configuring AI providers](#ai-integration) for advanced features
2. [Setting up email notifications](#email-configuration)
3. [Enabling Telegram bot](#telegram-bot-configuration)
4. [Configuring SSL/TLS for production](#ssl-tls-configuration)
5. [Setting up monitoring and alerts](#monitoring)

Refer to the [User Guide](USER_GUIDE.md) for instructions on using the platform.