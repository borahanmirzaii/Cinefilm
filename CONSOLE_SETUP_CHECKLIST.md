# 🎯 Console Setup Checklist

Complete guide for configuring Google Cloud Console, Firebase Console, and GitHub Repository.

---

## 🔵 Google Cloud Console

### 1. Enable Required APIs
**URL**: https://console.cloud.google.com/apis/library?project=cinefilm-platform

Enable these APIs:
- ✅ Cloud Run API (`run.googleapis.com`)
- ✅ Cloud Build API (`cloudbuild.googleapis.com`)
- ✅ Container Registry API (`containerregistry.googleapis.com`)
- ✅ Artifact Registry API (`artifactregistry.googleapis.com`)
- ✅ Secret Manager API (`secretmanager.googleapis.com`)
- ✅ Cloud Scheduler API (`cloudscheduler.googleapis.com`)
- ✅ Cloud Tasks API (`cloudtasks.googleapis.com`)
- ✅ IAM Credentials API (`iamcredentials.googleapis.com`)
- ✅ Vertex AI Platform API (`aiplatform.googleapis.com`)
- ✅ Generative Language API (`generativelanguage.googleapis.com`)
- ✅ Google Drive API (`drive.googleapis.com`)
- ✅ Gmail API (`gmail.googleapis.com`)
- ✅ Firebase API (`firebase.googleapis.com`)
- ✅ Firebase Hosting API (`firebasehosting.googleapis.com`)
- ✅ Firestore API (`firestore.googleapis.com`)
- ✅ Firebase Storage API (`firebasestorage.googleapis.com`)

**Quick Command**:
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

### 2. Create Service Account
**URL**: https://console.cloud.google.com/iam-admin/serviceaccounts?project=cinefilm-platform

1. Click **"Create Service Account"**
2. Name: `cinefilm-backend`
3. Description: "Service account for FastAPI backend on Cloud Run"
4. Grant these roles:
   - `Cloud Run Invoker`
   - `Secret Manager Secret Accessor`
   - `Storage Object Admin` (for Firebase Storage)
   - `Firebase Admin SDK Administrator Service Agent`
   - `Vertex AI User` (for AI features)
   - `Service Account User`

**Quick Command**:
```bash
gcloud iam service-accounts create cinefilm-backend \
  --display-name="Cinefilm Backend Service Account" \
  --description="Service account for FastAPI backend on Cloud Run"

# Grant roles
gcloud projects add-iam-policy-binding cinefilm-platform \
  --member="serviceAccount:cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

gcloud projects add-iam-policy-binding cinefilm-platform \
  --member="serviceAccount:cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding cinefilm-platform \
  --member="serviceAccount:cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding cinefilm-platform \
  --member="serviceAccount:cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com" \
  --role="roles/firebase.adminsdkAdminServiceAgent"

gcloud projects add-iam-policy-binding cinefilm-platform \
  --member="serviceAccount:cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### 3. Create Service Account Key
**URL**: https://console.cloud.google.com/iam-admin/serviceaccounts?project=cinefilm-platform

1. Click on `cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com`
2. Go to **"Keys"** tab
3. Click **"Add Key"** → **"Create new key"**
4. Choose **JSON** format
5. Download and save securely (DO NOT commit to git!)
6. Save path: `backend/service-account-key.json` (add to `.gitignore`)

**Quick Command**:
```bash
gcloud iam service-accounts keys create backend/service-account-key.json \
  --iam-account=cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com
```

### 4. Create Secrets in Secret Manager
**URL**: https://console.cloud.google.com/security/secret-manager?project=cinefilm-platform

Create these secrets:

1. **`stripe-api-key`**
   - Value: Your Stripe secret key (starts with `sk_test_` or `sk_live_`)
   - Location: https://dashboard.stripe.com/apikeys

2. **`stripe-webhook-secret`**
   - Value: Your Stripe webhook signing secret
   - Create webhook first in Stripe Dashboard → Webhooks

3. **`google-application-credentials`**
   - Value: Contents of `backend/service-account-key.json` (copy entire JSON)
   - Or use: `gcloud secrets create google-application-credentials --data-file=backend/service-account-key.json`

4. **`jwt-secret`** (optional, for custom JWT)
   - Value: Random secure string (32+ characters)

**Quick Commands**:
```bash
# Stripe API Key
echo -n "sk_test_..." | gcloud secrets create stripe-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Stripe Webhook Secret
echo -n "whsec_..." | gcloud secrets create stripe-webhook-secret \
  --data-file=- \
  --replication-policy="automatic"

# Google Application Credentials
gcloud secrets create google-application-credentials \
  --data-file=backend/service-account-key.json \
  --replication-policy="automatic"

