@echo off
setlocal

set "BASE_DIR=%~dp0"
set "FRONTEND_DIR=%BASE_DIR%frontend"
set "PYTHON_EXE=%BASE_DIR%.venv\Scripts\python.exe"
set "CHANNEL=%~1"

if "%CHANNEL%"=="" set "CHANNEL=whatsapp"

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python executable not found at: "%PYTHON_EXE%"
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo [ERROR] Frontend directory not found at: "%FRONTEND_DIR%"
    exit /b 1
)

if not exist "%FRONTEND_DIR%\logs" mkdir "%FRONTEND_DIR%\logs"

cd /d "%FRONTEND_DIR%"
echo [%date% %time%] Running payment reminders on channel: %CHANNEL%>> "%FRONTEND_DIR%\logs\payment_reminders.log"
"%PYTHON_EXE%" manage.py send_payment_reminders --channel %CHANNEL% --interval-days 2 --days 0 >> "%FRONTEND_DIR%\logs\payment_reminders.log" 2>&1

if errorlevel 1 (
    echo [ERROR] Reminder command failed. Check logs\payment_reminders.log
    exit /b 1
)

echo [OK] Reminder command completed successfully.
exit /b 0
