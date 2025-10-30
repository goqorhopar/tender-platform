@echo off
REM Tender Platform Setup Script for Windows

echo Setting up Tender Platform...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist backend\.env (
    echo Creating .env file from example...
    copy backend\.env.example backend\.env
    echo Please edit backend\.env and set your SECRET_KEY before running in production!
)

REM Create logs directory
echo Creating logs directory...
if not exist backend\logs mkdir backend\logs

REM Build and start services
echo Building and starting Docker containers...
docker-compose up -d --build

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check service health
echo Checking service health...
docker-compose ps

echo.
echo Setup complete!
echo.
echo Services status:
docker-compose ps
echo.
echo Access the application:
echo    - Backend API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo    - Health Check: http://localhost:8000/health
echo.
echo View logs:
echo    docker-compose logs -f backend
echo.
echo Stop services:
echo    docker-compose down
