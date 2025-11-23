# Cinefilm Platform - Complete Setup Guide

This guide walks you through the complete setup process for Cinefilm Platform.

## Prerequisites Checklist

- [ ] Node.js 22+ installed
- [ ] Python 3.11+ installed
- [ ] uv installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- [ ] pnpm installed (`brew install pnpm`)
- [ ] Google Cloud SDK installed and authenticated
- [ ] Firebase CLI installed (`npm install -g firebase-tools`)
- [ ] Docker/OrbStack running
- [ ] GitHub repository access

## Phase 1: Clean Up Old Resources

Before starting fresh, clean up any old deployments:

```bash
./scripts/setup/clean-cloud.sh
```

Or manually:

```bash
gcloud run services delete backend-api --region=us-central1 --quiet
gcloud run services delete main-frontend --region=us-central1 --quiet
gcloud run jobs delete db-migration --region=us-central1 --quiet
```

## Phase 2: Verify Prerequisites

Run the preflight check:

```bash
./scripts/setup/preflight.sh
```

This will verify all required tools are installed and configured.

## Phase 3: Google Cloud Setup

### Enable Required APIs

```bash
gcloud config set project cinefilm-platform

gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com \
  cloudtasks.googleapis.com \
  secretmanager.googleapis.com \
  iamcredentials.googleapis.com \
  aiplatform.googleapis.com \
  generativelanguage.googleapis.com \
  drive.googleapis.com \
  gmail.googleapis.com \
  firebase.googleapis.com \
  firebasehosting.googleapis.com \
  firestore.googleapis.com \
  firebasestorage.googleapis.com
```

### Create Service Account

```bash
gcloud iam service-accounts create cinefilm-backend \
  --display-name="Cinefilm Backend Service Account" \
  --description="Service account for FastAPI backend on Cloud Run"

# Grant roles
gcloud projects add-iam-policy-binding cinefilm-platform \
  --member="serviceAccount:cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding cinefilm-platform \
  --member="serviceAccount:cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding cinefilm-platform \
  --member="serviceAccount:cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Download key for local development
gcloud iam service-accounts keys create ~/cinefilm-sa-key.json \
  --iam-account=cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com
```

⚠️ **Keep the service account key secure - never commit to git!**

### Create Secrets

```bash
# Stripe API Key
echo -n "sk_test_YOUR_STRIPE_KEY" | gcloud secrets create stripe-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Stripe Webhook Secret
echo -n "whsec_YOUR_WEBHOOK_SECRET" | gcloud secrets create stripe-webhook-secret \
  --data-file=- \
  --replication-policy="automatic"

# Google Drive OAuth
echo -n "YOUR_DRIVE_CLIENT_ID" | gcloud secrets create drive-client-id \
  --data-file=- \
  --replication-policy="automatic"

echo -n "YOUR_DRIVE_CLIENT_SECRET" | gcloud secrets create drive-client-secret \
  --data-file=- \
  --replication-policy="automatic"

# JWT Secret
openssl rand -base64 32 | gcloud secrets create jwt-secret \
  --data-file=- \
  --replication-policy="automatic"

# Grant access to service account
for secret in stripe-api-key stripe-webhook-secret drive-client-id drive-client-secret jwt-secret; do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done
```

## Phase 4: Firebase Configuration

### Authentication Setup

1. Go to [Firebase Console](https://console.firebase.google.com/project/cinefilm-platform/authentication/providers)
2. Enable GitHub provider:
   - Create OAuth App at https://github.com/settings/developers
   - Homepage URL: `https://cinefilm.tech`
   - Callback URL: `https://cinefilm-platform.firebaseapp.com/__/auth/handler`
   - Add Client ID and Secret to Firebase
3. Enable Email/Password provider
4. Add authorized domains:
   - `cinefilm.tech`
   - `*.cinefilm.tech`
   - `localhost`

### Firestore Database

1. Go to Firestore Database
2. Create database in Production mode
3. Location: `asia-east1` (Hong Kong)
4. Collections will be created automatically by the app

### Custom Domain

1. Go to Firebase Hosting
2. Click "Add custom domain"
3. Enter: `cinefilm.tech`
4. Follow verification steps (TXT record)
5. Add subdomains:
   - `app.cinefilm.tech` → Firebase Hosting
   - `api.cinefilm.tech` → Cloud Run backend
   - `staging.cinefilm.tech` → Staging environment

## Phase 5: Stripe Setup

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/test/products)
2. Create products:
   - **Cinefilm Basic** - $29/month
     - 10 AI generations/month
     - 5GB storage
   - **Cinefilm Pro** - $99/month
     - 100 AI generations/month
     - 50GB storage
     - Priority support
3. Copy Price IDs to `.env` files
4. Create webhook endpoint:
   - URL: `https://api.cinefilm.tech/webhooks/stripe`
   - Events: `checkout.session.completed`, `customer.subscription.*`, `invoice.*`
   - Copy webhook secret to Secret Manager

## Phase 6: Local Development Setup

### Backend

```bash
cd backend

# Install dependencies
uv sync

# Create .env file
cp .env.example .env
# Edit .env with your values

# Run development server
uv run uvicorn api.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
pnpm install

# Create .env.local file
cp env.example .env.local
# Edit .env.local with your values

# Run development server
pnpm dev
```

### Docker Services

```bash
# Start PostgreSQL, Redis, n8n
./scripts/setup/orbstack-start.sh
```

### Firebase Emulators

```bash
firebase emulators:start
```

## Phase 7: GitHub Actions Setup

1. Go to GitHub repository settings
2. Add secrets:
   - `WIF_PROVIDER`: Workload Identity Provider
   - `WIF_SERVICE_ACCOUNT`: Service Account Email

To create Workload Identity Pool:

```bash
gcloud iam workload-identity-pools create github-pool \
  --project=cinefilm-platform \
  --location=global \
  --display-name="GitHub Actions Pool"

gcloud iam workload-identity-pools providers create-oidc github-provider \
  --project=cinefilm-platform \
  --location=global \
  --workload-identity-pool=github-pool \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

## Phase 8: First Deployment

### Test Locally

```bash
# Backend
cd backend && uv run uvicorn api.main:app --reload
# Visit http://localhost:8000/docs

# Frontend
cd frontend && pnpm dev
# Visit http://localhost:3000
```

### Deploy to Staging

```bash
git checkout -b staging
git push origin staging
# GitHub Actions will deploy automatically
```

### Deploy to Production

```bash
git checkout main
git merge staging
git push origin main
# GitHub Actions will deploy automatically
```

## Troubleshooting

### Backend won't start

- Check `.env` file exists and has correct values
- Verify service account key path in `GOOGLE_APPLICATION_CREDENTIALS`
- Check Firebase Admin SDK initialization

### Frontend build fails

- Verify all environment variables are set
- Check Firebase config values
- Ensure Node.js 22 is being used

### Docker services not starting

- Check OrbStack is running: `orb status`
- Verify ports aren't already in use
- Check Docker logs: `docker-compose logs`

## Next Steps

- [ ] Implement authentication flow
- [ ] Set up usage tracking
- [ ] Configure Stripe webhooks
- [ ] Set up monitoring and alerts
- [ ] Write tests
- [ ] Deploy to staging

## Support

- Firebase Console: https://console.firebase.google.com/project/cinefilm-platform
- Google Cloud Console: https://console.cloud.google.com/home/dashboard?project=cinefilm-platform
- GitHub Actions: https://github.com/borahanmirzaii/Cinefilm/actions

