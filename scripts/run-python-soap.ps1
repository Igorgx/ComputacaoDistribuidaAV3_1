$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = $root
$python = Join-Path $root ".venv/Scripts/python.exe"
if (-not (Test-Path $python)) { & (Join-Path $PSScriptRoot "setup-python.ps1") }
& $python -m python.soap.main
