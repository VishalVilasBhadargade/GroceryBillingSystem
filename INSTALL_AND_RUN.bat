@echo off
echo ========================================
echo Installing and Running Grocery Billing System
echo ========================================
echo.

REM Check Java
echo [1/6] Checking Java...
java -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Java is not installed!
    echo Please download Java 17 from: https://www.oracle.com/java/technologies/downloads/
    pause
    exit /b 1
)
echo ✓ Java is installed

REM Check Python
echo [2/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please download Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python is installed

REM Check if Maven is installed, if not use system Java to compile
echo [3/6] Checking Maven...
mvn --version >nul 2>&1
if errorlevel 1 (
    echo Maven not found - Installing Maven automatically...
    
    REM Download Maven
    if not exist "tools" mkdir tools
    if not exist "tools\apache-maven-3.9.6" (
        echo Downloading Maven...
        powershell -Command "Invoke-WebRequest -Uri 'https://dlcdn.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.zip' -OutFile 'tools\maven.zip'"
        powershell -Command "Expand-Archive -Path 'tools\maven.zip' -DestinationPath 'tools' -Force"
        del tools\maven.zip
    )
    set "MAVEN_HOME=%CD%\tools\apache-maven-3.9.6"
    set "PATH=%MAVEN_HOME%\bin;%PATH%"
    echo ✓ Maven downloaded and configured
) else (
    echo ✓ Maven is already installed
)

REM Start MySQL
echo [4/6] Starting MySQL...
net start MySQL80 >nul 2>&1
if errorlevel 1 (
    net start MySQL >nul 2>&1
    if errorlevel 1 (
        echo WARNING: Could not start MySQL automatically
        echo Please start MySQL manually and press any key to continue...
        pause
    )
)
echo ✓ MySQL service started

REM Create Database
echo [5/6] Creating Database...
echo CREATE DATABASE IF NOT EXISTS grocery_billing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; > temp_db.sql
echo CREATE USER IF NOT EXISTS 'billing_user'@'localhost' IDENTIFIED BY 'secure_password_123'; >> temp_db.sql
echo GRANT ALL PRIVILEGES ON grocery_billing.* TO 'billing_user'@'localhost'; >> temp_db.sql
echo FLUSH PRIVILEGES; >> temp_db.sql

mysql -u root -p < temp_db.sql 2>nul
if errorlevel 1 (
    mysql -u root < temp_db.sql 2>nul
)
del temp_db.sql
echo ✓ Database created

REM Build Backend
echo [6/6] Building Backend (this may take 2-3 minutes)...
cd backend

REM Use Maven to build
if exist "%MAVEN_HOME%\bin\mvn.cmd" (
    call "%MAVEN_HOME%\bin\mvn.cmd" clean package -DskipTests
) else (
    mvn clean package -DskipTests
)

if errorlevel 1 (
    echo ERROR: Backend build failed!
    pause
    exit /b 1
)
echo ✓ Backend built successfully
cd ..

echo.
echo ========================================
echo Installation Complete! Starting Services...
echo ========================================
echo.

REM Create Backend Startup Script
echo @echo off > start_backend.bat
echo cd backend >> start_backend.bat
if exist "%MAVEN_HOME%\bin\mvn.cmd" (
    echo call "%MAVEN_HOME%\bin\mvn.cmd" spring-boot:run >> start_backend.bat
) else (
    echo mvn spring-boot:run >> start_backend.bat
)
echo pause >> start_backend.bat

REM Create Frontend Startup Script
echo @echo off > start_frontend.bat
echo cd frontend >> start_frontend.bat
echo if not exist "venv" ( >> start_frontend.bat
echo     echo Creating Python virtual environment... >> start_frontend.bat
echo     python -m venv venv >> start_frontend.bat
echo ) >> start_frontend.bat
echo call venv\Scripts\activate >> start_frontend.bat
echo pip install -q -r requirements.txt >> start_frontend.bat
echo python manage.py migrate --no-input >> start_frontend.bat
echo python manage.py runserver 0.0.0.0:8000 >> start_frontend.bat
echo pause >> start_frontend.bat

REM Start Backend in new window
echo Starting Backend Server (port 8080)...
start "Backend Server" cmd /k start_backend.bat

REM Wait 5 seconds for backend to initialize
timeout /t 5 /nobreak >nul

REM Start Frontend in new window
echo Starting Frontend Server (port 8000)...
start "Frontend Server" cmd /k start_frontend.bat

REM Wait 10 seconds for frontend to initialize
timeout /t 10 /nobreak >nul

REM Open Browser
echo Opening browser...
start http://localhost:8000

echo.
echo ========================================
echo ✓ ALL SERVICES STARTED!
echo ========================================
echo.
echo Backend:  http://localhost:8080
echo Frontend: http://localhost:8000
echo.
echo Login with:
echo   Username: admin
echo   Password: admin123
echo.
echo Two windows have opened - DO NOT CLOSE THEM!
echo - Backend Server (Java)
echo - Frontend Server (Python)
echo.
echo Press any key to see this information again...
pause
exit