# JWT Secret (generate random)
openssl rand -base64 32 | gcloud secrets create jwt-secret \
  --data-file=- \
  --replication-policy="automatic"
```

### 5. Set Up Workload Identity Federation (for GitHub Actions)
**URL**: https://console.cloud.google.com/iam-admin/workload-identity-federation?project=cinefilm-platform

1. Go to **Workload Identity Federation**
2. Click **"Create Pool"**
3. Pool ID: `github-actions-pool`
4. Display name: "GitHub Actions Pool"
5. Click **"Continue"**
6. Click **"Add Provider"**
7. Provider: **OpenID Connect (OIDC)**
8. Provider name: `github-provider`
9. Issuer URL: `https://token.actions.githubusercontent.com`
10. Click **"Continue"**
11. Add attribute mapping:
    - `google.subject` = `assertion.sub`
    - `attribute.repository` = `assertion.repository`
    - `attribute.ref` = `assertion.ref`
12. Click **"Save"**
13. Grant access:
    - Principal: `principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/borahanmirzaii/Cinefilm`
    - Role: `roles/iam.workloadIdentityUser`
    - Service Account: `cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com`

**Quick Commands**:
```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe cinefilm-platform --format="value(projectNumber)")

# Create workload identity pool
gcloud iam workload-identity-pools create github-actions-pool \
  --project=cinefilm-platform \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Create provider
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --project=cinefilm-platform \
  --location="global" \
  --workload-identity-pool="github-actions-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Grant access
gcloud iam service-accounts add-iam-policy-binding \
  cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com \
  --project=cinefilm-platform \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/borahanmirzaii/Cinefilm"
```

### 6. Clean Up Old Cloud Run Services (Optional)
**URL**: https://console.cloud.google.com/run?project=cinefilm-platform

Delete old services if they exist:
- `backend-api`
- `main-frontend`
- `db-migration` (Cloud Run Job)

**Quick Command**:
```bash
./scripts/setup/clean-cloud.sh
```

---

## 🔴 Firebase Console

### 1. Verify Project Access
**URL**: https://console.firebase.google.com/project/cinefilm-platform

- ✅ Project: `cinefilm-platform`
- ✅ Project Number: `422357752899`

### 2. Enable Authentication Providers
**URL**: https://console.firebase.google.com/project/cinefilm-platform/authentication/providers

Enable these sign-in methods:

1. **Email/Password**
   - Click **"Email/Password"**
   - Enable **"Email/Password"**
   - Enable **"Email link (passwordless sign-in)"** (optional)
   - Click **"Save"**

2. **GitHub**
   - Click **"GitHub"**
   - Enable provider
   - **Client ID**: Get from GitHub → Settings → Developer settings → OAuth Apps
   - **Client Secret**: Get from same location
   - **Authorized redirect URIs**: 
     - `https://cinefilm-platform.firebaseapp.com/__/auth/handler`
     - `https://cinefilm.tech/__/auth/handler` (after custom domain setup)
   - Click **"Save"**

**GitHub OAuth App Setup**:
1. Go to: https://github.com/settings/developers
2. Click **"New OAuth App"**
3. Application name: `Cinefilm Platform`
4. Homepage URL: `https://cinefilm.tech`
5. Authorization callback URL: `https://cinefilm-platform.firebaseapp.com/__/auth/handler`
6. Click **"Register application"**
7. Copy **Client ID** and generate **Client Secret**

### 3. Configure Firestore Database
**URL**: https://console.firebase.google.com/project/cinefilm-platform/firestore

1. Click **"Create database"** (if not exists)
2. Choose **"Start in production mode"**
3. Select location: **`asia-east1`** (or your preferred region)
4. Click **"Enable"**
5. Create collections:
   - `users` (auto-created by Firebase Auth)
   - `projects`
   - `usage`
   - `quotas`
   - `subscriptions`

### 4. Configure Storage
**URL**: https://console.firebase.google.com/project/cinefilm-platform/storage

1. Click **"Get started"** (if not initialized)
2. Start in **production mode**
3. Location: **`asia-east1`** (match Firestore)
4. Click **"Done"**
5. Create folders:
   - `users/{userId}/assets/`
   - `projects/{projectId}/assets/`
   - `public/`

### 5. Set Up Firebase Hosting
**URL**: https://console.firebase.google.com/project/cinefilm-platform/hosting

1. Click **"Get started"** (if not initialized)
2. Connect custom domain:
   - **Production**: `cinefilm.tech`
   - **Staging**: `staging.cinefilm.tech` (optional)
