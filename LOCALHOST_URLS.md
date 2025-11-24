# Cinefilm Platform - Localhost URLs Reference

## ✅ Working URLs

### Frontend (Next.js)
- **Main App**: http://localhost:3000
- **Landing Page**: http://localhost:3000/
- **Login**: http://localhost:3000/login
- **Projects (Studio)**: http://localhost:3000/projects
- **Project Detail**: http://localhost:3000/projects/[id]
- **Admin Dashboard**: http://localhost:3000/admin
- **Admin Users**: http://localhost:3000/admin/users
- **Admin Projects**: http://localhost:3000/admin/projects
- **Admin Workflows**: http://localhost:3000/admin/workflows
- **Admin Agents**: http://localhost:3000/admin/agents

### Backend API (FastAPI)
- **API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **API Base**: http://localhost:8000/api
- **Projects API**: http://localhost:8000/api/projects
- **Agents API**: http://localhost:8000/api/agents
- **Admin API**: http://localhost:8000/api/admin
- **Webhooks**: http://localhost:8000/api/webhooks

### n8n (Workflow Automation)
- **n8n UI**: http://localhost:5678/home/workflows
- **n8n Base**: http://localhost:5678
- **Default Credentials**: 
  - Email: `admin@example.com`
  - Password: `changeme` (or check docker-compose.yml)

### Firebase Emulators
- **Emulator UI Dashboard**: http://localhost:4000 ✅ (Main UI for all emulators)
- **Auth Emulator**: http://localhost:9099 (direct API)
- **Firestore Emulator**: http://localhost:8080 (direct API)
- **Storage Emulator**: http://localhost:9199 (direct API)
- **Functions Emulator**: http://localhost:5001 (if enabled)
- **Emulator Hub**: http://localhost:4400 (internal)

### Database & Cache
- **PostgreSQL**: `localhost:5432`
  - Database: `cinefilm`
  - User: `postgres`
  - Password: `postgres`
- **Redis**: `localhost:6379`

## ✅ All Services Working!

All services are now accessible. The Firebase Emulator UI is configured to bind to `0.0.0.0` so it's accessible from outside the Docker container.

### Firebase Emulator UI Features
- View and manage Auth users: http://localhost:4000/auth
- View and query Firestore data: http://localhost:4000/firestore
- View and manage Storage files: http://localhost:4000/storage
- Main dashboard: http://localhost:4000

### Alternative: Use Firebase CLI
You can also interact with emulators via CLI:
```bash
# View emulator status
docker-compose logs firebase-emulators

# Access emulator data
# Auth: Use Firebase SDK in your app (already configured)
# Firestore: Use Firestore SDK (already configured)
# Storage: Use Storage SDK (already configured)
```

## Quick Access Commands

```bash
# Open all services in browser (macOS)
open http://localhost:3000      # Frontend
open http://localhost:8000/docs  # Backend API Docs
open http://localhost:5678       # n8n
open http://localhost:4000      # Firebase Emulator UI

# Check service status
docker-compose ps

# View logs
docker-compose logs -f frontend
docker-compose logs -f backend-api
docker-compose logs -f firebase-emulators
docker-compose logs -f n8n
```

## Service Ports Summary

| Service | Port | Status | URL |
|--------|------|--------|-----|
| Frontend (Next.js) | 3000 | ✅ Working | http://localhost:3000 |
| Backend API (FastAPI) | 8000 | ✅ Working | http://localhost:8000 |
| n8n | 5678 | ✅ Working | http://localhost:5678 |
| Firebase Auth Emulator | 9099 | ✅ Working | http://localhost:9099 |
| Firebase Firestore Emulator | 8080 | ✅ Working | http://localhost:8080 |
| Firebase Storage Emulator | 9199 | ✅ Working | http://localhost:9199 |
| Firebase Emulator UI | 4000 | ✅ Working | http://localhost:4000 |
| PostgreSQL | 5432 | ✅ Running | localhost:5432 |
| Redis | 6379 | ✅ Running | localhost:6379 |

## Testing Endpoints

### Backend Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","redis":"available"}
```

### Frontend Health
```bash
curl http://localhost:3000
# Should return HTML
```

### Firebase Auth Emulator
```bash
curl http://localhost:9099
# Should return emulator info
```

### Firebase Firestore Emulator
```bash
curl http://localhost:8080
# Should return emulator info
```

## Notes

- All services are running in Docker containers
- Hot reload is enabled for frontend and backend
- Firebase emulators are configured for local development
- The Firebase Emulator UI (port 4000) may require additional configuration or may not be fully supported in the current setup
- Use direct emulator endpoints (9099, 8080, 9199) instead of the UI hub

