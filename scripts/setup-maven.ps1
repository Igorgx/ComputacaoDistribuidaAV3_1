$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$tools = Join-Path $root ".tools"
$mavenHome = Join-Path $tools "apache-maven-3.9.9"
$mavenBin = Join-Path $mavenHome "bin/mvn.cmd"

if (-not (Test-Path $mavenBin)) {
    New-Item -ItemType Directory -Force -Path $tools | Out-Null
    $zip = Join-Path $tools "apache-maven-3.9.9-bin.zip"
    if (-not (Test-Path $zip)) {
        $urls = @(
            "https://dlcdn.apache.org/maven/maven-3/3.9.9/binaries/apache-maven-3.9.9-bin.zip",
            "https://archive.apache.org/dist/maven/maven-3/3.9.9/binaries/apache-maven-3.9.9-bin.zip",
            "https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.9/apache-maven-3.9.9-bin.zip"
        )
        foreach ($url in $urls) {
            try {
                Invoke-WebRequest -Uri $url -OutFile $zip
                break
            } catch {
                if (Test-Path $zip) { Remove-Item $zip -Force }
                if ($url -eq $urls[-1]) { throw }
            }
        }
    }
    Expand-Archive -Force -Path $zip -DestinationPath $tools
}

Write-Output $mavenBin
