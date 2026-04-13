@echo off
setlocal
set SCRIPT_DIR=%~dp0
if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs"
set BACKEND_DIR=%SCRIPT_DIR%backend
set BACKEND_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe
if not exist "%BACKEND_PYTHON%" set BACKEND_PYTHON=%SCRIPT_DIR%backend_dependency\venv\Scripts\python.exe
if not exist "%BACKEND_PYTHON%" (
  echo Python virtual environment not found. Run setup_backend.ps1 first.
  exit /b 1
)
cd /d "%BACKEND_DIR%"
"%BACKEND_PYTHON%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 1>"%SCRIPT_DIR%logs\backend.out.log" 2>"%SCRIPT_DIR%logs\backend.err.log"
