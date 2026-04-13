@echo off
setlocal

set SCRIPT_DIR=%~dp0
if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs"

powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%stop_services.ps1" >nul 2>nul

start "" /min cmd /c "%SCRIPT_DIR%start_backend.cmd"
call :wait_http http://127.0.0.1:8000/api/analysis/health 45
if errorlevel 1 (
  echo Backend did not become ready in time. Check logs\backend.err.log
  exit /b 1
)

start "" /min cmd /c "%SCRIPT_DIR%start_frontend.cmd"
call :wait_http http://127.0.0.1:5173 45
if errorlevel 1 (
  echo Frontend did not become ready in time. Check logs\frontend.err.log
  exit /b 1
)

echo.
echo Services are running:
echo   Frontend: http://127.0.0.1:5173
echo   Backend : http://127.0.0.1:8000
echo.
echo Use stop_services.cmd to stop them.
exit /b 0

:wait_http
set URL=%~1
set MAX_SECONDS=%~2

for /L %%i in (1,1,%MAX_SECONDS%) do (
  powershell -NoProfile -Command "try { Invoke-WebRequest -Uri '%URL%' -UseBasicParsing -TimeoutSec 3 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
  if not errorlevel 1 exit /b 0
  timeout /t 1 /nobreak >nul
)

exit /b 1
