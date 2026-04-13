@echo off
setlocal
set SCRIPT_DIR=%~dp0
if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs"
cd /d "%SCRIPT_DIR%frontend"
if not exist node_modules (
  echo Frontend dependencies are missing. Run setup_frontend.ps1 first.
  exit /b 1
)
npm run dev -- --host 127.0.0.1 --port 5173 1>"%SCRIPT_DIR%logs\frontend.out.log" 2>"%SCRIPT_DIR%logs\frontend.err.log"
