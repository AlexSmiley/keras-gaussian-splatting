# Local Windows worker + Vercel

**Vercel frontend:** [https://keras-gaussian-splatting.vercel.app](https://keras-gaussian-splatting.vercel.app)

Reconstruction requires a running worker and configured Vercel environment variables.

Install Docker Desktop with WSL2 and Linux containers. From PowerShell in the repository run:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/start-local.ps1
```
The script creates secrets only if .env is absent, builds the CPU worker, starts a Cloudflare Quick Tunnel and checks its public health endpoint. Existing .env values must be real secrets, not placeholders. The worker remains bound to loopback on the host; the tunnel uses the internal Compose network.

In Vercel project settings, set WORKER_URL to the printed HTTPS URL, WORKER_TOKEN and GENERATION_KEY to the corresponding values in .env. Redeploy production. Visit /api to check worker_configured, then submit an authorized video in the frontend using GENERATION_KEY.

Quick Tunnels are for development, have changing URLs and no uptime guarantee. Update WORKER_URL and redeploy whenever the URL changes. For stable use configure a named Cloudflare tunnel and your own hostname. Keep the computer awake and Docker running. The tunnel exposes the worker to the internet; job endpoints require the worker token. Protect the Vercel deployment for private data. Large downloads may exceed Vercel response limits; use direct authenticated local worker downloads for large files.

Stop: docker compose -f compose.yaml -f compose.tunnel.yaml down
Do not add -v unless you intend to erase stored jobs.
