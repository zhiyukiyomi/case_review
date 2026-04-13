$ErrorActionPreference = "Continue"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogsDir = Join-Path $Root "logs"
$BackendPidFile = Join-Path $LogsDir "backend.pid"
$FrontendPidFile = Join-Path $LogsDir "frontend.pid"

function Stop-FromPidFile {
    param(
        [string]$PidFile,
        [string]$Name
    )
    if (-not (Test-Path $PidFile)) {
        return
    }

    $raw = (Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    $pidValue = 0
    if ([int]::TryParse($raw, [ref]$pidValue)) {
        try {
            $process = Get-Process -Id $pidValue -ErrorAction Stop
            Stop-Process -Id $process.Id -Force -ErrorAction Stop
            Write-Host "Stopped $Name process by pid: $pidValue"
        } catch {
            Write-Warning "Could not stop ${Name} by pid ${pidValue}: $($_.Exception.Message)"
        }
    }

    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

function Stop-FromPort {
    param(
        [int]$Port,
        [string]$Name
    )
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($conn) {
        try {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction Stop
            Write-Host "Stopped $Name process on port $Port (pid $($conn.OwningProcess))"
        } catch {
            Write-Warning "Could not stop ${Name} on port ${Port}: $($_.Exception.Message)"
        }
    }
}

Stop-FromPidFile -PidFile $BackendPidFile -Name "backend"
Stop-FromPidFile -PidFile $FrontendPidFile -Name "frontend"

Stop-FromPort -Port 8000 -Name "backend"
Stop-FromPort -Port 5173 -Name "frontend"

Write-Host "Done."
