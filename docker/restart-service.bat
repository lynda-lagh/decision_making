@echo off
echo ========================================
echo Docker Service Restart
echo ========================================
echo.
echo Select service to restart:
echo.
echo 1. Dashboard (Streamlit)
echo 2. Backend (FastAPI)
echo 3. Pipeline
echo 4. Database (PostgreSQL)
echo 5. All services
echo.
set /p choice="Enter choice (1-5): "

cd /d "%~dp0"

if "%choice%"=="1" (
    echo.
    echo Restarting DASHBOARD...
    docker-compose restart dashboard
    echo [OK] Dashboard restarted
) else if "%choice%"=="2" (
    echo.
    echo Restarting BACKEND...
    docker-compose restart backend
    echo [OK] Backend restarted
) else if "%choice%"=="3" (
    echo.
    echo Restarting PIPELINE...
    docker-compose restart pipeline
    echo [OK] Pipeline restarted
) else if "%choice%"=="4" (
    echo.
    echo Restarting DATABASE...
    docker-compose restart db
    echo [OK] Database restarted
) else if "%choice%"=="5" (
    echo.
    echo Restarting ALL SERVICES...
    docker-compose restart
    echo [OK] All services restarted
) else (
    echo.
    echo Invalid choice!
    pause
    exit /b 1
)

echo.
echo Service status:
docker-compose ps
echo.
pause
