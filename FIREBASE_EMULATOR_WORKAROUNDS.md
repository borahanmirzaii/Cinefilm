# 🔧 Firebase Emulator Workarounds for Starlink/IP Blocking

## Problem
Google Cloud Storage is blocking downloads from Starlink IP addresses (common/shared IPs), causing:
```
Error: download failed, status 403: Access denied.
We're sorry, but this service is not available in your location
```

## Solutions (Ranked by Effectiveness)

---

## Solution 1: Tailscale VPN with UAE Mac Exit Node ⭐ RECOMMENDED

**Best for**: Reliable, persistent solution with your existing infrastructure

### Setup Steps

#### 1. Install Tailscale on UAE Mac
```bash
# On UAE Mac
brew install tailscale
sudo tailscale up
```

#### 2. Configure UAE Mac as Exit Node
```bash
# On UAE Mac - Enable as exit node
sudo tailscale up --advertise-exit-node

# Get the node name
tailscale status
```

#### 3. Connect Local Mac to Tailscale
```bash
# On your local Mac (Starlink)
brew install tailscale
sudo tailscale up

# Connect to UAE Mac exit node
sudo tailscale set --exit-node=<UAE-MAC-NODE-NAME>
```

#### 4. Verify Connection
```bash
# Check your IP
curl ifconfig.me
# Should show UAE IP, not Starlink IP

# Test Google Cloud Storage access
curl -I https://storage.googleapis.com/firebase-tools/...
```

#### 5. Download Emulators with Tailscale Active
```bash
# With Tailscale connected, download emulators
firebase emulators:exec --only firestore "echo 'Downloading'"

# This will download to: ~/.cache/firebase/emulators/
```

#### 6. Copy Emulators to Docker Volume
```bash
# Copy downloaded emulators to project
mkdir -p .firebase-emulators
cp -r ~/.cache/firebase/emulators/* .firebase-emulators/

# Update docker-compose.yml to use pre-downloaded emulators
```

#### 7. Update docker-compose.yml
```yaml
firebase-emulators:
  image: node:22-alpine
  container_name: cinefilm-firebase-emulators
  ports:
    - "9099:9099"  # Auth
    - "8080:8080"  # Firestore
    - "9199:9199"  # Storage
    - "4000:4000"  # UI
  working_dir: /app
  command: >
    sh -c "
      apk add --no-cache openjdk21-jre &&
      npm install -g firebase-tools@latest &&
      # Use pre-downloaded emulators
      export FIREBASE_EMULATOR_HUB_EMULATORS_DIR=/app/.firebase-emulators &&
      firebase emulators:start --only auth,firestore,storage --project cinefilm-platform
    "
  volumes:
    - .:/app
    - .firebase-emulators:/root/.cache/firebase/emulators  # Use pre-downloaded
  environment:
    - FIREBASE_TOKEN=${FIREBASE_TOKEN:-}
  networks:
    - cinefilm-network
  restart: unless-stopped
```

**Pros**:
- ✅ Uses your UAE Mac's IP (not blocked)
- ✅ Persistent solution
- ✅ Private network (secure)
- ✅ Can use for other Google services too

**Cons**:
- ⚠️ Requires UAE Mac to be online
- ⚠️ Slight latency increase

---

## Solution 2: Pre-download Emulators on UAE Mac

**Best for**: One-time setup, then share files

### Steps

#### 1. On UAE Mac (with good connectivity)
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Download all emulators
firebase emulators:exec --only auth,firestore,storage "echo 'Downloading'"

# This downloads to: ~/.cache/firebase/emulators/
ls -la ~/.cache/firebase/emulators/
```

#### 2. Package Emulators
```bash
# On UAE Mac - Create tarball
cd ~/.cache/firebase
tar -czf firebase-emulators.tar.gz emulators/

# Transfer to Starlink Mac (via scp, USB, cloud storage, etc.)
scp firebase-emulators.tar.gz user@starlink-mac:~/
```

#### 3. Extract on Starlink Mac
```bash
# On Starlink Mac
mkdir -p ~/.cache/firebase
tar -xzf firebase-emulators.tar.gz -C ~/.cache/firebase/

# Or extract to project directory
mkdir -p .firebase-emulators
tar -xzf firebase-emulators.tar.gz -C .firebase-emulators/
```

#### 4. Use Pre-downloaded Emulators
```yaml
# docker-compose.yml
firebase-emulators:
  volumes:
    - .firebase-emulators:/root/.cache/firebase/emulators
