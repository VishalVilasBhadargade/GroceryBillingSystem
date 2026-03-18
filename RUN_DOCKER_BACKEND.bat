@echo off
setlocal

cd /d "%~dp0backend"
call docker_build_run_logs.bat

endlocal
