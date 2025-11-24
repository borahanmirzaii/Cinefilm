# ⚠️ Firebase Emulators - Temporarily Disabled

## Status
Firebase emulators have been **disabled** in `docker-compose.yml` to prevent unlimited download attempts that were failing due to IP blocking.

## Current Setup
- ✅ Firebase emulators service **commented out** in `docker-compose.yml`
- ✅ Backend/Frontend dependencies **removed** (won't wait for emulators)
- ✅ Container **stopped and removed**

## Running Services
All other services are running normally:
- ✅ Backend API (port 8000)
- ✅ Frontend (port 3000)
- ✅ PostgreSQL (port 5432)
- ✅ Redis (port 6379)
- ✅ n8n (port 5678)

## To Re-enable Emulators

### Option 1: Download Emulators First (Recommended)
```bash
# 1. Setup Tailscale with UAE Mac exit node
./scripts/setup/setup-tailscale.sh

# 2. Download emulators
./scripts/setup/download-emulators.sh

# 3. Uncomment firebase-emulators service in docker-compose.yml

# 4. Start services
docker-compose up -d
```

### Option 2: Run Emulators Locally
```bash
# Start emulators locally (outside Docker)
firebase emulators:start --only auth,firestore,storage

# Update backend environment to use localhost:
# FIREBASE_AUTH_EMULATOR_HOST=localhost:9099
# FIRESTORE_EMULATOR_HOST=localhost:8080
```

## Impact
- ⚠️ **Authentication won't work** without emulators (or production Firebase)
- ⚠️ **Firestore operations won't work** without emulators
- ✅ **Backend/Frontend still run** - just can't use Firebase features

## Next Steps
When ready to use Firebase locally:
1. Follow the Tailscale setup guide
2. Download emulators once
3. Re-enable the service in docker-compose.yml

See `README_EMULATOR_SETUP.md` for complete instructions.

