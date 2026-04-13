$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendDir = Join-Path $Root "frontend"

if (-not (Test-Path (Join-Path $FrontendDir "package.json"))) {
    throw "frontend\\package.json not found."
}

Push-Location $FrontendDir
try {
    Write-Host "Installing frontend dependencies ..."
    npm install
} finally {
    Pop-Location
}

Write-Host "Frontend setup completed."
