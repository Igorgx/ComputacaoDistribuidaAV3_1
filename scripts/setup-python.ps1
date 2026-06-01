$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $root ".venv"

if (-not (Test-Path $venv)) {
    python -m venv $venv
}

$python = Join-Path $venv "Scripts/python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -r (Join-Path $root "python/requirements.txt")

$generated = Join-Path $root "python/grpc/generated"
New-Item -ItemType Directory -Force -Path $generated | Out-Null

& $python -m grpc_tools.protoc `
    -I (Join-Path $root "shared/proto") `
    --python_out=$generated `
    --grpc_python_out=$generated `
    (Join-Path $root "shared/proto/music.proto")

Write-Host "Python environment ready at $venv"
