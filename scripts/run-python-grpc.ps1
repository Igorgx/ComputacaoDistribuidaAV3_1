$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = "$root;$(Join-Path $root 'python/grpc/generated')"
$python = Join-Path $root ".venv/Scripts/python.exe"
if (-not (Test-Path $python)) { & (Join-Path $PSScriptRoot "setup-python.ps1") }
& $python -m python.grpc.server
