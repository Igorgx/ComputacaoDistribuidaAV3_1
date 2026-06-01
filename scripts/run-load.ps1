param(
    [string]$Class = "MusicHttpUser",
    [string]$HostUrl = "http://127.0.0.1:8001",
    [int]$Users = 100,
    [int]$SpawnRate = 20,
    [string]$RunTime = "1m",
    [string]$Protocol = "rest",
    [string]$Out = "results"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = "$root;$(Join-Path $root 'python/grpc/generated')"
$env:PROTOCOL = $Protocol
$python = Join-Path $root ".venv/Scripts/python.exe"
if (-not (Test-Path $python)) { & (Join-Path $PSScriptRoot "setup-python.ps1") }
New-Item -ItemType Directory -Force -Path (Join-Path $root "report/results") | Out-Null
& $python -m locust `
    -f (Join-Path $root "load-tests/locustfile.py") `
    $Class `
    --headless `
    --host $HostUrl `
    --users $Users `
    --spawn-rate $SpawnRate `
    --run-time $RunTime `
    --csv (Join-Path $root "report/results/$Out") `
    --html (Join-Path $root "report/results/$Out.html")
