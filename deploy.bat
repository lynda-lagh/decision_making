@echo off
echo ========================================
echo WeeFarm Predictive Maintenance
echo Complete Deployment Script
echo ========================================
echo.

echo [1/6] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed!
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo OK: Docker is installed

echo.
echo [2/6] Building and starting containers...
docker-compose up -d --build

echo.
echo [3/6] Waiting for services to be ready...
timeout /t 15 /nobreak > nul

echo.
echo [4/6] Generating synthetic data...
docker-compose exec -T backend python src/data_generation/generate_all_data.py

echo.
echo [5/6] Creating database tables...
docker-compose exec -T backend python database/create_tables.py

echo.
echo [6/6] Loading data and running pipeline...
docker-compose exec -T backend python database/migrate_data.py
docker-compose exec -T backend python pipeline/pipeline.py

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
echo Opening dashboard in browser...
start http://localhost:8501

echo.
echo Press any key to view logs (Ctrl+C to exit)...
pause > nul
docker-compose logs -f
