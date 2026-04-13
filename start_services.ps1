param(
    [switch]$OpenBrowser
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$StartCmd = Join-Path $Root "start_services.cmd"

cmd.exe /c "`"$StartCmd`""
if ($LASTEXITCODE -ne 0) {
    throw "start_services.cmd failed."
}

if ($OpenBrowser) {
    cmd.exe /c start "" "http://127.0.0.1:5173" | Out-Null
}
