@echo off
setlocal

echo ========================================
echo Grocery Billing Backend - Docker Run
echo ========================================
echo.

set "IMAGE_NAME=grocery-billing-api"
set "CONTAINER_NAME=grocery-billing-api"
set "HOST_PORT=8080"
set "CONTAINER_PORT=8080"

where docker >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker CLI is not installed or not in PATH.
    echo Install Docker Desktop and try again.
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker daemon is not running.
    echo Start Docker Desktop, wait until it is ready, then run this script again.
    pause
    exit /b 1
)

echo [INFO] Building Docker image...
docker build --no-cache -t %IMAGE_NAME% .
if errorlevel 1 (
    echo [ERROR] Docker build failed.
    pause
    exit /b 1
)

echo [INFO] Stopping old container (if running)...
docker stop %CONTAINER_NAME% >nul 2>&1

echo [INFO] Removing old container (if exists)...
docker rm %CONTAINER_NAME% >nul 2>&1

echo [INFO] Starting new container...
docker run -d -p %HOST_PORT%:%CONTAINER_PORT% --name %CONTAINER_NAME% %IMAGE_NAME%
if errorlevel 1 (
    echo [ERROR] Failed to start container.
    pause
    exit /b 1
)

echo.
echo [OK] Container started successfully.
echo Backend URL: http://localhost:%HOST_PORT%/
echo.
echo [INFO] Current container status:
docker ps --filter "name=%CONTAINER_NAME%"

echo.
echo [INFO] Showing live logs. Press Ctrl+C to stop logs view.
docker logs -f %CONTAINER_NAME%

endlocal
