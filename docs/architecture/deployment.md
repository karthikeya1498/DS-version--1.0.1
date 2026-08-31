# Containerized Microservice Deployment

The routing and forecasting engine is exposed as a FastAPI REST service. The container runs as a non-root user, exposes port 8000, and includes a health check at `/api/v1/health`. PostgreSQL is provided as a Compose dependency for persistence-ready deployments.

```bash
docker compose up --build
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/routing/strategies
curl -X POST http://localhost:8000/api/v1/simulation/run \
  -H 'content-type: application/json' \
  -d '{"seed":42,"duration_hours":1,"zones":2,"vehicles":2,"orders_per_hour":2}'
```

The service is suitable for local reproducible demonstrations. Production deployment still requires secret management, TLS termination, authentication, rate limits, observability, database migrations, and resource limits.
