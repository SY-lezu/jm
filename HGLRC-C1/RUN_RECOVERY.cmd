@echo off
setlocal
title HGLRC C1 Recovery Launcher
cd /d "%~dp0"

echo ==============================================================
echo  HGLRC C1 Recovery Launcher
echo ==============================================================
echo.
echo Current folder:
echo %CD%
echo.

if not exist "hglrc_c1_recovery.py" (
  echo [ERROR] hglrc_c1_recovery.py was not found.
  echo Please download the ENTIRE HGLRC-C1 folder, not only this CMD file.
  goto :fail
)

if not exist "stock\HGLRC-C1_DRAGON-V2.0_community-stock-dump.bin" (
  echo [ERROR] Firmware file was not found:
  echo stock\HGLRC-C1_DRAGON-V2.0_community-stock-dump.bin
  echo Please keep the stock folder next to this launcher.
  goto :fail
)

where py >nul 2>nul
if %errorlevel%==0 (
  echo [OK] Python launcher found: py
  echo.
  py --version
  echo.
  py "hglrc_c1_recovery.py"
  set RC=%errorlevel%
  goto :done
)

where python >nul 2>nul
if %errorlevel%==0 (
  echo [OK] Python found: python
  echo.
  python --version
  echo.
  python "hglrc_c1_recovery.py"
  set RC=%errorlevel%
  goto :done
)

echo [ERROR] Python is not installed or is not available in PATH.
echo.
echo Install Python 3 from:
echo https://www.python.org/downloads/windows/
echo.
echo IMPORTANT: during installation, tick "Add python.exe to PATH".
echo Then close this window and double-click RUN_RECOVERY.cmd again.
goto :fail

:done
echo.
echo --------------------------------------------------------------
echo Recovery program exited with code %RC%.
echo --------------------------------------------------------------
echo.
pause
exit /b %RC%

:fail
echo.
echo --------------------------------------------------------------
echo Launcher stopped before flashing. Nothing was written to C1.
echo --------------------------------------------------------------
echo.
pause
exit /b 1
