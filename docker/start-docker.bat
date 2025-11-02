@echo off
echo ========================================
echo WeeFarm Predictive Maintenance System
echo Docker Deployment Script
echo ========================================
echo.

echo [1/5] Stopping existing containers...
docker-compose down

echo.
echo [2/5] Building Docker images...
docker-compose build

echo.
echo [3/5] Starting services...
docker-compose up -d

echo.
echo [4/5] Waiting for services to be ready...
timeout /t 10 /nobreak > nul

echo.
echo [5/5] Checking service status...
docker-compose ps

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Services Available:
echo   Dashboard:  http://localhost:8501
echo   API:        http://localhost:5000/docs
echo   Database:   localhost:5432
echo.
echo View logs: docker-compose logs -f
echo Stop all:  docker-compose down
echo ========================================

pause
