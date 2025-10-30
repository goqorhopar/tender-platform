#!/usr/bin/env python3
"""Verification script for infrastructure setup"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} MISSING: {filepath}")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if Path(dirpath).is_dir():
        print(f"✓ {description}: {dirpath}")
        return True
    else:
        print(f"✗ {description} MISSING: {dirpath}")
        return False

def main():
    """Main verification function"""
    print("=" * 60)
    print("Tender Platform Infrastructure Verification")
    print("=" * 60)
    print()
    
    checks_passed = 0
    checks_total = 0
    
    # Check Docker files
    print("Docker Configuration:")
    checks_total += 1
    if check_file_exists("docker-compose.yml", "Docker Compose config"):
        checks_passed += 1
    
    checks_total += 1
    if check_file_exists("backend/Dockerfile", "Backend Dockerfile"):
        checks_passed += 1
    
    checks_total += 1
    if check_file_exists("backend/.dockerignore", "Backend .dockerignore"):
        checks_passed += 1
    
    print()
    
    # Check configuration files
    print("Configuration Files:")
    checks_total += 1
    if check_file_exists("backend/.env.example", ".env.example"):
        checks_passed += 1
    
    checks_total += 1
    if check_file_exists("backend/.env", ".env"):
        checks_passed += 1
    
    checks_total += 1
    if check_file_exists("backend/app/config.py", "config.py"):
        checks_passed += 1
    
    print()
    
    # Check database setup
    print("Database Configuration:")
    checks_total += 1
    if check_file_exists("backend/app/database.py", "database.py"):
        checks_passed += 1
    
    checks_total += 1
    if check_file_exists("backend/alembic.ini", "alembic.ini"):
        checks_passed += 1
    
    checks_total += 1
    if check_directory_exists("backend/alembic", "alembic directory"):
        checks_passed += 1
    
    print()
    
    # Check Redis setup
    print("Redis Configuration:")
    checks_total += 1
    if check_file_exists("backend/app/utils/redis_client.py", "redis_client.py"):
        checks_passed += 1
    
    print()
    
    # Check logging setup
    print("Logging Configuration:")
    checks_total += 1
    if check_file_exists("backend/app/utils/logger.py", "logger.py"):
        checks_passed += 1
    
    # Check if logs directory will be created
    checks_total += 1
    logs_dir = Path("backend/logs")
    if logs_dir.exists() or "mkdir -p logs" in Path("backend/Dockerfile").read_text():
        print(f"✓ Logs directory setup: configured in Dockerfile")
        checks_passed += 1
    else:
        print(f"✗ Logs directory setup MISSING")
    
    print()
    
    # Check Celery setup
    print("Celery Configuration:")
    checks_total += 1
    if check_file_exists("backend/app/tasks/celery_app.py", "celery_app.py"):
        checks_passed += 1
    
    checks_total += 1
    if check_file_exists("backend/app/tasks/tender_tasks.py", "tender_tasks.py"):
        checks_passed += 1
    
    print()
    
    # Check directory structure
    print("Directory Structure:")
    required_dirs = [
        ("backend/app/api", "API directory"),
        ("backend/app/models", "Models directory"),
        ("backend/app/schemas", "Schemas directory"),
        ("backend/app/services", "Services directory"),
        ("backend/app/tasks", "Tasks directory"),
        ("backend/app/utils", "Utils directory"),
        ("backend/app/integrations", "Integrations directory"),
        ("backend/app/templates", "Templates directory"),
    ]
    
    for dirpath, description in required_dirs:
        checks_total += 1
        if check_directory_exists(dirpath, description):
            checks_passed += 1
    
    print()
    
    # Check main application file
    print("Application Entry Point:")
    checks_total += 1
    if check_file_exists("backend/app/main.py", "main.py"):
        checks_passed += 1
    
    checks_total += 1
    if check_file_exists("backend/requirements.txt", "requirements.txt"):
        checks_passed += 1
    
    print()
    
    # Summary
    print("=" * 60)
    print(f"Verification Results: {checks_passed}/{checks_total} checks passed")
    print("=" * 60)
    
    if checks_passed == checks_total:
        print("✓ All infrastructure components are properly configured!")
        return 0
    else:
        print(f"✗ {checks_total - checks_passed} components need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
