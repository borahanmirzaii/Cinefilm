# 🔧 Firebase Emulator Fix Guide

## Problem
Firebase Emulator container is failing with:
```
Error: download failed, status 403: Access denied.
We're sorry, but this service is not available in your location
```

## Quick Fix Options

### Option 1: Run Emulators Locally (Easiest) ⭐ RECOMMENDED

Instead of running emulators in Docker, run them on your host machine:

```bash
# 1. Install Firebase CLI (if not already installed)
npm install -g firebase-tools

# 2. Authenticate (if needed)
firebase login

# 3. Start emulators locally
firebase emulators:start --only auth,firestore,storage

# 4. Update docker-compose.yml to remove firebase-emulators service
#    OR comment it out and update backend/frontend to use localhost:9099
```

**Update docker-compose.yml**:
```yaml
backend-api:
  environment:
    # Change from firebase-emulators:9099 to localhost:9099
    - FIREBASE_AUTH_EMULATOR_HOST=localhost:9099
    - FIRESTORE_EMULATOR_HOST=localhost:8080
```

**Note**: You'll need to use `host.docker.internal` instead of `localhost` from inside Docker containers on some systems.

### Option 2: Fix Docker Container (Update Java Version)

Update `docker-compose.yml`:

```yaml
firebase-emulators:
  image: eclipse-temurin:21-jre-alpine  # Use Java 21 instead of node:22-alpine
  container_name: cinefilm-firebase-emulators
  ports:
    - "9099:9099"  # Auth
    - "8080:8080"  # Firestore
    - "9199:9199"  # Storage
    - "4000:4000"  # UI
  working_dir: /app
  command: >
    sh -c "
      apk add --no-cache nodejs npm &&
      npm install -g firebase-tools@latest &&
      firebase emulators:start --only auth,firestore,storage --project cinefilm-platform
    "
  volumes:
    - .:/app
    - firebase_emulator_data:/root/.cache/firebase/emulators
  environment:
    - FIREBASE_TOKEN=${FIREBASE_TOKEN:-}
  networks:
    - cinefilm-network
  restart: unless-stopped
```

### Option 3: Pre-download Emulator JAR

```bash
# 1. Run Firebase CLI locally to download emulators
firebase emulators:exec --only firestore "echo 'Downloading emulator'"

# 2. Copy downloaded emulator to Docker volume
# The emulator JAR will be in ~/.cache/firebase/emulators/
# Copy it to your project and mount it in docker-compose.yml
```

### Option 4: Use Host Network Mode (macOS/Linux)

```yaml
firebase-emulators:
  network_mode: host  # Use host network
  # ... rest of config
```

**Note**: This only works on Linux. On macOS/Windows, use `host.docker.internal`.

---

## Recommended Solution: Hybrid Approach

**Best approach**: Run Firebase emulators locally, keep everything else in Docker.

### Step-by-Step:

1. **Stop the failing container**:
   ```bash
   docker-compose stop firebase-emulators
   ```

2. **Start emulators locally** (in a separate terminal):
   ```bash
   firebase emulators:start --only auth,firestore,storage
   ```

3. **Update docker-compose.yml** to remove dependency on firebase-emulators:
   ```yaml
   backend-api:
     depends_on:
       - postgres
       - redis
       # Remove: - firebase-emulators
   
   frontend:
     depends_on:
       - backend-api
       # Remove: - firebase-emulators
   ```

4. **Update backend environment** to use host network:
   ```yaml
   backend-api:
     environment:
       # Use host.docker.internal (macOS/Windows) or host IP
       - FIREBASE_AUTH_EMULATOR_HOST=host.docker.internal:9099
       - FIRESTORE_EMULATOR_HOST=host.docker.internal:8080
   ```

5. **Update frontend** (already using localhost, which is correct):
   ```typescript
   // web-app/src/lib/firebase.ts
   // Already configured correctly:
   connectAuthEmulator(auth, "http://localhost:9099", ...)
   connectFirestoreEmulator(db, "localhost", 8080)
   ```

6. **Restart services**:
   ```bash
   docker-compose up -d
   ```

---

## Verification

After applying the fix:

1. **Check emulators are running**:
   ```bash
   # Should show emulators running
   firebase emulators:exec "echo 'Emulators running'"
   ```

2. **Check emulator UI**:
   ```bash
   open http://localhost:4000
   ```

3. **Test authentication**:
   - Go to http://localhost:3000/login
   - Try Google sign-in
   - Check browser console for emulator connection logs

4. **Check backend logs**:
   ```bash
   docker-compose logs backend-api | grep -i firebase
   # Should show: "Initializing Firebase Admin SDK with Auth Emulator"
   ```

---

## Alternative: Skip Emulators for Now

If you need to continue development without emulators:

1. **Use production Firebase** (with caution):
   - Remove emulator environment variables
   - Use real Firebase credentials
   - ⚠️ **Warning**: This will use production Firebase!

2. **Mock authentication** (for frontend-only development):
   - Create mock tokens
   - Skip backend auth temporarily
   - ⚠️ **Warning**: Not recommended for full-stack testing

---

## Troubleshooting

### Issue: "Cannot connect to emulator"
- **Check**: Emulators are running (`firebase emulators:start`)
- **Check**: Ports are not blocked
- **Check**: Firewall settings

### Issue: "host.docker.internal not found"
- **macOS/Windows**: Should work automatically
- **Linux**: Add to docker-compose.yml:
  ```yaml
  extra_hosts:
    - "host.docker.internal:host-gateway"
  ```

### Issue: "Emulator UI not accessible"
- **Check**: Port 4000 is not in use
- **Check**: Emulator UI is enabled in firebase.json

---

## Quick Test Script

```bash
#!/bin/bash
# test-emulators.sh

echo "Testing Firebase Emulators..."

# Check if emulators are running
if curl -s http://localhost:4000 > /dev/null; then
  echo "✅ Emulator UI accessible"
else
  echo "❌ Emulator UI not accessible - start emulators first"
  exit 1
fi

# Check Auth emulator
if curl -s http://localhost:9099 > /dev/null; then
  echo "✅ Auth emulator accessible"
else
  echo "❌ Auth emulator not accessible"
fi

# Check Firestore emulator
if curl -s http://localhost:8080 > /dev/null; then
  echo "✅ Firestore emulator accessible"
else
  echo "❌ Firestore emulator not accessible"
fi

echo ""
echo "If all checks pass, emulators are working correctly!"
```

---

**Recommended**: Use Option 1 (Run Emulators Locally) - it's the simplest and most reliable solution.

