# 🚀 Deployment & Domain Status

**Date**: November 23, 2025  
**Status**: ⚠️ **Workflows Configured, But Domain Not Connected**

---

## ✅ **GitHub Actions Status**

### **Workflows Active** ✅
- ✅ Development CI (`dev.yml`)
- ✅ Deploy to Firebase Hosting on merge
- ✅ Deploy to Firebase Hosting on PR
- ✅ Production deployment (`production.yml`)
- ✅ Staging deployment (`staging.yml`)

### **Recent Runs** ⚠️
- ❌ **Last run failed** (11 hours ago)
- **Error**: Git process failed during build
- **Issue**: Workflow tried to use `npm ci` but project uses `pnpm`
- **Fix Needed**: Update workflow to use `pnpm` instead of `npm`

**View failed run**: https://github.com/borahanmirzaii/Cinefilm/actions/runs/19603873145

---

## 🌐 **Domain Status**

### **cinefilm.tech** ❌ **NOT CONFIGURED**

**Current Status**:
- ❌ Domain not connected to Firebase Hosting
- ❌ Returns 404 when accessed
- ⚠️ Workflows reference `cinefilm.tech` but it's not set up

**What's Configured**:
- ✅ Default Firebase URL: `https://cinefilm-platform.web.app` ✅ **WORKING**
- ✅ Firebase Hosting site exists
- ✅ Last deployment: November 22, 2025

**What's Missing**:
- ❌ Custom domain `cinefilm.tech` not added to Firebase Hosting
- ❌ DNS records not configured
- ❌ Domain verification not completed

---

## 🔧 **Cloud Run Services**

### **Existing Services** ✅
- ✅ `backend-api` - https://backend-api-422357752899.us-central1.run.app
- ✅ `main-frontend` - https://main-frontend-422357752899.us-central1.run.app

### **Expected Services** (from workflows)
- ⚠️ `cinefilm-backend` - **DOES NOT EXIST** (workflow will create it)
- ⚠️ `cinefilm-backend-staging` - **DOES NOT EXIST** (workflow will create it)

**Note**: Workflows deploy to different service names than what currently exists.

---

## 📋 **What Needs to Be Done**

### **1. Fix GitHub Actions Workflow** (5 minutes)

The workflow is using `npm` but should use `pnpm`. The workflow file `.github/workflows/firebase-hosting-merge.yml` needs updating.

**Current Issue**:
```yaml
- run: npm ci && npm run build  # ❌ Wrong package manager
```

**Should be**:
```yaml
- uses: pnpm/action-setup@v4
  with:
    version: 10.22.0
- run: pnpm install --frozen-lockfile && pnpm build
```

### **2. Connect Domain to Firebase Hosting** (15 minutes)

**Steps**:
1. Go to: https://console.firebase.google.com/project/cinefilm-platform/hosting
2. Click "Add custom domain"
3. Enter: `cinefilm.tech`
4. Follow DNS setup instructions:
   - Add A record: `@` → Firebase IP addresses
   - Add CNAME record: `www` → `cinefilm-platform.web.app`
5. Wait for DNS propagation (can take up to 24 hours)
6. Verify domain in Firebase Console

**DNS Records Needed**:
```
Type    Name    Value
A       @       [Firebase IP addresses - provided by Firebase]
CNAME   www     cinefilm-platform.web.app
```

### **3. Update Cloud Run Domain Mapping** (Optional - 10 minutes)

If you want `api.cinefilm.tech` to point to Cloud Run backend:

1. Go to: https://console.cloud.google.com/run?project=cinefilm-platform
2. Select `cinefilm-backend` service (or create it)
3. Click "Manage custom domains"
4. Add domain: `api.cinefilm.tech`
5. Update DNS with CNAME record:
   ```
   CNAME   api     [Cloud Run domain - provided by GCP]
   ```

### **4. Update Firebase Auth Authorized Domains** (5 minutes)

1. Go to: https://console.firebase.google.com/project/cinefilm-platform/authentication/providers
2. Click "Authorized domains"
3. Add: `cinefilm.tech`
4. Add: `www.cinefilm.tech` (if using www subdomain)

---

## 🔍 **Current URLs**

### **Working** ✅
- **Firebase Default**: https://cinefilm-platform.web.app ✅
- **Backend API**: https://backend-api-422357752899.us-central1.run.app ✅
- **Frontend (old)**: https://main-frontend-422357752899.us-central1.run.app ✅

### **Not Working** ❌
- **Custom Domain**: https://cinefilm.tech ❌ (404 - not configured)
- **API Domain**: https://api.cinefilm.tech ❌ (not configured)

---

## 📊 **Workflow Configuration**

### **Production Workflow** (`production.yml`)
- **Triggers**: Push to `main` branch
- **Backend**: Deploys to `cinefilm-backend` service
- **Frontend**: Deploys to Firebase Hosting `app` target
- **API URL**: Configured as `https://api.cinefilm.tech` (but domain not set up)

### **Staging Workflow** (`staging.yml`)
- **Triggers**: Push to `staging` branch
- **Backend**: Deploys to `cinefilm-backend-staging` service
- **Frontend**: Deploys to Firebase Hosting `staging` channel
- **API URL**: Uses Cloud Run default URL

---

## ✅ **Quick Fix Checklist**

- [ ] Fix GitHub Actions workflow to use `pnpm`
- [ ] Add `cinefilm.tech` domain to Firebase Hosting
- [ ] Configure DNS records for `cinefilm.tech`
- [ ] Add `cinefilm.tech` to Firebase Auth authorized domains
- [ ] (Optional) Set up `api.cinefilm.tech` for Cloud Run
- [ ] Test deployment by pushing to `main` branch
- [ ] Verify domain works: https://cinefilm.tech

---

## 🚀 **After Domain Setup**

Once `cinefilm.tech` is configured:

1. **Frontend**: https://cinefilm.tech ✅
2. **API Rewrites**: https://cinefilm.tech/api/** → Cloud Run backend ✅
3. **Auth**: Google Auth will work on custom domain ✅
4. **Deployments**: GitHub Actions will deploy to custom domain ✅

---

## 📞 **Quick Reference**

- **GitHub Actions**: https://github.com/borahanmirzaii/Cinefilm/actions
- **Firebase Console**: https://console.firebase.google.com/project/cinefilm-platform/hosting
- **Cloud Run**: https://console.cloud.google.com/run?project=cinefilm-platform
- **Current Site**: https://cinefilm-platform.web.app ✅

---

**Status**: Workflows ready, domain needs setup  
**Next**: Add `cinefilm.tech` to Firebase Hosting → Configure DNS → Deploy!