```

**Pros**:
- ✅ No network needed after initial download
- ✅ Works offline
- ✅ Fast startup

**Cons**:
- ⚠️ Need to update manually when emulators update
- ⚠️ Requires file transfer

---

## Solution 3: Custom Docker Image with Pre-downloaded Emulators

**Best for**: Team sharing, CI/CD

### Steps

#### 1. Create Dockerfile for Firebase Emulators
```dockerfile
# Dockerfile.firebase-emulators
FROM node:22-alpine

# Install Java 21
RUN apk add --no-cache openjdk21-jre

# Install Firebase CLI
RUN npm install -g firebase-tools@latest

# Copy pre-downloaded emulators (downloaded on UAE Mac)
COPY firebase-emulators/ /root/.cache/firebase/emulators/

WORKDIR /app

# Expose emulator ports
EXPOSE 9099 8080 9199 4000

CMD ["firebase", "emulators:start", "--only", "auth,firestore,storage", "--project", "cinefilm-platform"]
```

#### 2. Build Image (on UAE Mac or with Tailscale)
```bash
# Download emulators first (on UAE Mac or with Tailscale)
firebase emulators:exec --only firestore "echo 'Downloading'"

# Copy emulators to project
cp -r ~/.cache/firebase/emulators ./firebase-emulators/

# Build Docker image
docker build -f Dockerfile.firebase-emulators -t cinefilm-firebase-emulators:latest .
```

#### 3. Update docker-compose.yml
```yaml
firebase-emulators:
  image: cinefilm-firebase-emulators:latest
  container_name: cinefilm-firebase-emulators
  ports:
    - "9099:9099"
    - "8080:8080"
    - "9199:9199"
    - "4000:4000"
  volumes:
    - .:/app
  networks:
    - cinefilm-network
  restart: unless-stopped
```

**Pros**:
- ✅ Self-contained
- ✅ Shareable with team
- ✅ Version controlled (if you commit image)

**Cons**:
- ⚠️ Large Docker image (~500MB+)
- ⚠️ Need to rebuild when emulators update

---

## Solution 4: Run Emulators Locally (Bypass Docker)

**Best for**: Quick development, simplest setup

### Steps

#### 1. Install Firebase CLI Locally
```bash
npm install -g firebase-tools
```

#### 2. Download Emulators (with Tailscale or VPN)
```bash
# Connect Tailscale first
sudo tailscale set --exit-node=<UAE-MAC>

# Then download
firebase emulators:exec --only firestore "echo 'Downloading'"
```

#### 3. Start Emulators Locally
```bash
# In separate terminal
firebase emulators:start --only auth,firestore,storage
```

#### 4. Update docker-compose.yml
```yaml
# Remove firebase-emulators service
# Update backend to use host.docker.internal

backend-api:
  environment:
    - FIREBASE_AUTH_EMULATOR_HOST=host.docker.internal:9099
    - FIRESTORE_EMULATOR_HOST=host.docker.internal:8080
  depends_on:
    - postgres
    - redis
    # Remove: - firebase-emulators
```

#### 5. Add Extra Hosts (Linux)
```yaml
backend-api:
  extra_hosts:
    - "host.docker.internal:host-gateway"
```

**Pros**:
- ✅ Simplest setup
- ✅ No Docker networking issues
- ✅ Easy to debug

**Cons**:
- ⚠️ Requires manual start
- ⚠️ Not containerized

---

## Solution 5: Use HTTP Proxy

**Best for**: Temporary workaround

### Steps

#### 1. Set Up Proxy (UAE Mac or VPN)
```bash
# On UAE Mac - Set up proxy (if available)
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
```

#### 2. Configure Docker to Use Proxy
```yaml
firebase-emulators:
  environment:
    - HTTP_PROXY=http://host.docker.internal:3128
    - HTTPS_PROXY=http://host.docker.internal:3128
```

**Pros**:
- ✅ Can use existing proxy infrastructure

**Cons**:
- ⚠️ Requires proxy setup
- ⚠️ More complex

---

## Solution 6: Mobile Hotspot (Temporary)

**Best for**: Quick test, one-time download

### Steps
1. Connect Mac to mobile hotspot (different IP)
2. Download emulators
3. Switch back to Starlink
4. Use pre-downloaded emulators

**Pros**:
- ✅ Quick solution
- ✅ No infrastructure needed

**Cons**:
- ⚠️ Temporary
- ⚠️ Data usage

---

## Recommended Approach: Hybrid Solution

**Best of both worlds**: Use Tailscale for downloads, pre-download for reliability

### Complete Setup

#### 1. Initial Setup (One-time, with Tailscale)
```bash
# Connect Tailscale
sudo tailscale set --exit-node=<UAE-MAC>

