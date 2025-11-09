@echo off
echo ========================================
echo Docker Rebuild Script
echo ========================================
echo.
echo This will:
echo 1. Stop all containers
echo 2. Rebuild images
echo 3. Start services
echo.
echo WARNING: This may take 5-10 minutes
echo.
set /p confirm="Continue? (y/n): "

if /i not "%confirm%"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

cd /d "%~dp0"

echo.
echo [1/4] Stopping containers...
docker-compose down
echo.

echo [2/4] Removing old images...
docker-compose down --rmi local
echo.

echo [3/4] Rebuilding images...
docker-compose build --no-cache
if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)
echo.

echo [4/4] Starting services...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start!
    pause
    exit /b 1
)
echo.

echo ========================================
echo Rebuild Complete!
echo ========================================
echo.
echo Waiting for services to initialize...
timeout /t 20 /nobreak > nul
echo.

docker-compose ps
echo.
echo Services are ready!
echo.
echo Dashboard: http://localhost:8501
echo API Docs:  http://localhost:5000/docs
echo.
pause
