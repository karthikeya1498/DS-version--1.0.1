# Security, Real-Time Streaming, and Operations Dashboard

OPTIMA-X now includes development-ready tenant-aware JWTs, an in-process sliding-window rate limiter, a traffic update publisher, and a WebSocket endpoint at `/api/v1/ws/traffic`. Clients authenticate with a token query parameter for the WebSocket handshake; REST clients use the standard `Authorization: Bearer <token>` header.

The token endpoint is `POST /api/v1/auth/token` and accepts `username`, `password`, and `tenant_id`. The current implementation is a service scaffold: production deployments must replace the permissive login handler with an identity provider or hashed credential store, use a strong `JWT_SECRET`, enforce `AUTH_REQUIRED=true`, and move rate-limit state to Redis or another shared store when multiple replicas are deployed.

The Streamlit dashboard is `dashboard.py`. It visualizes the road network, benchmark runtime, and XGBoost forecast metrics. Docker Compose exposes it at `http://localhost:8501` alongside the API at `http://localhost:8000`.

```bash
JWT_SECRET='replace-with-a-long-random-secret' AUTH_REQUIRED=true docker compose up --build
```
