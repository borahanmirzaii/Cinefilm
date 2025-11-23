# 🔄 Domain Migration: Cloud Run → Firebase Hosting

**Current Status**: `cinefilm.tech` is verified by Google and used for Cloud Run  
**Goal**: Use `cinefilm.tech` for Firebase Hosting instead (or alongside)

---

## 📋 **Step-by-Step Actions**

### **Step 1: Check Current Domain Mapping** (2 minutes)

**Check what's currently using your domain**:

```bash
# Check Cloud Run domain mappings
gcloud beta run domain-mappings list --region=us-central1 --project=cinefilm-platform

# Check Firebase Hosting domains
firebase hosting:sites:list --project=cinefilm-platform
```

**What to look for**:
- Is `cinefilm.tech` mapped to a Cloud Run service?
- Is `cinefilm.tech` already in Firebase Hosting?

---

### **Step 2: Decide on Architecture** (Choose One)

#### **Option A: Replace Cloud Run Domain with Firebase Hosting** (Recommended)

**What happens**:
- Remove domain from Cloud Run
- Add domain to Firebase Hosting
- Firebase rewrites `/api/**` to Cloud Run (no direct domain needed)

**Pros**:
- ✅ Single domain (`cinefilm.tech`)
- ✅ Simpler DNS
- ✅ Firebase handles SSL automatically
- ✅ API still works via rewrites

**Cons**:
- ⚠️ Need to remove Cloud Run domain mapping first

#### **Option B: Keep Both (Hybrid)**

**What happens**:
- Keep `cinefilm.tech` on Cloud Run (or remove it)
- Add `cinefilm.tech` to Firebase Hosting
- Use Firebase rewrites for `/api/**`

**Note**: You can't have the same domain on both simultaneously. Choose one.

---

### **Step 3: Remove Domain from Cloud Run** (If Option A)

**If your domain is currently mapped to Cloud Run**:

```bash
# List current mappings
gcloud beta run domain-mappings list --region=us-central1 --project=cinefilm-platform

# Remove domain mapping (if exists)
gcloud beta run domain-mappings delete cinefilm.tech \
  --region=us-central1 \
  --project=cinefilm-platform
```

**⚠️ Important**: This will make `cinefilm.tech` temporarily unavailable until you add it to Firebase Hosting.

---

### **Step 4: Add Domain to Firebase Hosting** (10 minutes)

**Via Firebase Console** (Easiest):

1. Go to: https://console.firebase.google.com/project/cinefilm-platform/hosting
2. Click **"Add custom domain"**
3. Enter: `cinefilm.tech`
4. Click **"Continue"**
5. Firebase will show you DNS records to add

**Via Firebase CLI**:

```bash
firebase hosting:channel:create live --project=cinefilm-platform
# Then add domain via Console (CLI doesn't support custom domains directly)
```

---

### **Step 5: Update DNS Records** (5 minutes)

**Firebase will provide DNS records like**:

```
Type    Name    Value
A       @       151.101.1.195
A       @       151.101.65.195
CNAME   www     cinefilm-platform.web.app
```

**What to do**:
1. Go to your domain registrar (where you bought `cinefilm.tech`)
2. Update DNS records:
   - **Remove old A/CNAME records** (if pointing to Cloud Run)
   - **Add new A records** (provided by Firebase)
   - **Add CNAME record** for `www` subdomain
3. Save changes

**DNS Propagation**: Can take 5 minutes to 24 hours (usually 5-30 minutes)

---

### **Step 6: Verify Domain in Firebase** (5 minutes)

**After DNS records are added**:

1. Go back to Firebase Console → Hosting
2. Firebase will automatically verify DNS records
3. Once verified, SSL certificate is automatically provisioned
4. Status will change from "Pending" to "Connected"

**Check status**:
```bash
firebase hosting:sites:list --project=cinefilm-platform
```

---

### **Step 7: Update Firebase Auth Authorized Domains** (2 minutes)

**Add your domain to Firebase Auth**:

1. Go to: https://console.firebase.google.com/project/cinefilm-platform/authentication/providers
2. Click **"Authorized domains"** tab
3. Click **"Add domain"**
4. Enter: `cinefilm.tech`
5. Click **"Add"**

**Why**: Google Auth needs to know `cinefilm.tech` is authorized.

---

### **Step 8: Test Deployment** (5 minutes)

**Deploy to Firebase Hosting**:

```bash
cd web-app
firebase deploy --only hosting:app --project=cinefilm-platform
```

**Test URLs**:
- Frontend: https://cinefilm.tech ✅
- API via rewrite: https://cinefilm.tech/api/health ✅

---

## ⚠️ **Important Notes**

### **DNS Propagation Time**
- DNS changes can take 5 minutes to 24 hours
- During this time, your domain may be temporarily unavailable
- Plan for a brief downtime window

### **SSL Certificate**
- Firebase automatically provisions SSL certificates
- Takes 5-10 minutes after DNS verification
- Your site will be HTTPS automatically

### **Cloud Run Services**
- Your Cloud Run services (`backend-api`, `main-frontend`) remain running
- They're just not directly accessible via `cinefilm.tech` anymore
- API requests go through Firebase rewrites instead

### **Backward Compatibility**
- Old Cloud Run URLs still work:
  - `https://backend-api-422357752899.us-central1.run.app`
- But `cinefilm.tech` now points to Firebase Hosting

---

## 🔄 **Migration Checklist**

- [ ] Check current Cloud Run domain mappings
- [ ] Remove `cinefilm.tech` from Cloud Run (if mapped)
- [ ] Add `cinefilm.tech` to Firebase Hosting
- [ ] Update DNS records (A records + CNAME)
- [ ] Wait for DNS propagation
- [ ] Verify domain in Firebase Console
- [ ] Add domain to Firebase Auth authorized domains
- [ ] Deploy frontend to Firebase Hosting
- [ ] Test: https://cinefilm.tech
- [ ] Test API: https://cinefilm.tech/api/health

---

## 🚨 **Rollback Plan**

**If something goes wrong**:

1. **Keep Cloud Run domain mapping** (don't delete until Firebase is working)
2. **Or quickly restore**:
   ```bash
   gcloud beta run domain-mappings create cinefilm.tech \
     --service=backend-api \
     --region=us-central1 \
     --project=cinefilm-platform
   ```

---

## 📊 **Before vs After**

### **Before (Current)**
```
cinefilm.tech → Cloud Run service (direct)
```

### **After (Target)**
```
cinefilm.tech → Firebase Hosting
  ├─ / → Frontend files
  └─ /api/** → Cloud Run (via Firebase rewrites)
```

---

## 🎯 **Quick Command Summary**

```bash
# 1. Check current setup
gcloud beta run domain-mappings list --region=us-central1 --project=cinefilm-platform

# 2. Remove from Cloud Run (if needed)
gcloud beta run domain-mappings delete cinefilm.tech --region=us-central1 --project=cinefilm-platform

# 3. Add to Firebase Hosting (via Console)
# Go to: https://console.firebase.google.com/project/cinefilm-platform/hosting

# 4. Update DNS (at your registrar)
# Add A records + CNAME as provided by Firebase

# 5. Verify
firebase hosting:sites:list --project=cinefilm-platform

# 6. Deploy
cd web-app && firebase deploy --only hosting:app --project=cinefilm-platform
```

---

**Status**: Ready to migrate  
**Time Estimate**: 30-60 minutes (mostly waiting for DNS)  
**Downtime**: 5-30 minutes (during DNS propagation)

