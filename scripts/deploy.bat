@echo off
REM Deployment script for Tender Platform (Windows)

echo 🚀 Starting Tender Platform deployment...

REM Check if we're in the right directory
if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml not found. Please run this script from the project root directory.
    exit /b 1
)

echo ✅ Found project root directory

REM Load environment variables
if exist ".env" (
    echo ✅ Loading environment variables from .env file
    for /f "tokens=*" %%i in (.env) do set %%i
) else (
    echo ⚠️  No .env file found. Using default values or environment variables.
)

REM Check required environment variables
set MISSING_VARS=
if "%DB_USER%"=="" set MISSING_VARS=%MISSING_VARS% DB_USER
if "%DB_PASSWORD%"=="" set MISSING_VARS=%MISSING_VARS% DB_PASSWORD
if "%SECRET_KEY%"=="" set MISSING_VARS=%MISSING_VARS% SECRET_KEY

if defined MISSING_VARS (
    echo ❌ Missing required environment variables:%MISSING_VARS%
    echo Please set these variables in your .env file or environment.
    exit /b 1
)

echo ✅ All required environment variables are set

REM Pull latest images
echo 📥 Pulling latest Docker images...
docker-compose pull

REM Build images
echo 🏗️  Building Docker images...
docker-compose build

REM Stop any running containers
echo ⏹️  Stopping any running containers...
docker-compose down

REM Start services
echo 🚀 Starting services...
docker-compose up -d

REM Wait for services to start
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Run database migrations
echo 🔧 Running database migrations...
docker-compose exec backend alembic upgrade head

REM Run health checks
echo 🩺 Running health checks...
echo ⚠️  Health check script not implemented for Windows yet

echo 🎉 Deployment completed successfully!
echo.
echo 📝 Next steps:
echo    1. Access the application at http://localhost:8000
echo    2. View logs with: docker-compose logs -f
echo    3. View running services with: docker-compose ps
echo.
echo 🔐 Default credentials (if created):
echo    Email: admin@example.com
echo    Password: Please check your .env file