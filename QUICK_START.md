# 🚀 Cinefilm Platform - Quick Start Guide

## Prerequisites

- ✅ Docker/OrbStack installed and running
- ✅ Google Cloud SDK authenticated (`gcloud auth login`)
- ✅ Firebase CLI installed (`npm install -g firebase-tools`)
- ✅ Firebase CLI authenticated (`firebase login`)

## Local Development (5 Minutes)

### 1. Set Up Environment Files

```bash
# Backend
cp backend/env.example backend/.env
# Edit backend/.env with your Firebase service account path

# Frontend  
cp web-app/env.example web-app/.env.local
# Edit web-app/.env.local with your Firebase config
```

### 2. Start Everything

```bash
./scripts/dev.sh
```

**That's it!** All services are now running in Docker containers.

### 3. Access Your App

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **n8n**: http://localhost:5678 (admin/changeme)

### 4. Start Coding

- Edit code in `backend/` → Backend auto-reloads
- Edit code in `web-app/` → Frontend auto-reloads
- No need to restart containers!

## Deployment (Automatic)

### Dev Environment

```bash
git checkout -b dev
git push origin dev
# GitHub Actions automatically deploys
```

### Staging Environment

```bash
git checkout -b staging
git push origin staging
# Deploys to staging.cinefilm.tech
```

### Production Environment

```bash
git checkout main
git push origin main
# Deploys to cinefilm.tech
```

## Common Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Stop services
docker-compose down

# Rebuild after dependency changes
docker-compose build --no-cache [service-name]
docker-compose up
```

## File Structure

```
cinefilm/
├── docker-compose.yml      # Start here!
├── backend/                # FastAPI backend
├── web-app/                # Next.js frontend
├── scripts/                # Helper scripts
└── .github/workflows/      # CI/CD automation
```

## Troubleshooting

**Services won't start?**
- Check Docker is running: `docker info`
- Check logs: `docker-compose logs`
- Rebuild: `docker-compose build --no-cache`

**Frontend can't reach backend?**
- Check `NEXT_PUBLIC_API_URL` in `web-app/.env.local`
- Should be `http://backend-api:8000` in Docker

**Need help?**
- Check `VERIFICATION_CHECKLIST.md`
- Check `README_DOCKER.md`
- Check logs: `docker-compose logs -f`

---

**Happy coding!** 🎬

