# Firebase Emulators Setup

## Status: ✅ Enabled

Firebase Emulators are now enabled in Docker Compose and configured for local development.

## Services Running

- **Auth Emulator**: Port `9099`
- **Firestore Emulator**: Port `8080`
- **Storage Emulator**: Port `9199`
- **Functions Emulator**: Port `5001`
- **Emulator UI**: Port `4000`

## Access Points

### Emulator UI
- **URL**: http://localhost:4000
- View all emulators, data, and logs in one place

### Individual Emulators
- **Auth**: http://localhost:9099
- **Firestore**: http://localhost:8080
- **Storage**: http://localhost:9199

## Configuration

### Backend Configuration

The backend automatically detects and uses emulators via environment variables:

```yaml
FIREBASE_AUTH_EMULATOR_HOST=http://firebase-emulators:9099
FIRESTORE_EMULATOR_HOST=firebase-emulators:8080
FIREBASE_STORAGE_EMULATOR_HOST=firebase-emulators:9199
```

### Frontend Configuration

The frontend connects to emulators when `NEXT_PUBLIC_USE_FIREBASE_EMULATOR=true`:

```typescript
// web-app/src/lib/firebase.ts
if (useEmulator && typeof window !== "undefined") {
  connectAuthEmulator(auth, "http://localhost:9099");
  connectFirestoreEmulator(db, "localhost", 8080);
  connectStorageEmulator(storage, "localhost", 9199);
}
```

## Starting Emulators

```bash
# Start all services including emulators
docker-compose up

# Or start just emulators
docker-compose up firebase-emulators
```

## Testing Emulators

### 1. Check Emulator UI
Open http://localhost:4000 to see the Firebase Emulator Suite UI.

### 2. Create Test User (via Emulator UI)
- Go to Authentication tab
- Click "Add user"
- Create a test user with email/password

### 3. Test Authentication Flow
1. Open frontend: http://localhost:3000
2. Try to sign in with test user
3. Check backend logs for authentication success

### 4. Test Firestore Operations
1. Create a project via frontend
2. Check Firestore tab in Emulator UI
3. Verify data appears in `projects` collection

## Data Persistence

Emulator data is stored in Docker volume `firebase_emulator_data` and persists between container restarts.

To reset emulator data:
```bash
docker-compose down -v firebase_emulator_data
```

## Troubleshooting

### Emulators Not Starting

1. **Check Java Installation**:
   ```bash
   docker-compose exec firebase-emulators java -version
   ```
   Should show Java 21

2. **Check Firebase Tools**:
   ```bash
   docker-compose exec firebase-emulators firebase --version
   ```

3. **Check Logs**:
   ```bash
   docker-compose logs firebase-emulators
   ```

### Backend Not Connecting to Emulators

1. **Verify Environment Variables**:
   ```bash
   docker-compose exec backend-api env | grep FIREBASE
   ```

2. **Check Network**:
   ```bash
   docker-compose exec backend-api ping firebase-emulators
   ```

### Frontend Not Connecting to Emulators

1. **Check Browser Console**: Should see "🔥 Connected to Firebase Emulators"
2. **Verify Environment Variable**: `NEXT_PUBLIC_USE_FIREBASE_EMULATOR=true`
3. **Check Network Tab**: Requests should go to `localhost:9099`, `localhost:8080`, etc.

## Production vs Development

- **Development**: Uses emulators automatically when `FIREBASE_AUTH_EMULATOR_HOST` is set
- **Production**: Uses production Firebase services (no emulators)

The backend automatically detects which mode to use based on environment variables.

