@echo off
REM ============================================
REM Grocery Billing Software - Startup Script
REM ============================================
REM This script starts all services on Windows

setlocal enabledelayedexpansion

REM Colors (Windows 10+ only)
set "GREEN=[0;32m"
set "RED=[0;31m"
set "YELLOW=[1;33m"
set "BLUE=[0;34m"
set "NC=[0m"

REM ============================================
REM 1. VERIFY PREREQUISITES
REM ============================================
echo.
echo =========================================
echo Checking Prerequisites
echo =========================================
echo.

REM Check Java
java -version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Java is not installed
    echo Download from: https://www.oracle.com/java/technologies/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('java -version 2^>^&1 ^| find "version"') do set JAVA_VERSION=%%i
echo [OK] Java %JAVA_VERSION% is installed

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% is installed

REM Check Maven
mvn --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Maven is not installed
    echo Download from: https://maven.apache.org/download.cgi
    pause
    exit /b 1
)
echo [OK] Maven is installed

REM Check MySQL
mysql --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] MySQL is not installed
    echo Download from: https://dev.mysql.com/downloads/mysql/
    pause
    exit /b 1
)
echo [OK] MySQL is installed

REM ============================================
REM 2. SETUP MySQL
REM ============================================
echo.
echo =========================================
echo Setting up MySQL Database
echo =========================================
echo.

REM Start MySQL service
echo [INFO] Starting MySQL service...
net start MySQL80 >nul 2>&1
if errorlevel 1 (
    echo [WARNING] MySQL service may already be running
) else (
    echo [OK] MySQL service started
)

REM Wait for MySQL to start
timeout /t 2 /nobreak >nul

REM Check if database exists
mysql -u billing_user -psecure_password_123 -e "USE grocery_billing" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Creating database and user...
    
    mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS grocery_billing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" >nul 2>&1
    mysql -u root -p -e "CREATE USER IF NOT EXISTS 'billing_user'@'localhost' IDENTIFIED BY 'secure_password_123';" >nul 2>&1
    mysql -u root -p -e "GRANT ALL PRIVILEGES ON grocery_billing.* TO 'billing_user'@'localhost';" >nul 2>&1
    mysql -u root -p -e "FLUSH PRIVILEGES;" >nul 2>&1
    
    if errorlevel 1 (
        echo [ERROR] Could not create database
        echo Please run MySQL setup manually
        pause
        exit /b 1
    )
    
    echo [OK] Database created
) else (
    echo [OK] Database already exists
)

REM ============================================
REM 3. BUILD BACKEND
REM ============================================
echo.
echo =========================================
echo Building Java Spring Boot Backend
echo =========================================
echo.

if not exist "backend" (
    echo [ERROR] Backend directory not found!
    pause
    exit /b 1
)

cd backend

if not exist "pom.xml" (
    echo [ERROR] pom.xml not found in backend directory
    cd ..
    pause
    exit /b 1
)

echo [INFO] Running Maven build (this may take 2-3 minutes)...
call mvn clean package -DskipTests -q
if errorlevel 1 (
    echo [ERROR] Maven build failed
    echo Try running: mvn clean package -DskipTests
    cd ..
    pause
    exit /b 1
)

if not exist "target\grocery-billing-system-1.0.0.jar" (
    echo [ERROR] JAR file not created
    cd ..
    pause
    exit /b 1
)

echo [OK] Backend built successfully

cd ..

REM ============================================
REM 4. SETUP FRONTEND
REM ============================================
echo.
echo =========================================
echo Setting up Django Frontend
echo =========================================
echo.

if not exist "frontend" (
    echo [ERROR] Frontend directory not found!
    pause
    exit /b 1
)

cd frontend

if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
)

echo [INFO] Installing Python dependencies...
call venv\Scripts\pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    cd ..
    pause
    exit /b 1
)

echo [OK] Dependencies installed

cd ..

REM ============================================
REM 5. START SERVICES
REM ============================================
echo.
echo =========================================
echo Starting Services
echo =========================================
echo.

REM Create batch files to start services
echo Creating service startup files...

REM Backend startup file
(
    echo @echo off
    echo cd /d "%cd%\backend"
    echo java -jar target/grocery-billing-system-1.0.0.jar
    echo pause
) > start_backend.bat

REM Frontend startup file
(
    echo @echo off
    echo cd /d "%cd%\frontend"
    echo call venv\Scripts\activate.bat
    echo python manage.py runserver 0.0.0.0:8000
    echo pause
) > start_frontend.bat

REM Start services in new windows
echo [INFO] Starting Backend on port 8080...
start "Grocery Billing - Backend (Java)" cmd /k call start_backend.bat

timeout /t 3 /nobreak >nul

echo [INFO] Starting Frontend on port 8000...
start "Grocery Billing - Frontend (Django)" cmd /k call start_frontend.bat

REM ============================================
REM 6. ACCESS APPLICATION
REM ============================================
echo.
echo =========================================
echo ^! All Services Started!
echo =========================================
echo.

echo [OK] Backend: http://localhost:8080
echo [OK] Frontend: http://localhost:8000
echo [OK] Database: localhost:3306
echo.

echo [INFO] Credentials:
echo   Username: admin
echo   Password: admin123
echo.

REM Open in browser
echo [INFO] Opening application in browser...
timeout /t 2 /nobreak >nul
start http://localhost:8000

REM Keep console open
echo.
echo [INFO] Services are running in separate windows
echo [WARNING] You can close those windows to stop the services
echo.
pause

REM Cleanup temp files
del start_backend.bat 2>nul
del start_frontend.bat 2>nul

endlocal
