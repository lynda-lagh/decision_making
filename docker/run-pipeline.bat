@echo off
echo ========================================
echo Run Pipeline Manually
echo ========================================
echo.
echo This will run the integrated pipeline once.
echo.
set /p confirm="Continue? (y/n): "

if /i not "%confirm%"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

cd /d "%~dp0"

echo.
echo Starting pipeline...
docker-compose run --rm pipeline

echo.
echo ========================================
echo Pipeline execution completed!
echo ========================================
echo.
pause
