# Infrastructure Setup Guide

## Overview

This document describes the infrastructure setup for the Tender Platform, including Docker configuration, database setup, Redis configuration, and logging system.

## Architecture Components

### Services

1. **PostgreSQL 15** - Primary database
   - Port: 5432
   - Database: tender_platform
   - User: tender_user
   - Health checks enabled

2. **Redis 7** - Cache and message broker
   - Port: 6379
   - Used for caching and Celery task queue
   - Health checks enabled

3. **Backend (FastAPI)** - API server
   - Port: 8000
   - Python 3.11+
   - Auto-reload in development mode
   - Multi