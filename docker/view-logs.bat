@echo off
echo ========================================
echo Docker Logs Viewer
echo ========================================
echo.
echo Select service to view logs:
echo.
echo 1. All services
echo 2. Dashboard (Streamlit)
echo 3. Backend (FastAPI)
echo 4. Pipeline
echo 5. Database (PostgreSQL)
echo.
set /p choice="Enter choice (1-5): "

cd /d "%~dp0"

if "%choice%"=="1" (
    echo.
    echo Viewing logs for ALL services...
    echo Press Ctrl+C to stop
    echo.
    docker-compose logs -f
) else if "%choice%"=="2" (
    echo.
    echo Viewing logs for DASHBOARD...
    echo Press Ctrl+C to stop
    echo.
    docker-compose logs -f dashboard
) else if "%choice%"=="3" (
    echo.
    echo Viewing logs for BACKEND...
    echo Press Ctrl+C to stop
    echo.
    docker-compose logs -f backend
) else if "%choice%"=="4" (
    echo.
    echo Viewing logs for PIPELINE...
    echo Press Ctrl+C to stop
    echo.
    docker-compose logs -f pipeline
) else if "%choice%"=="5" (
    echo.
    echo Viewing logs for DATABASE...
    echo Press Ctrl+C to stop
    echo.
    docker-compose logs -f db
) else (
    echo.
    echo Invalid choice!
    pause
    exit /b 1
)
