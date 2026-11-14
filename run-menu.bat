@echo off
setlocal EnableDelayedExpansion
title Eastern Special Inihaw Menu - local preview
cd /d "%~dp0"

rem ---- find Python ----
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY where py >nul 2>nul && set "PY=py"
if not defined PY (
  echo.
  echo  Python was not found. Install it from https://www.python.org/downloads/
  echo  and tick "Add python.exe to PATH" during setup.
  echo.
  pause
  exit /b 1
)

rem ---- pick a free port (8080-8090) ----
set "PORT="
for /l %%p in (8080,1,8090) do (
  if not defined PORT (
    netstat -ano | findstr /r /c:":%%p .*LISTENING" >nul || set "PORT=%%p"
  )
)
if not defined PORT set "PORT=8091"

rem ---- this PC's Wi-Fi/LAN address, for testing on a phone (skips VMware/virtual adapters) ----
set "LANIP="
for /f "delims=" %%a in ('%PY% -c "import socket;s=socket.socket(2,2);s.connect(('8.8.8.8',80));print(s.getsockname()[0])" 2^>nul') do set "LANIP=%%a"

echo.
echo  ==============================================
echo    EASTERN SPECIAL INIHAW MENU - running locally
echo  ==============================================
echo.
echo    On this PC :  http://localhost:%PORT%/
if defined LANIP echo    On a phone :  http://!LANIP!:%PORT%/   (same Wi-Fi; allow Python if Windows Firewall asks)
echo.
echo    Close this window or press Ctrl+C to stop.
echo.

if not "%NO_BROWSER%"=="1" start "" "http://localhost:%PORT%/"

%PY% -m http.server %PORT%
