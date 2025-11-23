# ✅ Docker + Deployment Verification Checklist

## 🐳 Local Docker Development

### Prerequisites Check
- [ ] Docker/OrbStack is running
- [ ] `backend/.env` exists (copy from `env.example`)
- [ ] `web-app/.env.local` exists (copy from `env.example`)

### Start Services
```bash
./scripts/dev.sh
# or
docker-compose up
```

### Verify Services Running
- [ ] All 5 services show "Up" status: `docker-compose ps`
- [ ] Backend health check: `curl http://localhost:8000/health`
- [ ] Frontend loads: Open http://localhost:3000
- [ ] API docs load: Open http://localhost:8000/docs

### Test Hot Reload
- [ ] Edit `backend/api/routers/health.py` → Backend reloads
- [ ] Edit `web-app/src/app/page.tsx` → Frontend reloads
- [ ] Changes appear without restarting containers

### Test Internal Networking
```bash
# From host
curl http://localhost:8000/api/projects

# From frontend container (should use backend-api hostname)
docker-compose exec frontend sh -c "wget -qO- http://backend-api:8000/health"
```

## 🚀 Deployment Verification

### GitHub Secrets Setup
- [ ] `WIF_PROVIDER` - Workload Identity Provider
- [ ] `WIF_SERVICE_ACCOUNT` - Service Account Email  
- [ ] `FIREBASE_TOKEN` - Firebase CI token

**To get Firebase token:**
```bash
firebase login:ci
# Copy the token to GitHub Secrets
```

### Test Dev Deployment
```bash
git checkout -b dev
git push origin dev
```

**Verify:**
- [ ] GitHub Actions workflow runs successfully
- [ ] Backend deploys to Cloud Run (dev)
- [ ] Frontend deploys to Firebase Hosting (dev channel)
- [ ] Test dev URLs work

### Test Staging Deployment
```bash
git checkout -b staging
git push origin staging
```

**Verify:**
- [ ] Backend deploys to `cinefilm-backend-staging`
- [ ] Frontend deploys to staging channel
- [ ] Custom domain `staging.cinefilm.tech` works (if configured)

### Test Production Deployment
```bash
git checkout main
git merge staging
git push origin main
```

**Verify:**
- [ ] Backend deploys to `cinefilm-backend`
- [ ] Frontend deploys to production
- [ ] Custom domain `cinefilm.tech` works
- [ ] API rewrites work: `https://cinefilm.tech/api/projects`

## 🔍 Troubleshooting

### Services Won't Start
```bash
# Check Docker
docker info

# Check logs
docker-compose logs

# Rebuild
docker-compose build --no-cache
docker-compose up
```

### Frontend Can't Reach Backend
- Check `NEXT_PUBLIC_API_URL` in `web-app/.env.local`
- In Docker: Should be `http://backend-api:8000`
- Verify both services on same network: `docker network inspect cinefilm_cinefilm-network`

### Hot Reload Not Working
- Check volumes are mounted: `docker-compose config`
- Restart service: `docker-compose restart frontend`
- Check file permissions

### Deployment Fails
- Check GitHub Secrets are set
- Verify service account has correct permissions
- Check Cloud Build logs in GCP Console
- Verify Firebase token is valid

## 📊 Expected Results

### Local Development
✅ All services start without errors  
✅ Hot reload works for both frontend and backend  
✅ Frontend can call backend API  
✅ Database connections work  
✅ Logs are visible and helpful  

### Deployment
✅ GitHub Actions complete successfully  
✅ Cloud Run services are healthy  
✅ Firebase Hosting serves frontend  
✅ API rewrites work correctly  
✅ Custom domains resolve properly  

---

**Status**: Ready for testing! 🚀

