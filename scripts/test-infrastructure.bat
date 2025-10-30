@echo off
REM Infrastructure testing script for Tender Platform (Windows)

echo ==========================================
echo Tender Platform Infrastructure Test
echo ==========================================
echo.

REM Check Docker
echo Checking Docker...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker is installed
    docker --version
) else (
    echo [ERROR] Docker is not installed
    exit /b 1
)
echo.

REM Check Docker Compose
echo Checking Docker Compose...
docker compose version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Docker Compose is installed
    docker compose version
) else (
    echo [ERROR] Docker Compose is not installed
    exit /b 1
)
echo.

REM Validate docker-compose.yml
echo Validating docker-compose.yml...
docker compose config >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] docker-compose.yml is valid
) else (
    echo [ERROR] docker-compose.yml has errors
    exit /b 1
)
echo.

REM Check if services are running
echo Checking running services...
docker compose ps
echo.

REM Start services
echo Starting services...
echo This may take a few minutes on first run...
docker compose up -d

REM Wait for services to be healthy
echo.
echo Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

REM Check PostgreSQL
echo.
echo Testing PostgreSQL connection...
docker compose exec -T postgres pg_isready -U tender_user -d tender_platform >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] PostgreSQL is healthy
) else (
    echo [WARNING] PostgreSQL is not responding
)

REM Check Redis
echo Testing Redis connection...
docker compose exec -T redis redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Redis is healthy
) else (
    echo [WARNING] Redis is not responding
)

REM Check Backend API
echo Testing Backend API...
timeout /t 5 /nobreak >nul
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend API is responding
    echo Response:
    curl -s http://localhost:8000/health
) else (
    echo [WARNING] Backend API is not responding yet
)

REM Check API root endpoint
echo.
echo Testing API root endpoint...
curl -s http://localhost:8000/ >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] API root endpoint is responding
    echo Response:
    curl -s http://localhost:8000/
) else (
    echo [WARNING] API root endpoint is not responding yet
)

REM Show service status
echo.
echo ==========================================
echo Service Status:
echo ==========================================
docker compose ps

REM Show logs summary
echo.
echo ==========================================
echo Recent Logs (last 20 lines):
echo ==========================================
docker compose logs --tail=20

echo.
echo ==========================================
echo Infrastructure Test Complete!
echo ==========================================
echo.
echo Access points:
echo   - Backend API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo   - Health Check: http://localhost:8000/health
echo.
echo To view logs: docker compose logs -f
echo To stop services: docker compose down
echo.

pause
