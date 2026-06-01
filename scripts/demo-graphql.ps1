param(
    [string]$BaseUrl = "http://127.0.0.1:8003/graphql"
)

$ErrorActionPreference = "Stop"

$queries = @(
    "{ users { id name age } }",
    "{ musicsByPlaylist(playlistId: 1) { id name artist } }",
    "mutation { createUser(input: { name: `"Usuario GraphQL`", age: 29 }) { id name age } }"
)

foreach ($query in $queries) {
    $body = @{ query = $query } | ConvertTo-Json
    Invoke-RestMethod -Uri $BaseUrl -Method Post -ContentType "application/json" -Body $body |
        ConvertTo-Json -Depth 6
}
