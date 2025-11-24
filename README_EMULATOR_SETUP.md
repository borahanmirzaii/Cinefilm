# 🔥 Firebase Emulator Setup Guide

## Problem
Google Cloud Storage blocks downloads from Starlink IP addresses, preventing Firebase emulator downloads.

## Solution: Tailscale + Pre-downloaded Emulators

We use **Tailscale VPN** with your **UAE Mac as exit node** to download emulators, then use pre-downloaded emulators in Docker.

---

## Quick Start

### 1. Setup Tailscale (One-time)

```bash
# Install Tailscale (if not already installed)
brew install tailscale

# Run setup script
./scripts/setup/setup-tailscale.sh
```

This will:
- Check Tailscale installation
- Help you connect to UAE Mac exit node
- Verify IP change
- Test Google Cloud Storage access

### 2. Download Emulators (One-time)

```bash
# With Tailscale connected, download emulators
./scripts/setup/download-emulators.sh
```

This will:
- Verify Tailscale connection
- Download Firebase emulators through UAE Mac IP
- Copy emulators to `.firebase-emulators/` directory
- Verify download success

### 3. Start Docker Services

```bash
# Start all services (emulators will use pre-downloaded files)
docker-compose up -d

# Check emulator logs
docker-compose logs -f firebase-emulators
```

---

## Manual Setup

### Step 1: Setup Tailscale Exit Node

#### On UAE Mac:
```bash
# Install Tailscale
brew install tailscale

# Start Tailscale
sudo tailscale up

# Enable as exit node
sudo tailscale up --advertise-exit-node

# Get node name
tailscale status
# Note the node name (e.g., "uae-mac")
```

#### On Local Mac (Starlink):
```bash
# Install Tailscale
brew install tailscale

# Start Tailscale
sudo tailscale up

# Connect to UAE Mac exit node
sudo tailscale set --exit-node=<UAE-MAC-NODE-NAME>

# Verify IP changed
curl ifconfig.me
# Should show UAE IP, not Starlink IP
```

### Step 2: Download Emulators

```bash
# Install Firebase CLI (if needed)
npm install -g firebase-tools@latest

# Login to Firebase
firebase login

# Download emulators (will use UAE Mac IP via Tailscale)
firebase emulators:exec --only auth,firestore,storage "echo 'Downloading'"

# Copy to project directory
mkdir -p .firebase-emulators
cp -r ~/.cache/firebase/emulators/* .firebase-emulators/
```

### Step 3: Start Services

```bash
# Start Docker services
docker-compose up -d

# Verify emulators are running
docker-compose logs firebase-emulators
# Should see: "All emulators ready!"

# Access Emulator UI
open http://localhost:4000
```

---

## How It Works

1. **Tailscale VPN**: Routes traffic through UAE Mac (non-blocked IP)
2. **Pre-download**: Emulators downloaded once via Tailscale
3. **Docker Volume**: Pre-downloaded emulators mounted in Docker container
4. **Offline Use**: Works without network after initial download

---

## Troubleshooting

### Issue: Tailscale not connecting

```bash
# Check Tailscale status
tailscale status

# Restart Tailscale
sudo tailscale down
sudo tailscale up

# Check exit node
tailscale status | grep "exit node"
```

### Issue: Emulators not downloading

```bash
# Verify IP changed
curl ifconfig.me

# Test Google Cloud Storage
curl -I https://storage.googleapis.com

# Check Tailscale exit node is active
tailscale status
```

### Issue: Docker can't find emulators

```bash
# Check emulators directory exists
ls -la .firebase-emulators/

# Check Docker volume mount
docker-compose exec firebase-emulators ls -la /root/.cache/firebase/emulators/

# Re-download if needed
./scripts/setup/download-emulators.sh
```

### Issue: Emulator container keeps restarting

```bash
# Check logs
docker-compose logs firebase-emulators

# Common issues:
# - Java version mismatch (should be Java 21)
# - Missing emulator files
# - Port conflicts
```

---

## Updating Emulators

When Firebase updates emulators:

```bash
# 1. Connect Tailscale
sudo tailscale set --exit-node=<UAE-MAC-NODE>

# 2. Re-download
./scripts/setup/download-emulators.sh

# 3. Restart Docker
docker-compose restart firebase-emulators
```

---

## Alternative: Run Emulators Locally

If Docker continues to have issues:

```bash
# Start emulators locally (uses pre-downloaded)
firebase emulators:start --only auth,firestore,storage

# Update docker-compose.yml to use host.docker.internal
# See FIREBASE_EMULATOR_WORKAROUNDS.md for details
```

---

## Files Created

- `.firebase-emulators/` - Pre-downloaded emulator files (gitignored)
- `scripts/setup/download-emulators.sh` - Download script
- `scripts/setup/setup-tailscale.sh` - Tailscale setup script

---

## Benefits

✅ **Reliable**: Works offline after initial download  
✅ **Fast**: No download delays in Docker  
✅ **Private**: Uses your own Tailscale network  
✅ **Confident**: Same setup for local dev and deployment testing  

---

## Next Steps

1. ✅ Setup Tailscale with UAE Mac exit node
2. ✅ Download emulators once
3. ✅ Start Docker services
4. ✅ Test authentication flow
5. ✅ Deploy with confidence! 🚀

