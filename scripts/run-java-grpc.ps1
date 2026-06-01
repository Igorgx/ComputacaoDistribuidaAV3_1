$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$mvn = & (Join-Path $PSScriptRoot "setup-maven.ps1")
$work = Join-Path $env:TEMP "music-streaming-java-grpc"
if (Test-Path $work) {
    $resolved = (Resolve-Path $work).Path
    if (-not $resolved.StartsWith((Resolve-Path $env:TEMP).Path)) {
        throw "Refusing to remove unexpected path: $resolved"
    }
    Remove-Item -Recurse -Force -LiteralPath $work
}
New-Item -ItemType Directory -Force -Path (Join-Path $work "java") | Out-Null
Copy-Item -Recurse -Force -Path (Join-Path $root "java/grpc") -Destination (Join-Path $work "java/grpc")
Copy-Item -Recurse -Force -Path (Join-Path $root "java/common") -Destination (Join-Path $work "java/common")
Push-Location (Join-Path $work "java/grpc")
try {
    & $mvn -q compile exec:java
} finally {
    Pop-Location
}
