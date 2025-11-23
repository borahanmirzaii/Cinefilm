# 🖥️ CLI vs Web UI Setup Guide

**What you have**: `gcloud`, `firebase`, `brew`, `gh` CLI tools

---

## ✅ **CLI-ONLY Tasks** (Do These First)

### 1. **Google Cloud Setup** (via `gcloud`)

```bash
# Set project
gcloud config set project cinefilm-platform

# Enable APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  firebase.googleapis.com \
  firestore.googleapis.com \
  firebasestorage.googleapis.com \
  aiplatform.googleapis.com

# Create service account
gcloud iam service-accounts create cinefilm-backend \
  --display-name="Cinefilm Backend Service Account"

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

# Create service account key
gcloud iam service-accounts keys create backend/service-account-key.json \
  --iam-account=cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com

# Create secrets (replace with your actual values)
echo -n "sk_live_YOUR_STRIPE_KEY" | gcloud secrets create stripe-api-key \
  --data-file=- \
  --replication-policy="automatic"

echo -n "whsec_YOUR_WEBHOOK_SECRET" | gcloud secrets create stripe-webhook-secret \
  --data-file=- \
  --replication-policy="automatic"

# Store service account JSON as secret
gcloud secrets create google-application-credentials \
  --data-file=backend/service-account-key.json \
  --replication-policy="automatic"

# Get project number (needed for Workload Identity)
gcloud projects describe cinefilm-platform --format="value(projectNumber)"
```

### 2. **Firebase Setup** (via `firebase`)

```bash
# Login
firebase login

# Initialize (if not done)
firebase init

# Get CI token (for GitHub Actions)
firebase login:ci
# Copy the token - you'll need it for GitHub secrets

# Deploy security rules
firebase deploy --only firestore:rules,storage:rules

# Deploy hosting (after build)
cd web-app
firebase deploy --only hosting
```

### 3. **GitHub Setup** (via `gh`)

```bash
# Set secrets (replace values)
gh secret set FIREBASE_TOKEN --body "YOUR_FIREBASE_CI_TOKEN"
gh secret set GCP_PROJECT_ID --body "cinefilm-platform"

# Get project number for WIF_PROVIDER
PROJECT_NUMBER=$(gcloud projects describe cinefilm-platform --format="value(projectNumber)")
gh secret set WIF_PROVIDER --body "projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider"
gh secret set WIF_SERVICE_ACCOUNT --body "cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com"

# Verify secrets
gh secret list

# Push workflow files
git add .github/workflows/
git commit -m "chore: add CI/CD workflows"
git push origin main
```

### 4. **Workload Identity Federation** (via `gcloud`)

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

---

## 🌐 **WEB UI ONLY Tasks** (Must Do in Browser)

### 1. **Firebase Console** (https://console.firebase.google.com/project/cinefilm-platform)

**Authentication**:
- Go to Authentication → Sign-in methods
- Enable **Google** provider
- Add your Google OAuth Client ID & Secret
- Add authorized domains (your custom domain)

**Firestore**:
- Go to Firestore Database
- Create database (if not exists)
- Choose location: `asia-east1`
- Start in production mode

**Storage**:
- Go to Storage
- Get started (if not initialized)
- Choose location: `asia-east1`
- Start in production mode

**Hosting**:
- Go to Hosting
- Add custom domain: `yourdomain.com`
- Follow DNS instructions (add A/CNAME records)
- Create staging channel (optional)

### 2. **Stripe Dashboard** (https://dashboard.stripe.com)

**Products**:
- Go to Products → Create product
- Create subscription tiers
- Set prices

**Webhooks**:
- Go to Developers → Webhooks → Add endpoint
- URL: `https://yourdomain.com/api/webhooks/stripe`
- Select events: `payment_intent.succeeded`, `customer.subscription.created`, etc.
- Copy webhook signing secret

**API Keys**:
- Go to Developers → API keys
- Copy Secret key (starts with `sk_live_`)
- Copy Publishable key (starts with `pk_live_`)

### 3. **Google Cloud Console** (https://console.cloud.google.com/?project=cinefilm-platform)

**Only if CLI fails**:
- IAM & Admin → Service Accounts (verify creation)
- Secret Manager (verify secrets exist)
- Cloud Run (verify deployments)

---

## 🔧 **GitHub Workflow Issues & Fixes**

### **Issue 1: Workflow Files Not Pushed**

**Problem**: Workflows exist locally but not on GitHub

