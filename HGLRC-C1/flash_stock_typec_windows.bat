@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"

set "FW=stock\HGLRC-C1_DRAGON-V2.0_community-stock-dump.bin"

echo ============================================================
echo HGLRC C1 Type-C stock firmware recovery (Windows)
echo - Uses the C1 USB-C / CH340 serial connection
echo - Backs up the full 4MB flash BEFORE writing
echo - Writes ONLY the ESP32 application at 0x10000
echo - Does NOT erase the whole chip
echo ============================================================
echo.

if not exist "%FW%" (
  echo ERROR: Firmware not found: %FW%
  echo Please run this BAT from the HGLRC-C1 folder in the repository.
  pause
  exit /b 1
)

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo ERROR: Python 3 was not found.
    echo Install Python 3 from python.org, then run this BAT again.
    pause
    exit /b 1
  )
  set "PY=python"
)

%PY% -m esptool version >nul 2>nul
if errorlevel 1 (
  echo Installing esptool...
  %PY% -m pip install --user --upgrade esptool
  if errorlevel 1 (
    echo ERROR: Could not install esptool.
    pause
    exit /b 1
  )
)

echo.
echo Detected USB serial / CH340 devices:
powershell -NoProfile -Command "Get-CimInstance Win32_PnPEntity ^| Where-Object { $_.Name -match 'CH340|USB-SERIAL|USB Serial' } ^| Select-Object -ExpandProperty Name"
echo.
set /p PORT=Enter the C1 COM port, for example COM6: 
if "%PORT%"=="" (
  echo ERROR: No COM port entered.
  pause
  exit /b 1
)

set "BACKUP=C1_fullflash_backup_%PORT%_%RANDOM%.bin"

echo.
echo STEP 1/3 - Backing up the full 4MB flash to:
echo   %BACKUP%
echo Keep the C1 connected by USB-C. Do not unplug it.
echo.
%PY% -m esptool --chip esp32 --port %PORT% --baud 115200 read_flash 0x000000 0x400000 "%BACKUP%"
if errorlevel 1 (
  echo.
  echo BACKUP FAILED. Nothing has been written.
  echo If esptool stays on Connecting..., close any program using the COM port,
  echo unplug/replug the USB-C cable, keep the controller powered OFF first, and retry.
  pause
  exit /b 1
)

echo.
echo STEP 2/3 - Flashing C1 stock application to 0x10000...
echo IMPORTANT: This does not erase bootloader, partition table, or the rest of flash.
echo.
%PY% -m esptool --chip esp32 --port %PORT% --baud 460800 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 40m --flash_size detect 0x10000 "%FW%"
if errorlevel 1 (
  echo.
  echo 460800 baud failed. Retrying at 115200...
  %PY% -m esptool --chip esp32 --port %PORT% --baud 115200 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 40m --flash_size detect 0x10000 "%FW%"
  if errorlevel 1 (
    echo.
    echo FLASH FAILED. Your full flash backup is preserved as:
    echo   %BACKUP%
    pause
    exit /b 1
  )
)

echo.
echo STEP 3/3 - Verifying the flashed application...
%PY% -m esptool --chip esp32 --port %PORT% --baud 115200 verify_flash 0x10000 "%FW%"
if errorlevel 1 (
  echo.
  echo WARNING: Verification failed. Do not continue testing the radio yet.
  echo Your full flash backup is preserved as:
  echo   %BACKUP%
  pause
  exit /b 1
)

echo.
echo ============================================================
echo FLASH + VERIFY SUCCESS
echo Full backup saved as:
echo   %BACKUP%
echo.
echo Now unplug USB-C, wait a few seconds, then power on the C1 normally.
echo First test: sticks/buttons, then SET+POWER Wi-Fi mode, then ELRS binding.
echo ============================================================
pause
