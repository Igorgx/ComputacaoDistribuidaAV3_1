$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$out = Join-Path $root "build/java-rest"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$sources = @()
$sources += Get-ChildItem -Recurse -Filter *.java (Join-Path $root "java/common") | ForEach-Object FullName
$sources += Get-ChildItem -Recurse -Filter *.java (Join-Path $root "java/rest") | ForEach-Object FullName
javac -d $out $sources
java -cp $out com.music.rest.RestServer
