param(
    [string]$BaseUrl = "http://127.0.0.1:8001"
)

$ErrorActionPreference = "Stop"

Write-Host "Health"
curl.exe -s "$BaseUrl/health"
Write-Host "`nList users"
curl.exe -s "$BaseUrl/users"
Write-Host "`nCreate user"
curl.exe -s -X POST "$BaseUrl/users" -H "Content-Type: application/json" -d "{\"name\":\"Usuario Demo\",\"age\":31}"
Write-Host "`nUpdate user"
curl.exe -s -X PUT "$BaseUrl/users/1" -H "Content-Type: application/json" -d "{\"name\":\"Usuario 1 Atualizado\",\"age\":40}"
Write-Host "`nPlaylists by user"
curl.exe -s "$BaseUrl/users/1/playlists"
Write-Host "`nMusics by playlist"
curl.exe -s "$BaseUrl/playlists/1/musics"
Write-Host "`nPlaylists by music"
curl.exe -s "$BaseUrl/musics/1/playlists"
