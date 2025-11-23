# 🚀 Go-Live Executive Summary

**Goal**: Deploy Cinefilm Platform to production with Google Auth + Stripe payments

**Timeline**: ~2-3 hours of setup work

---

## ✅ What You Already Have

- ✅ Domain (with client ID & secret)
- ✅ Docker development environment working
- ✅ Backend API (FastAPI)
- ✅ Frontend (Next.js)
- ✅ Firebase project (`cinefilm-platform`)

---

## 📋 Action Plan (In Order)

### **Phase 1: Fix Authentication (15 min)**

**Remove GitHub Auth, Keep Only Google**

1. **Update Login Page** (`web-app/src/app/login/page.tsx`)
   - Remove GitHub OAuth button
   - Keep only Google Sign-In button

2. **Update Auth Functions** (`web-app/src/lib/auth.ts`)
   - Remove `signInWithGithub()`
   - Keep only `signInWithGoogle()`

3. **Firebase Console** → Authentication → Sign-in methods
   - Disable GitHub provider
   - Enable Google provider
   - Add your Google OAuth Client ID & Secret

---

### **Phase 2: Google Cloud Setup (30 min)**

**URL**: https://console.cloud.google.com/?project=cinefilm-platform

1. **Enable Required APIs** (run this command):
   ```bash
   gcloud config set project cinefilm-platform
   gcloud services enable \
     run.googleapis.com \
     cloudbuild.googleapis.com \
     secretmanager.googleapis.com \
     firebase.googleapis.com \
     firestore.googleapis.com \
     firebasestorage.googleapis.com
   ```

2. **Create Service Account**:
   - IAM & Admin → Service Accounts → Create
   - Name: `cinefilm-backend`
   - Grant roles:
     - Cloud Run Invoker
     - Secret Manager Secret Accessor
     - Storage Object Admin
     - Firebase Admin SDK Administrator

3. **Create Service Account Key**:
   - Download JSON key
   - Save as `backend/service-account-key.json` (DO NOT commit!)

4. **Create Secrets** (Secret Manager):
   - `stripe-api-key` → Your Stripe secret key
   - `stripe-webhook-secret` → Your Stripe webhook secret
   - `google-application-credentials` → Contents of service account JSON

---

### **Phase 3: Firebase Configuration (20 min)**

**URL**: https://console.firebase.google.com/project/cinefilm-platform

1. **Authentication**:
   - Enable **Google** provider only
   - Add your Google OAuth Client ID & Secret
   - Authorized domains: Add your domain

2. **Firestore Database**:
   - Create database (if not exists)
   - Location: `asia-east1`
   - Mode: Production

3. **Storage**:
   - Initialize (if not exists)
   - Location: `asia-east1`
   - Mode: Production

4. **Hosting**:
   - Connect custom domain: `yourdomain.com`
   - Add DNS records as instructed
   - Create staging channel (optional)

5. **Get Firebase CI Token**:
   ```bash
   firebase login:ci
   ```
   Copy the token (needed for GitHub Actions)

---

### **Phase 4: Stripe Setup (15 min)**

**URL**: https://dashboard.stripe.com

1. **Create Products**:
   - Go to Products → Create product
   - Create your subscription tiers (e.g., Basic, Pro, Enterprise)
   - Set prices (monthly/annual)

2. **Create Webhook**:
   - Developers → Webhooks → Add endpoint
   - URL: `https://yourdomain.com/api/webhooks/stripe`
   - Events: Select payment events
   - Copy webhook signing secret → Add to Secret Manager

3. **Get API Keys**:
   - Developers → API keys
   - Copy Secret key → Add to Secret Manager as `stripe-api-key`
   - Copy Publishable key → Add to frontend `.env.local`

---

### **Phase 5: GitHub Repository Setup (10 min)**

**URL**: https://github.com/borahanmirzaii/Cinefilm/settings/secrets/actions

1. **Add Secrets**:
   - `FIREBASE_TOKEN` → From `firebase login:ci`
   - `GCP_PROJECT_ID` → `cinefilm-platform`
   - `WIF_PROVIDER` → (if using Workload Identity)
   - `WIF_SERVICE_ACCOUNT` → `cinefilm-backend@cinefilm-platform.iam.gserviceaccount.com`

2. **Push Workflow Files**:
   ```bash
   git add .github/workflows/
   git commit -m "chore: add CI/CD workflows"
   git push origin main
   ```

---

### **Phase 6: Environment Variables (10 min)**

1. **Backend** (`backend/.env`):
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
   FIREBASE_PROJECT_ID=cinefilm-platform
   STRIPE_API_KEY=sk_live_... (from Secret Manager)
   REDIS_URL=redis://redis:6379/0
   DATABASE_URL=postgresql://postgres:postgres@postgres:5432/cinefilm
   ```

2. **Frontend** (`web-app/.env.local`):
   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY=...
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=cinefilm-platform.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=cinefilm-platform
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=cinefilm-platform.firebasestorage.app
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=422357752899
   NEXT_PUBLIC_FIREBASE_APP_ID=1:422357752899:web:...
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com
   ```

---

### **Phase 7: Deploy to Production (30 min)**

**Option A: Manual Deployment**

```bash
# Backend
cd backend
gcloud builds submit --config cloudbuild.yaml

# Frontend
cd web-app
firebase deploy --only hosting
```

**Option B: Automatic (via GitHub)**

1. Push to `main` branch
2. GitHub Actions will:
   - Build backend → Deploy to Cloud Run
   - Build frontend → Deploy to Firebase Hosting

---

### **Phase 8: Post-Deployment Verification (15 min)**

1. **Test Authentication**:
   - Visit `https://yourdomain.com/login`
   - Click "Sign in with Google"
   - Verify redirect works

2. **Test API**:
   - Visit `https://yourdomain.com/api/health`
   - Should return `{"status": "ok"}`

3. **Test Stripe**:
   - Go through payment flow
   - Verify webhook receives events
   - Check Stripe dashboard for payments

4. **Test Firestore**:
   - Create a project in UI
   - Verify it appears in Firestore console

---

## 🔐 Security Checklist

- [ ] Service account key is NOT committed to git
- [ ] `.env` files are in `.gitignore`
- [ ] Firebase security rules are production-ready
- [ ] Stripe webhook secret is secure
- [ ] CORS is configured correctly
- [ ] API routes require authentication

---

## 💰 Payment Flow Setup

1. **Frontend**: Stripe Checkout or Elements
2. **Backend**: Stripe webhook handler
3. **Database**: Store subscription status in Firestore
4. **Middleware**: Check subscription before API access

---

## 🚨 Common Issues & Fixes

**Issue**: Authentication redirect fails
- **Fix**: Add domain to Firebase Authorized domains

**Issue**: API returns 401
- **Fix**: Check Firebase token in request headers

**Issue**: Stripe webhook fails
- **Fix**: Verify webhook URL and secret match

**Issue**: Deployment fails
- **Fix**: Check GitHub secrets are set correctly

---

## 📞 Quick Reference

- **Google Cloud Console**: https://console.cloud.google.com/?project=cinefilm-platform
- **Firebase Console**: https://console.firebase.google.com/project/cinefilm-platform
- **Stripe Dashboard**: https://dashboard.stripe.com
- **GitHub Repo**: https://github.com/borahanmirzaii/Cinefilm

---

## ⏱️ Estimated Timeline

- **Setup**: 2-3 hours
- **Testing**: 1 hour
- **Total**: ~3-4 hours to go live

---

**Status**: Ready to execute  
**Next Step**: Start with Phase 1 (Remove GitHub Auth)

