param(
    [string]$BaseUrl = "http://127.0.0.1:8004"
)

$ErrorActionPreference = "Stop"

$payload = @"
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <listMusics xmlns="music.streaming.soap"/>
  </soap:Body>
</soap:Envelope>
"@

(Invoke-WebRequest -Uri $BaseUrl -Method Post -ContentType "text/xml" -Body $payload).Content
