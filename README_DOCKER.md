# Docker & Deployment Guide

## Quick Start

### Local Development (Everything in Docker)

```bash
# Start all services
./scripts/dev.sh

# Or manually
docker-compose up

# View logs
docker-compose logs -f [service-name]

# Stop services
docker-compose down
```

### Access Points (Local)

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **n8n**: http://localhost:5678 (admin/changeme)

## Architecture

### Docker Network

All services run on `cinefilm-network`:
- `backend-api` - FastAPI backend (port 8000)
- `frontend` - Next.js frontend (port 3000)
- `postgres` - PostgreSQL database (port 5432)
- `redis` - Redis cache (port 6379)
- `n8n` - Workflow automation (port 5678)

### Internal Communication

- Frontend → Backend: `http://backend-api:8000` (Docker network)
- Backend → PostgreSQL: `postgresql://postgres:postgres@postgres:5432/cinefilm`
- Backend → Redis: `redis://redis:6379/0`

### Hot Reload

Both services support hot reload:
- **Backend**: Code changes trigger uvicorn reload
- **Frontend**: Next.js Fast Refresh on code changes

## Deployment

### Staging

```bash
./scripts/deploy-staging.sh
```

Or via GitHub:
```bash
git push origin staging
```

### Production

```bash
./scripts/deploy-prod.sh
```

Or via GitHub:
```bash
git push origin main
```

## Environment Variables

### Backend (.env)

```bash
ENVIRONMENT=development
DEBUG=true
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
FIREBASE_PROJECT_ID=cinefilm-platform
REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/cinefilm
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://backend-api:8000
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
# ... other Firebase config
```

## Troubleshooting

### Services won't start

```bash
# Check Docker is running
docker info

# Check logs
docker-compose logs

# Rebuild containers
docker-compose build --no-cache
docker-compose up
```

### Frontend can't reach backend

- Check `NEXT_PUBLIC_API_URL` is set to `http://backend-api:8000` in Docker
- Verify both services are on `cinefilm-network`
- Check backend logs: `docker-compose logs backend-api`

### Hot reload not working

- Ensure volumes are mounted correctly
- Check file permissions
- Restart containers: `docker-compose restart [service-name]`

## Production Considerations

- Backend uses multi-worker uvicorn (4 workers)
- Frontend uses static export for Firebase Hosting
- API calls proxied through Firebase Hosting rewrites
- Secrets managed via Google Secret Manager
- Cloud SQL for production database (not local PostgreSQL)

