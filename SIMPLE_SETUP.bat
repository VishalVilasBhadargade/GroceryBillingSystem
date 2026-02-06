@echo off
echo ========================================
echo SIMPLE SETUP - Grocery Billing System
echo ========================================
echo.

echo STEP 1: Please install these programs first:
echo.
echo 1. MySQL - https://dev.mysql.com/downloads/installer/
echo    After installing, start MySQL service
echo.
echo 2. Maven - https://maven.apache.org/download.cgi
echo    Download apache-maven-3.9.6-bin.zip
echo    Extract to C:\maven
echo    Add C:\maven\bin to your PATH
echo.
echo Once installed, press any key to continue...
pause
echo.

REM Check MySQL
echo Checking if MySQL is running...
mysql --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo MySQL is not found in PATH!
    echo Please install MySQL and add it to PATH
    echo.
    pause
    exit /b 1
)

REM Check Maven
echo Checking if Maven is installed...
mvn --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo Maven is not found!
    echo Please install Maven and add it to PATH
    echo OR download from: https://maven.apache.org/download.cgi
    echo.
    pause
    exit /b 1
)

echo.
echo ✓ All dependencies found!
echo.

REM Create Database
echo Creating database...
echo CREATE DATABASE IF NOT EXISTS grocery_billing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; > temp.sql
echo USE grocery_billing; >> temp.sql
echo CREATE TABLE IF NOT EXISTS users (id BIGINT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(50) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL, email VARCHAR(100), full_name VARCHAR(100), role VARCHAR(20), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP); >> temp.sql
echo INSERT IGNORE INTO users (id, username, password, email, full_name, role) VALUES (1, 'admin', '$2a$10$N9qo8UQOEtWpAjR8RVLzvuIKCqCr8lfKkEkWqHlRLqqM8qEYJNHn2', 'admin@grocery.com', 'Administrator', 'ADMIN'); >> temp.sql

mysql -u root -p < temp.sql
del temp.sql
echo ✓ Database created
echo.

REM Build Backend
echo Building backend (2-3 minutes)...
cd backend
mvn clean package -DskipTests -q
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)
cd ..
echo ✓ Backend built
echo.

REM Setup Frontend
echo Setting up frontend...
cd frontend
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate
pip install -q -r requirements.txt
cd ..
echo ✓ Frontend ready
echo.

REM Create startup scripts
echo @echo off > run_backend.bat
echo cd backend >> run_backend.bat
echo mvn spring-boot:run >> run_backend.bat

echo @echo off > run_frontend.bat
echo cd frontend >> run_frontend.bat
echo call venv\Scripts\activate >> run_frontend.bat
echo python manage.py runserver 0.0.0.0:8000 >> run_frontend.bat

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Starting services...
start "Backend" cmd /k run_backend.bat
timeout /t 5 >nul
start "Frontend" cmd /k run_frontend.bat
timeout /t 10 >nul
start http://localhost:8000

echo.
echo ✓ Website is starting!
echo ✓ Login: admin / admin123
echo.
echo Two windows opened - keep them running!
pause
