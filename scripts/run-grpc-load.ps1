param(
    [string]$Target = "127.0.0.1:8102",
    [int]$Users = 100,
    [double]$SpawnRate = 20,
    [int]$RunTimeSeconds = 120,
    [string]$Out = "java_grpc_moderada"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = "$root;$(Join-Path $root 'python/grpc/generated')"
$python = Join-Path $root ".venv/Scripts/python.exe"
if (-not (Test-Path $python)) { & (Join-Path $PSScriptRoot "setup-python.ps1") }

& $python (Join-Path $root "load-tests/grpc_load_test.py") `
    --target $Target `
    --users $Users `
    --spawn-rate $SpawnRate `
    --run-time $RunTimeSeconds `
    --out $Out
