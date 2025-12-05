# Production Runbook for ehr-nlp-project

This document covers building the frontend for production, serving pre-compressed assets with nginx, CI checks, and rollout/rollback steps.

## Build

### 1. Frontend Assets (SASS)

The project uses a custom SASS build of Pico CSS 2.0.

**Prerequisites:**
- Node.js & npm installed

**Build Command:**
```powershell
# Install dependencies
npm install

# Compile SASS to CSS (Compressed)
npm run sass:build
```

This generates `backend/static/css/theme.css`.

### 2. Python Backend

Ensure all dependencies are installed:
```powershell
pip install -r requirements.txt
```

## Serve pre-compressed assets (nginx)

Recommended: have nginx front the application and serve static assets directly. Example `nginx` configuration snippet:

```
server {
  listen 80;
  server_name example.com;

  root /var/www/ehr-nlp-project/backend/static;

  location / {
    proxy_pass http://localhost:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }

  # Serve static assets directly
  location /static {
    alias /var/www/ehr-nlp-project/backend/static;
    expires 30d;
    add_header Cache-Control "public, no-transform";
  }

  location ~* \.(?:js|css|png|jpg|jpeg|gif|svg|ico)$ {
    add_header Cache-Control "public, max-age=31536000, immutable";
    try_files $uri $uri/ =404;
  }
}
```

Notes:
- Ensure nginx doesn't double-compress. The `add_header Content-Encoding` lines tell nginx to return compressed content.
- You may instead use the `brotli` nginx module; adjust accordingly.

## Serving from Flask (fallback)

If you must serve static files from Flask, ensure your webserver (gunicorn/uwsgi) is placed behind nginx for compression and caching. Flask can also be configured to send `.br`/.gz files when available — but do this only if you cannot use nginx.

## CI (GitLab)

A `.gitlab-ci.yml` is included to build the frontend and run the `verify-bundle` script. The CI will fail if the initial bundle is larger than configured thresholds (150KB gzip, 120KB brotli).

## Rollout checklist

- [ ] Build artifacts locally and run `verify-bundle`.
- [ ] Deploy to staging behind nginx with the above config.
- [ ] Smoke test critical flows: load home page, patients page, create/edit medical note, open joint-assessment canvas.
- [ ] Measure Real-World Performance (FCP, TTI) via Lighthouse or RUM.
- [ ] Canary deploy: route small percentage of traffic to new deployment.
- [ ] If stable for 24–72 hours, promote to full rollout.

## Rollback

- If issues occur, revert the deployment and redeploy previous artifact. Ensure stale CDN caches are purged if needed.

## Monitoring & Alerts

- Watch for: increased error rates, JS exceptions, slow TTI/FCP, and bundle size regressions.
- Log build artifacts and manifest to track changes in entry chunk sizes over time.

## Tips

- Prefer Brotli for clients that support it; gzip fallback keeps compatibility.
- Keep large vendor libraries (Konva) lazy-loaded to avoid initial payload regressions.
- Use the bundle visualizer occasionally to understand chunk composition.
