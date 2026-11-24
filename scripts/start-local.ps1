$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
function New-Secret {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    return ([BitConverter]::ToString($bytes)).Replace("-", "").ToLowerInvariant()
}
if (!(Test-Path .env)) {
    @("WORKER_TOKEN=$(New-Secret)", "GENERATION_KEY=$(New-Secret)") | Set-Content -Encoding ascii .env
}
docker compose -f compose.yaml -f compose.tunnel.yaml up -d --build
if ($LASTEXITCODE -ne 0) { throw "Docker startup failed" }
Write-Host "Waiting for tunnel URL..."
$url = $null
for ($i=0; $i -lt 120; $i++) {
    $logs = docker compose -f compose.yaml -f compose.tunnel.yaml logs --no-color tunnel 2>&1 | Out-String
    $matchesFound = [regex]::Matches($logs, 'https://[a-z0-9-]+\.trycloudflare\.com')
    if ($matchesFound.Count -gt 0) { $url = $matchesFound[$matchesFound.Count-1].Value; break }
    Start-Sleep -Seconds 2
}
if (!$url) { throw "Tunnel URL not found; inspect Docker logs" }
Invoke-RestMethod -Uri "$url/health" -TimeoutSec 30
Write-Host "WORKER_URL=$url"
Write-Host "Set WORKER_TOKEN and GENERATION_KEY from your local .env in Vercel. Do not share them."
Write-Host "Redeploy Vercel after updating environment variables."
