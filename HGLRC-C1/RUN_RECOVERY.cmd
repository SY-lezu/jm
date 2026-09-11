@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py hglrc_c1_recovery.py
) else (
  python hglrc_c1_recovery.py
)
pause
