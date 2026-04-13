$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $Root "backend"
$VenvDir = Join-Path $BackendDir ".venv"
$Requirements = Join-Path $BackendDir "requirements.txt"

if (-not (Test-Path $Requirements)) {
    throw "backend\\requirements.txt not found."
}

if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating backend virtual environment at $VenvDir ..."
    Push-Location $BackendDir
    try {
        python -m venv .venv
    } finally {
        Pop-Location
    }
}

$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    throw "Python virtual environment was not created correctly."
}

Write-Host "Installing backend dependencies ..."
& $PythonExe -m pip install --upgrade pip
& $PythonExe -m pip install -r $Requirements

if (-not (Test-Path (Join-Path $BackendDir ".env"))) {
    Copy-Item (Join-Path $BackendDir ".env.example") (Join-Path $BackendDir ".env")
    Write-Host "Created backend\\.env from backend\\.env.example"
}

Write-Host "Backend setup completed."
