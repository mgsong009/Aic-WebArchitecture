$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $root "aic-backend\.venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    throw "Python not found at $pythonExe"
}

$envFile = Join-Path $root ".env"
& $pythonExe (Join-Path $PSScriptRoot "check_env.py") $envFile
