@echo off
setlocal enabledelayedexpansion

echo ========================================
echo WeeFarm Predictive Maintenance System
echo Docker Deployment Script v2.0
echo ========================================
echo.

REM Check if Docker is running
echo [CHECK] Verifying Docker is running...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo.
    echo Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)
echo [OK] Docker is running
echo.

REM Navigate to docker directory
cd /d "%~dp0"
echo [INFO] Working directory: %CD%
echo.

REM Stop existing containers
echo [1/6] Stopping existing containers...
docker-compose down
if errorlevel 1 (
    echo [WARNING] Error stopping containers, continuing...
)
echo.

REM Clean up old images (optional)
echo [2/6] Cleaning up old images...
docker image prune -f
echo.

REM Build Docker images
echo [3/6] Building Docker images...
echo This may take 5-10 minutes on first run...
docker-compose build --no-cache
if errorlevel 1 (
    echo [ERROR] Build failed!
    echo.
    echo Check the error messages above.
    pause
    exit /b 1
)
echo [OK] Build completed successfully
echo.

REM Start services
echo [4/6] Starting services...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services!
    echo.
    pause
    exit /b 1
)
echo [OK] Services started
echo.

REM Wait for services to be ready
echo [5/6] Waiting for services to initialize...
echo This may take 30-60 seconds...
timeout /t 30 /nobreak > nul

REM Check service health
echo.
echo [6/6] Checking service health...
docker-compose ps
echo.

REM Test database connection
echo [TEST] Testing database connection...
docker exec weefarm_db pg_isready -U postgres >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Database not ready yet, may need more time
) else (
    echo [OK] Database is ready
)
echo.

REM Display service URLs
echo ========================================
echo Deployment Complete! 🎉
echo ========================================
echo.
echo 📊 Services Available:
echo.
echo   Dashboard:  http://localhost:8501
echo              (Streamlit UI - 7 pages)
echo.
echo   API Docs:   http://localhost:5000/docs
echo              (FastAPI Interactive Documentation)
echo.
echo   Database:   localhost:5432
echo              User: postgres
echo              Password: 0000
echo              Database: weefarm_db
echo.
echo ========================================
echo 🔧 Useful Commands:
echo ========================================
echo.
echo   View logs (all):      docker-compose logs -f
echo   View logs (specific): docker-compose logs -f dashboard
echo   Stop all services:    docker-compose down
echo   Restart service:      docker-compose restart dashboard
echo   Service status:       docker-compose ps
echo.
echo ========================================
echo 📝 Next Steps:
echo ========================================
echo.
echo 1. Open http://localhost:8501 in your browser
echo 2. Navigate through the 7 dashboard pages
echo 3. Check the API at http://localhost:5000/docs
echo 4. Monitor logs: docker-compose logs -f
echo.
echo ========================================

REM Ask if user wants to open browser
echo.
set /p OPEN_BROWSER="Open dashboard in browser? (y/n): "
if /i "%OPEN_BROWSER%"=="y" (
    start http://localhost:8501
    start http://localhost:5000/docs
    echo.
    echo [OK] Browser opened
)

echo.
echo Press any key to exit...
pause >nul
