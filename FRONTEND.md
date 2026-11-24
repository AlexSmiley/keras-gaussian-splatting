# Web frontend

**Vercel frontend:** [https://keras-gaussian-splatting.vercel.app](https://keras-gaussian-splatting.vercel.app)

Reconstruction requires a running worker and configured Vercel environment variables.

Deploy the repository on Vercel using the Other framework preset and repository root. Configure WORKER_URL (HTTPS origin), WORKER_TOKEN (same as worker), and GENERATION_KEY (a separate random access key). Redeploy after setting variables. The UI prompts for the generation key; it is never embedded in the bundle. Job IDs are random bearer identifiers; protect the whole deployment for private scenes. Add per-user auth, quotas and durable queue before public use.

Example URL: https://www.youtube.com/watch?v=oxxucX4dr5k . Confirm permission before submitting. This example has not been reconstructed or verified. Start the worker per README. The preview loads a pinned browser module from esm.sh; downloads remain available if preview fails. The existing experimental export format may require compatibility corrections.

Smoke test: open /, verify example URL, submit without authorization (blocked), submit with valid key and configured worker, observe status, download both files, inspect preview. Without a worker, /api returns worker_configured false and submission returns 503.
