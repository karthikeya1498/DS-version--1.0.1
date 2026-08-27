# Security, Real-Time Streaming, and Operations Dashboard

**Author: Karthikeya**

OPTIMA-X now includes development-ready tenant-aware JWTs, an in-process sliding-window rate limiter, a traffic update publisher, and a WebSocket endpoint at `/api/v1/ws/traffic`. Clients authenticate with a token query parameter for the WebSocket handshake; REST clients use the standard `Authorization: Bearer <token>` header.

The token endpoint is `POST /api/v1/auth/token` and accepts `username`, `password`, and `tenant_id`. The current implementation is a service scaffold: production deployments must replace the permissive login handler with an identity provider or hashed credential store, use a strong `JWT_SECRET`, enforce `AUTH_REQUIRED=true`, and move rate-limit state to Redis or another shared store when multiple replicas are deployed.

The browser operations dashboard is the TypeScript/HTML/CSS application under `frontend/`; it calls the FastAPI application boundary and presents seeded scenario metrics and decision traces. On startup, `frontend/src/main.ts` obtains a short-lived development JWT from `/api/v1/auth/token`, opens `/api/v1/ws/traffic?token=...`, renders `route_reoptimization` events, and retries the connection after transient disconnects. The Streamlit research dashboard remains `dashboard.py` and visualizes the road network, benchmark runtime, and XGBoost forecast metrics. Docker Compose exposes Streamlit at `http://localhost:8501` alongside the API at `http://localhost:8000`.

```bash
JWT_SECRET='replace-with-a-long-random-secret' AUTH_REQUIRED=true docker compose up --build
```