3. Add DNS records as instructed:
   - A record: `@` → Firebase IP
   - A record: `staging` → Firebase IP (if using staging)
   - CNAME record: `www` → `cinefilm.tech`

### 6. Configure Firebase Hosting Channels
**URL**: https://console.firebase.google.com/project/cinefilm-platform/hosting/channels

1. Create **staging** channel:
   - Channel ID: `staging`
   - Branch: `staging` (GitHub branch)
2. Production channel is **live** by default

### 7. Get Firebase CI Token
**URL**: https://console.firebase.google.com/project/cinefilm-platform/settings/serviceaccounts/adminsdk

1. Click **"Generate new private key"**
2. Download JSON file (keep secure, DO NOT commit)
3. Or use CLI:
   ```bash
   firebase login:ci
   ```
   Copy the token (needed for GitHub Actions)

---

## 🟢 GitHub Repository

### 1. Repository Settings
**URL**: https://github.com/borahanmirzaii/Cinefilm/settings

### 2. Add Secrets for GitHub Actions
**URL**: https://github.com/borahanmirzaii/Cinefilm/settings/secrets/actions

Add these secrets:

1. **`WIF_PROVIDER`**
   - Value: `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider`
   - Get PROJECT_NUMBER: `gcloud projects describe cinefilm-platform --format="value(projectNumber)"`

2. **`WIF_SERVICE_ACCOUNT`**
   - Value: `cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com`

3. **`FIREBASE_TOKEN`**
   - Value: Token from `firebase login:ci`
   - Or get from: Firebase Console → Project Settings → Service Accounts → Generate new private key

4. **`GCP_PROJECT_ID`** (optional, can be hardcoded)
   - Value: `cinefilm-platform`

**Quick Commands**:
```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe cinefilm-platform --format="value(projectNumber)")

# Get Firebase token
firebase login:ci

# Then add to GitHub Secrets manually via web UI
```

### 3. Configure Branch Protection (Optional)
**URL**: https://github.com/borahanmirzaii/Cinefilm/settings/branches

Protect these branches:
- `main` (production)
- `staging` (staging)

Settings:
- ✅ Require pull request reviews
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Include administrators

### 4. Push Workflow Files
The workflow files are already committed locally. Push them:

```bash
# If you have a token with workflow scope:
git push origin main

# Or add workflows manually via GitHub UI:
# 1. Go to: https://github.com/borahanmirzaii/Cinefilm/tree/main/.github/workflows
# 2. Create each file manually if push fails
```

### 5. Verify GitHub Actions
**URL**: https://github.com/borahanmirzaii/Cinefilm/actions

After pushing, workflows should appear:
- ✅ `.github/workflows/dev.yml`
- ✅ `.github/workflows/staging.yml`
- ✅ `.github/workflows/production.yml`

---

## ✅ Verification Checklist

### Google Cloud Console
- [ ] All APIs enabled
- [ ] Service account created (`cinefilm-backend`)
- [ ] Service account has correct IAM roles
- [ ] Service account key downloaded
- [ ] Secrets created in Secret Manager:
  - [ ] `stripe-api-key`
  - [ ] `stripe-webhook-secret`
  - [ ] `google-application-credentials`
  - [ ] `jwt-secret` (optional)
- [ ] Workload Identity Federation configured
- [ ] Old Cloud Run services cleaned up (optional)

### Firebase Console
- [ ] Authentication enabled:
  - [ ] Email/Password
  - [ ] GitHub OAuth
- [ ] Firestore database created (`asia-east1`)
- [ ] Storage initialized (`asia-east1`)
- [ ] Firebase Hosting configured
- [ ] Custom domains added:
  - [ ] `cinefilm.tech` (production)
  - [ ] `staging.cinefilm.tech` (staging, optional)
- [ ] Firebase CI token obtained

### GitHub Repository
- [ ] Secrets added:
  - [ ] `WIF_PROVIDER`
  - [ ] `WIF_SERVICE_ACCOUNT`
  - [ ] `FIREBASE_TOKEN`
- [ ] Workflow files pushed (or created manually)
- [ ] Branch protection configured (optional)
- [ ] GitHub Actions workflows visible

---

## 🚀 Next Steps After Setup

1. **Test Local Docker Environment**:
   ```bash
   ./scripts/dev.sh
   ```

2. **Test Deployment**:
   ```bash
   # Staging
   ./scripts/deploy-staging.sh
   
   # Production
   ./scripts/deploy-prod.sh
   ```

3. **Verify CI/CD**:
   - Push to `staging` branch → Should deploy to staging
   - Push to `main` branch → Should deploy to production

---

**Last Updated**: November 23, 2025  
**Status**: Ready for manual configuration

