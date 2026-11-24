# Worker deployment
The default container uses CPU TensorFlow and CPU COLMAP for portability. Training may be slow and memory intensive. GPU acceleration requires a compatible GPU runtime/image; this container does not configure CUDA.

1. Install Docker with Compose on a Linux host with sufficient RAM and disk.
2. Create .env from .env.example and replace both values with distinct secrets (openssl rand -hex 32). Never commit .env.
3. Run docker compose up -d --build.
4. Check docker compose logs -f worker and curl http://127.0.0.1:8000/health.
5. Expose the loopback worker through an HTTPS reverse proxy on your host. Set WORKER_URL to that HTTPS origin in Vercel, WORKER_TOKEN to the same worker secret, and GENERATION_KEY to the separate generation key. Redeploy Vercel.
6. Open the frontend and enter the generation key and authorized video URL.

Local smoke test (only if authorized):
```sh
set -a; . ./.env; set +a
curl -fsS http://127.0.0.1:8000/jobs -H "X-Worker-Token: $WORKER_TOKEN" -H 'Content-Type: application/json' -d '{"url":"https://www.youtube.com/watch?v=oxxucX4dr5k","authorized":true}'
```
Poll /jobs/JOB_ID with the same token. Outputs persist in the reconstruction-data volume. Do not delete the volume unless you intend to delete jobs. Restrict access, monitor disk usage and clean old jobs manually. The in-process queue does not resume interrupted jobs. The health endpoint checks service availability, not successful ML reconstruction.
