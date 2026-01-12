param(
  [string]$HostAddr = "127.0.0.1",
  [int]$Port = 8001,
  [switch]$Reload
)

$ErrorActionPreference = "Stop"

# Always run from repo root so `server` is importable as a package.
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$venvPy = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPy) {
  $py = $venvPy
} else {
  $py = "python"
}

$argsList = @(
  "-m", "uvicorn",
  "server.main:app",
  "--host", $HostAddr,
  "--port", "$Port",
  "--log-level", "info"
)

if ($Reload) {
  $argsList += "--reload"
}

Write-Host "Starting backend: $py $($argsList -join ' ')" -ForegroundColor Cyan
& $py @argsList
