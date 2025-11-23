# 🚧 Walls Hit - Need Your Help

## ✅ **What I Successfully Automated**

1. ✅ Google Cloud project configuration
2. ✅ Enabled all required APIs
3. ✅ Created service account with proper roles
4. ✅ Generated service account key
5. ✅ Created Workload Identity Pool
6. ⚠️ Workload Identity Provider (see issue below)
7. ✅ Set GitHub secrets (GCP_PROJECT_ID, WIF_PROVIDER, WIF_SERVICE_ACCOUNT)
8. ✅ Updated and committed workflow files
9. ✅ Created service account key file

---

## 🚧 **Walls Hit**

### **Wall 1: Workload Identity Provider**

**Issue**: The provider creation is failing with attribute mapping errors.

**What I tried**:
- Simple mapping: `google.subject=assertion.sub` ❌
- With condition: Still failing ❌

**What you need to do**:
Option A: Create via Web UI (Easier)
1. Go to: https://console.cloud.google.com/iam-admin/workload-identity-federation?project=cinefilm-platform
2. Click on `github-actions-pool`
3. Click "Add Provider"
4. Choose "OpenID Connect (OIDC)"
5. Provider name: `github-provider`
6. Issuer URL: `https://token.actions.githubusercontent.com`
7. Attribute mapping:
   - `google.subject` = `assertion.sub`
8. Click "Save"

Option B: Try this CLI command (if you want):
```bash
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --project=cinefilm-platform \
  --location="global" \
  --workload-identity-pool="github-actions-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

---

### **Wall 2: Firebase CI Token**

**Issue**: `firebase login:ci` requires browser authentication - cannot automate.

**What you need to do**:
```bash
# Run this command - it will open a browser
firebase login:ci

# Copy the token that appears, then run:
gh secret set FIREBASE_TOKEN --body "PASTE_TOKEN_HERE"
```

**OR** if you already have a token, just set it:
```bash
gh secret set FIREBASE_TOKEN --body "YOUR_EXISTING_TOKEN"
```

---

### **Wall 3: Stripe Secrets**

**Issue**: I don't have your Stripe API keys (and shouldn't have them).

**What you need to do**:
1. Go to: https://dashboard.stripe.com/apikeys
2. Copy your **Secret key** (starts with `sk_live_` or `sk_test_`)
3. Run:
```bash
echo -n "sk_live_YOUR_KEY_HERE" | gcloud secrets create stripe-api-key \
  --data-file=- \
  --replication-policy="automatic"
```

4. Go to: https://dashboard.stripe.com/webhooks
5. Create webhook endpoint (if not exists)
6. Copy the **Signing secret** (starts with `whsec_`)
7. Run:
```bash
echo -n "whsec_YOUR_SECRET_HERE" | gcloud secrets create stripe-webhook-secret \
  --data-file=- \
  --replication-policy="automatic"
```

---

### **Wall 4: Git Push**

**Issue**: May require authentication or have permission issues.

**What happened**: Workflows are committed locally, ready to push.

**What you need to do**:
```bash
git push origin main
```

If it fails, check:
- GitHub authentication: `gh auth status`
- Repository permissions
- Branch protection rules

---

## 📋 **Complete Checklist**

### **CLI Tasks** (You can do these):

```bash
# 1. Fix Workload Identity Provider (if not working)
# See Wall 1 above - use Web UI or try the CLI command

# 2. Get Firebase token
firebase login:ci
gh secret set FIREBASE_TOKEN --body "TOKEN_FROM_ABOVE"

# 3. Create Stripe secrets
echo -n "sk_live_YOUR_KEY" | gcloud secrets create stripe-api-key --data-file=- --replication-policy="automatic"
echo -n "whsec_YOUR_SECRET" | gcloud secrets create stripe-webhook-secret --data-file=- --replication-policy="automatic"

# 4. Push workflows
git push origin main

# 5. Verify everything
gh secret list
gcloud secrets list
```

### **Web UI Tasks** (Must do in browser):

1. **Firebase Console**:
   - Enable Google Auth
   - Create Firestore database
   - Initialize Storage
   - Add custom domain

2. **Stripe Dashboard**:
   - Create products
   - Create webhook endpoint

---

## ✅ **What's Already Done**

- Google Cloud: ✅ Complete
- Service Account: ✅ Complete
- Workload Identity Pool: ✅ Complete
- GitHub Secrets: ✅ 3/4 complete (missing FIREBASE_TOKEN)
- Workflows: ✅ Updated and committed
- Service Account Key: ✅ Created

---

**Status**: ~85% Complete  
**Remaining**: 4 manual tasks (see above)

