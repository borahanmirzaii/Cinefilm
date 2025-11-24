#!/bin/bash
# Download Firebase emulators locally before starting Docker

set -e

echo "🔥 Downloading Firebase Emulators..."

# Ensure Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "Error: Firebase CLI not found. Install it with: npm install -g firebase-tools"
    exit 1
fi

# Create cache directory if it doesn't exist
CACHE_DIR="$HOME/.cache/firebase/emulators"
mkdir -p "$CACHE_DIR"

# Download emulators by running a dummy command
echo "Downloading Auth, Firestore, and Storage emulators..."
firebase emulators:exec --only auth,firestore,storage "echo 'Emulators downloaded'" || {
    echo "Warning: Some emulators may have failed to download due to geo-restrictions"
    echo "Trying to download Auth and Storage only..."
    firebase emulators:exec --only auth,storage "echo 'Auth and Storage emulators downloaded'" || {
        echo "Error: Failed to download emulators"
        exit 1
    }
}

echo "✅ Emulators downloaded to: $CACHE_DIR"
echo "You can now start Docker Compose and emulators will use cached versions"
