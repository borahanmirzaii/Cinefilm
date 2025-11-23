# Docker & Deployment Audit Report

## Current State Analysis

### ✅ What Exists:
1. **Docker Compose**: `infra/docker/docker-compose.yml` - Has backend, postgres, redis, n8n
2. **Backend Dockerfile**: `infra/docker/Dockerfile.backend` - Multi-stage (dev + prod)
3. **Frontend Dockerfile**: `infra/docker/Dockerfile.frontend` - Exists but needs Next.js updates
4. **GitHub Workflows**: `.github/workflows/` - dev.yml, staging.yml, production.yml exist
5. **Firebase Config**: `firebase.json` - Exists but missing API rewrites

### ❌ Critical Gaps:

#### 1. Docker Setup Issues:
- ❌ `docker-compose.yml` is in `infra/docker/` instead of project root
- ❌ Frontend service missing from docker-compose.yml
- ❌ Dockerfiles in wrong location (should be in `backend/` and `web-app/`)
- ❌ Frontend Dockerfile needs Next.js-specific configuration
- ❌ No hot reload verification for frontend

#### 2. Deployment Configuration:
- ❌ Missing `backend/cloudbuild.yaml` for Cloud Build
- ❌ `firebase.json` missing API rewrites to Cloud Run backend
- ❌ Frontend Dockerfile not optimized for Next.js production
- ❌ Missing environment variable configuration for production

#### 3. GitHub Actions Issues:
- ❌ Workflows reference wrong Dockerfile paths (`../infra/docker/Dockerfile.backend`)
- ❌ Frontend deployment doesn't use Docker (builds directly)
- ❌ Missing proper caching strategies
- ❌ No Firebase token configuration

#### 4. Missing Scripts:
- ❌ No `scripts/dev.sh` for local development
- ❌ No `scripts/deploy-staging.sh`
- ❌ No `scripts/deploy-prod.sh`

## Files to Create/Update

### Create:
1. `docker-compose.yml` (root level)
2. `backend/Dockerfile` (move from infra/docker/)
3. `web-app/Dockerfile` (update from infra/docker/)
4. `backend/cloudbuild.yaml`
5. `scripts/dev.sh`
6. `scripts/deploy-staging.sh`
7. `scripts/deploy-prod.sh`

### Update:
1. `firebase.json` - Add API rewrites
2. `.github/workflows/dev.yml` - Fix paths, add frontend Docker
3. `.github/workflows/staging.yml` - Fix paths, add frontend Docker
4. `.github/workflows/production.yml` - Fix paths, add frontend Docker

## Implementation Plan

1. Move docker-compose.yml to root and add frontend service
2. Move Dockerfiles to correct locations
3. Update frontend Dockerfile for Next.js
4. Create cloudbuild.yaml
5. Update firebase.json with API rewrites
6. Fix GitHub Actions workflows
7. Create deployment scripts