**Fix**:
```bash
# Check if workflows are tracked
git status .github/workflows/

# If not committed, commit and push
git add .github/workflows/
git commit -m "chore: add CI/CD workflows"
git push origin main

# If push fails due to OAuth scope, use gh CLI
gh workflow list  # Verify workflows appear
```

### **Issue 2: Missing Secrets**

**Problem**: Workflows fail because secrets are not set

**Fix**:
```bash
# Set all required secrets
gh secret set FIREBASE_TOKEN --body "$(firebase login:ci)"
gh secret set GCP_PROJECT_ID --body "cinefilm-platform"

PROJECT_NUMBER=$(gcloud projects describe cinefilm-platform --format="value(projectNumber)")
gh secret set WIF_PROVIDER --body "projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider"
gh secret set WIF_SERVICE_ACCOUNT --body "cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com"

# Verify
gh secret list
```

### **Issue 3: Workload Identity Not Configured**

**Problem**: `WIF_PROVIDER` secret is wrong or Workload Identity not set up

**Fix**:
```bash
# Run the Workload Identity setup commands above
# Then update the secret with correct value
PROJECT_NUMBER=$(gcloud projects describe cinefilm-platform --format="value(projectNumber)")
gh secret set WIF_PROVIDER --body "projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider"
```

### **Issue 4: Firebase Token Expired**

**Problem**: `FIREBASE_TOKEN` is invalid or expired

**Fix**:
```bash
# Get new token
firebase login:ci

# Update secret
gh secret set FIREBASE_TOKEN --body "NEW_TOKEN_HERE"
```

### **Issue 5: pnpm Version Mismatch**

**Problem**: Workflow uses pnpm v9 but you're using v10

**Fix**: Update workflow files:
```yaml
# In .github/workflows/*.yml
- name: Install pnpm
  uses: pnpm/action-setup@v4
  with:
    version: 10.22.0  # Match your local version
```

### **Issue 6: Missing Firebase Hosting Channel**

**Problem**: Staging workflow tries to deploy to `hosting:staging` but channel doesn't exist

**Fix**:
```bash
# Create staging channel via Firebase CLI
firebase hosting:channel:deploy staging --only hosting
```

Or create it in Firebase Console → Hosting → Channels → Create channel

---

## 📋 **Quick Setup Checklist**

### **CLI Commands** (Run in order):

```bash
# 1. Google Cloud setup
gcloud config set project cinefilm-platform
gcloud services enable run.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com firebase.googleapis.com firestore.googleapis.com firebasestorage.googleapis.com
gcloud iam service-accounts create cinefilm-backend --display-name="Cinefilm Backend"
# ... (grant roles, create secrets - see above)

# 2. Workload Identity
PROJECT_NUMBER=$(gcloud projects describe cinefilm-platform --format="value(projectNumber)")
gcloud iam workload-identity-pools create github-actions-pool --location="global" --project=cinefilm-platform
gcloud iam workload-identity-pools providers create-oidc github-provider --workload-identity-pool="github-actions-pool" --location="global" --project=cinefilm-platform --attribute-mapping="google.subject=assertion.sub" --issuer-uri="https://token.actions.githubusercontent.com"

# 3. Firebase token
firebase login:ci  # Copy token

# 4. GitHub secrets
gh secret set FIREBASE_TOKEN --body "TOKEN_FROM_STEP_3"
gh secret set GCP_PROJECT_ID --body "cinefilm-platform"
gh secret set WIF_PROVIDER --body "projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider"
gh secret set WIF_SERVICE_ACCOUNT --body "cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com"

# 5. Push workflows
git add .github/workflows/
git commit -m "chore: add CI/CD workflows"
git push origin main
```

### **Web UI Tasks** (Do in browser):

1. **Firebase Console**:
   - Enable Google Auth (add Client ID & Secret)
   - Create Firestore database (`asia-east1`)
   - Initialize Storage (`asia-east1`)
   - Add custom domain to Hosting

2. **Stripe Dashboard**:
   - Create products/prices
   - Create webhook endpoint
   - Copy API keys

---

## 🚀 **Test Workflows**

```bash
# Test workflow manually
gh workflow run production.yml

# View workflow runs
gh run list

# View specific run
gh run view RUN_ID

# Watch workflow
gh run watch
```

---

## ✅ **Verification**

```bash
# Check secrets are set
gh secret list

# Check workflows exist
gh workflow list

# Test deployment
git push origin main  # Should trigger production workflow

# Check Cloud Run
gcloud run services list --region=us-central1

# Check Firebase Hosting
firebase hosting:sites:list
```

---

**Status**: Ready to execute via CLI + minimal web UI  
**Time**: ~1 hour CLI + 30 min web UI = 1.5 hours total

