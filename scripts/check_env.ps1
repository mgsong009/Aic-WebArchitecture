$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $root ".env"
$checkScript = Join-Path $PSScriptRoot "check_env.py"

$candidatePaths = @(
    (Join-Path $root ".venv\Scripts\python.exe"),
    (Join-Path $root "aic-backend\.venv\Scripts\python.exe"),
    (Join-Path $root "aic-pipeline\.venv\Scripts\python.exe"),
    (Join-Path $env:USERPROFILE "anaconda3\python.exe")
)

foreach ($candidate in $candidatePaths) {
    if ($candidate -and (Test-Path $candidate)) {
        & $candidate $checkScript $envFile
        exit $LASTEXITCODE
    }
}

$pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
if ($pythonCommand -and $pythonCommand.Source -notlike "*\WindowsApps\python.exe") {
    & $pythonCommand.Source $checkScript $envFile
    exit $LASTEXITCODE
}

$pyCommand = Get-Command py.exe -ErrorAction SilentlyContinue
if ($pyCommand) {
    & $pyCommand.Source -3 $checkScript $envFile
    exit $LASTEXITCODE
}

throw "Python not found. Install Python or create a virtual environment at .venv, aic-backend\.venv, or aic-pipeline\.venv."
