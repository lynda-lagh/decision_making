@echo off
echo ========================================
echo Stopping WeeFarm Services
echo ========================================
echo.

docker-compose down

echo.
echo ========================================
echo All services stopped!
echo ========================================

pause
