@echo off
REM Health check script for Tender Platform services (Windows)

echo Checking Tender Platform services health...

REM Check if Docker is running
docker version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not running. Please start Docker first.
    exit /b 1
)
echo ✅ Docker is running

REM Check if docker-compose is available
docker-compose version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ docker-compose is not available
    exit /b 1
)
echo ✅ docker-compose is available

REM Check if containers are running
docker-compose ps | findstr "Up" >nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Containers are running
) else (
    echo ⚠️  No containers are currently running
)

REM Check PostgreSQL
docker-compose exec postgres pg_isready >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ PostgreSQL is healthy
) else (
    echo ❌ PostgreSQL is not responding
)

REM Check Redis
docker-compose exec redis redis-cli ping | findstr "PONG" >nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Redis is healthy
) else (
    echo ❌ Redis is not responding
)

REM Check backend API
curl -s http://localhost:8000/api/v1/health | findstr "\"status\":\"healthy\"" >nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Backend API is healthy
) else (
    echo ❌ Backend API is not responding
)

echo Health check completed.