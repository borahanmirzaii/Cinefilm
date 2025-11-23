# Cinefilm Platform

A modern film production collaboration platform built with Next.js, FastAPI, and Firebase.

## 🏗️ Architecture

- **Frontend**: Next.js 16 + React 19 + TypeScript + Tailwind CSS
- **Backend**: FastAPI (Python 3.11) + Firebase Admin SDK
- **Database**: Firestore + Firebase Data Connect
- **Storage**: Firebase Storage
- **Infrastructure**: Google Cloud Run + Firebase Hosting
- **CI/CD**: GitHub Actions
- **Local Development**: Docker Compose (OrbStack)

## 🚀 Quick Start

### Prerequisites

- Docker/OrbStack installed and running
- Google Cloud SDK (`gcloud`)
- Firebase CLI (`firebase-tools`)
- Node.js 22+ (for local development)
- Python 3.11+ (for local development)

### Local Development (Docker)

```bash
# 1. Set up environment files
cp backend/env.example backend/.env
cp web-app/env.example web-app/.env.local

# 2. Edit .env files with your credentials

# 3. Start everything
./scripts/dev.sh

# Or manually
docker-compose up
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- n8n: http://localhost:5678

### Without Docker (Alternative)

```bash
# Backend
cd backend
uv sync
uv run uvicorn api.main:app --reload

# Frontend (separate terminal)
cd web-app
pnpm install
pnpm dev
```

## 📁 Project Structure

```
cinefilm/
├── backend/              # FastAPI backend
│   ├── api/             # API routes, models, services
│   ├── Dockerfile       # Multi-stage Docker build
│   └── cloudbuild.yaml  # Cloud Build config
├── web-app/             # Next.js frontend
│   ├── src/
│   │   ├── app/        # Next.js app router
│   │   ├── components/ # React components
│   │   ├── hooks/      # React hooks
│   │   └── lib/        # Utilities
│   └── Dockerfile      # Multi-stage Docker build
├── docker-compose.yml   # Local development setup
├── firebase.json        # Firebase configuration
└── scripts/            # Helper scripts
```

## 🐳 Docker Services

All services run in Docker containers:

- **backend-api** - FastAPI backend (port 8000)
- **frontend** - Next.js frontend (port 3000)
- **postgres** - PostgreSQL database (port 5432)
- **redis** - Redis cache (port 6379)
- **n8n** - Workflow automation (port 5678)

## 🚢 Deployment

### Automatic (GitHub Actions)

- **Dev**: Push to `dev` branch → Auto-deploys to dev environment
- **Staging**: Push to `staging` branch → Auto-deploys to staging.cinefilm.tech
- **Production**: Push to `main` branch → Auto-deploys to cinefilm.tech

### Manual

```bash
# Staging
./scripts/deploy-staging.sh

# Production
./scripts/deploy-prod.sh
```

## 📚 Documentation

- **[QUICK_START.md](./QUICK_START.md)** - Quick reference guide
- **[VERIFICATION_CHECKLIST.md](./VERIFICATION_CHECKLIST.md)** - Testing checklist
- **[README_DOCKER.md](./README_DOCKER.md)** - Detailed Docker guide
- **[DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)** - Deployment info

## 🔧 Development

### Backend

```bash
cd backend
uv sync
uv run uvicorn api.main:app --reload
```

### Frontend

```bash
cd web-app
pnpm install
pnpm dev
```

## 🔐 Environment Variables

See `backend/env.example` and `web-app/env.example` for required variables.

## 📞 Resources

- Firebase Console: https://console.firebase.google.com/project/cinefilm-platform
- Google Cloud Console: https://console.cloud.google.com/home/dashboard?project=cinefilm-platform
- GitHub Actions: https://github.com/borahanmirzaii/Cinefilm/actions

## 📄 License

Private - All Rights Reserved
