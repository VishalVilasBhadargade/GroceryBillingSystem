@echo off
setlocal

set "TASK_NAME=GroceryPaymentReminder"
set "SCRIPT_PATH=%~dp0run_payment_reminders.bat"

if not exist "%SCRIPT_PATH%" (
    echo [ERROR] Script not found: "%SCRIPT_PATH%"
    exit /b 1
)

echo Creating or updating scheduled task "%TASK_NAME%"...
schtasks /Create /SC DAILY /TN "%TASK_NAME%" /TR "\"%SCRIPT_PATH%\" whatsapp" /ST 10:00 /F >nul

if errorlevel 1 (
    echo [ERROR] Failed to create scheduled task.
    echo Try running this file as Administrator.
    exit /b 1
)

echo [OK] Scheduled task created successfully.
echo Task Name : %TASK_NAME%
echo Run Time  : Daily at 10:00 AM
echo Command   : "%SCRIPT_PATH%" whatsapp

exit /b 0
