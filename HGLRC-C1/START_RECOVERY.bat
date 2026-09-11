@echo off
cd /d "%~dp0"
start "HGLRC C1 Recovery" cmd.exe /k call "%~dp0RUN_RECOVERY.cmd"
exit /b