# Download emulators
firebase emulators:exec --only auth,firestore,storage "echo 'Downloading'"

# Copy to project
mkdir -p .firebase-emulators
cp -r ~/.cache/firebase/emulators/* .firebase-emulators/
```

#### 2. Create Startup Script
```bash
#!/bin/bash
# scripts/start-emulators.sh

# Check if emulators are downloaded
if [ ! -d ".firebase-emulators" ] || [ -z "$(ls -A .firebase-emulators)" ]; then
  echo "⚠️  Emulators not found. Downloading..."
  
  # Try with Tailscale first
  if tailscale status > /dev/null 2>&1; then
    echo "✅ Tailscale connected, downloading..."
    firebase emulators:exec --only firestore "echo 'Downloading'"
    cp -r ~/.cache/firebase/emulators/* .firebase-emulators/
  else
    echo "❌ Tailscale not connected. Please connect first or use pre-downloaded emulators."
    exit 1
  fi
fi

# Start emulators (using pre-downloaded)
firebase emulators:start --only auth,firestore,storage
```

#### 3. Update docker-compose.yml
```yaml
firebase-emulators:
  image: node:22-alpine
  container_name: cinefilm-firebase-emulators
  ports:
    - "9099:9099"
    - "8080:8080"
    - "9199:9199"
    - "4000:4000"
  working_dir: /app
  command: >
    sh -c "
      apk add --no-cache openjdk21-jre &&
      npm install -g firebase-tools@latest &&
      firebase emulators:start --only auth,firestore,storage --project cinefilm-platform
    "
  volumes:
    - .:/app
    - .firebase-emulators:/root/.cache/firebase/emulators  # Pre-downloaded
  environment:
    - FIREBASE_TOKEN=${FIREBASE_TOKEN:-}
  networks:
    - cinefilm-network
  restart: unless-stopped
```

#### 4. Add to .gitignore
```gitignore
# Firebase emulators (large files, download separately)
.firebase-emulators/
firebase-emulators/
```

#### 5. Create Download Script
```bash
#!/bin/bash
# scripts/download-emulators.sh

echo "🔽 Downloading Firebase Emulators..."

# Check Tailscale
if ! tailscale status > /dev/null 2>&1; then
  echo "⚠️  Tailscale not connected. Connecting..."
  echo "Please run: sudo tailscale set --exit-node=<UAE-MAC>"
  read -p "Press enter after connecting Tailscale..."
fi

# Download
firebase emulators:exec --only auth,firestore,storage "echo 'Downloading'"

# Copy to project
mkdir -p .firebase-emulators
cp -r ~/.cache/firebase/emulators/* .firebase-emulators/

echo "✅ Emulators downloaded to .firebase-emulators/"
echo "You can now start Docker services without network issues."
```

---

## Testing & Verification

### Test Emulator Download
```bash
# With Tailscale connected
firebase emulators:exec --only firestore "echo 'Test'"
# Should download successfully
```

### Test Docker Setup
```bash
# Start services
docker-compose up -d firebase-emulators

# Check logs
docker-compose logs firebase-emulators

# Should see: "All emulators ready!"
```

### Test Emulator UI
```bash
open http://localhost:4000
# Should show Firebase Emulator Suite
```

---

## Troubleshooting

### Issue: Tailscale not routing correctly
```bash
# Check exit node
tailscale status

# Verify IP
curl ifconfig.me
# Should show UAE IP

# Test Google access
curl -I https://storage.googleapis.com
```

### Issue: Emulators still downloading in Docker
```bash
# Check volume mount
docker-compose exec firebase-emulators ls -la /root/.cache/firebase/emulators/

# Should show emulator files, not empty
```

### Issue: Permission errors
```bash
# Fix permissions
chmod -R 755 .firebase-emulators
```

---

## Summary

**Recommended Solution**: **Solution 1 (Tailscale) + Pre-download**

1. ✅ Use Tailscale with UAE Mac exit node for downloads
2. ✅ Pre-download emulators once
3. ✅ Use pre-downloaded emulators in Docker
4. ✅ Works offline after initial download
5. ✅ Reliable and repeatable

This gives you:
- **Reliability**: Pre-downloaded emulators work offline
- **Flexibility**: Can update via Tailscale when needed
- **Confidence**: Same setup for local dev and deployment testing
- **Team sharing**: Can share pre-downloaded emulators with team

---

**Next Steps**:
1. Set up Tailscale with UAE Mac exit node
2. Download emulators once
3. Update docker-compose.yml to use pre-downloaded emulators
4. Test locally
5. Deploy with confidence! 🚀

