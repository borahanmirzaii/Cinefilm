# Firebase Emulator Setup for Local Development

## Problem

Previously, the local Docker setup was calling production Firebase Auth (`https://cinefilm-platform.firebaseapp.com/__/auth/handler`) instead of using the Firebase Auth Emulator. This caused authentication to fail and redirect to production URLs.

## Solution

We've configured the application to use Firebase Emulators for local development:

### 1. Firebase Emulator Service

Added `firebase-emulators` service to `docker-compose.yml` that runs:
- **Auth Emulator**: Port 9099
- **Firestore Emulator**: Port 8080  
- **Storage Emulator**: Port 9199
- **Emulator UI**: Port 4000

### 2. Frontend Configuration

Updated `web-app/src/lib/firebase.ts` to:
- Check for `NEXT_PUBLIC_USE_FIREBASE_EMULATOR=true` environment variable
- Connect to emulators when enabled:
  - Auth: `http://localhost:9099`
  - Firestore: `localhost:8080`
  - Storage: `localhost:9199`

### 3. Backend Configuration

Updated `docker-compose.yml` to set:
- `FIREBASE_AUTH_EMULATOR_HOST=firebase-emulators:9099`
- `FIRESTORE_EMULATOR_HOST=firebase-emulators:8080`

This tells Firebase Admin SDK to use emulators instead of production.

## Usage

### Start Everything (Including Emulators)

```bash
docker-compose up
```

This will start:
- Backend API (port 8000)
- Frontend (port 3000)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Firebase Emulators (ports 9099, 8080, 9199, 4000)
- n8n (port 5678)

### Access Emulator UI

Open http://localhost:4000 to see the Firebase Emulator Suite UI where you can:
- View Auth users
- View Firestore data
- View Storage files
- Test authentication flows

### Create Test Users

You can create test users directly in the Emulator UI or programmatically:

```typescript
// In your frontend code
import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from "@/lib/firebase";

// This will create a user in the emulator, not production
await createUserWithEmailAndPassword(auth, "test@example.com", "password123");
```

## Environment Variables

### Frontend (.env.local)

```env
NEXT_PUBLIC_USE_FIREBASE_EMULATOR=true
NEXT_PUBLIC_FIREBASE_PROJECT_ID=cinefilm-platform
# Other Firebase config vars are optional when using emulators
```

### Backend (.env)

The backend automatically uses emulators when `FIREBASE_AUTH_EMULATOR_HOST` is set (done via docker-compose.yml).

## Troubleshooting

### Emulator Not Starting

If the Firebase Emulator service fails to start:

1. **Check Firebase CLI authentication:**
   ```bash
   docker-compose exec firebase-emulators firebase login:ci
   ```
   Then set `FIREBASE_TOKEN` in your environment or `.env` file.

2. **Check logs:**
   ```bash
   docker-compose logs firebase-emulators
   ```

3. **Verify firebase.json exists:**
   The emulator needs `firebase.json` in the project root.

### Still Connecting to Production

1. **Verify environment variable:**
   ```bash
   docker-compose exec frontend printenv | grep FIREBASE
   ```
   Should show `NEXT_PUBLIC_USE_FIREBASE_EMULATOR=true`

2. **Check browser console:**
   Should see: `🔥 Connected to Firebase Emulators`

3. **Hard refresh browser:**
   Clear cache and reload (Cmd+Shift+R / Ctrl+Shift+R)

### Backend Still Using Production

1. **Check backend environment:**
   ```bash
   docker-compose exec backend-api printenv | grep FIREBASE
   ```
   Should show `FIREBASE_AUTH_EMULATOR_HOST=firebase-emulators:9099`

2. **Restart backend:**
   ```bash
   docker-compose restart backend-api
   ```

## Production vs Development

- **Development (Docker)**: Uses Firebase Emulators
- **Production**: Uses real Firebase services

The environment variable `NEXT_PUBLIC_USE_FIREBASE_EMULATOR` controls this behavior. It's set to `true` in `docker-compose.yml` for local development.

## Benefits

✅ **No production data pollution** - Test users don't affect production  
✅ **Faster development** - No network calls to Firebase  
✅ **Free** - No Firebase usage costs during development  
✅ **Offline development** - Works without internet  
✅ **Easy testing** - Reset emulator data anytime  

