# 🔗 Firebase Hosting vs Cloud Run Domain Mapping

**Understanding the relationship and when to use each**

---

## 🎯 **Quick Answer**

**Firebase Hosting** and **Cloud Run Domain Mapping** are **complementary** services that can work together:

- **Firebase Hosting**: Serves your frontend and can proxy API requests to Cloud Run
- **Cloud Run Domain Mapping**: Maps custom domains directly to Cloud Run services (bypasses Firebase)

---

## 📊 **Architecture Options**

### **Option 1: Firebase Hosting with Rewrites** (Recommended for your setup)

```
User → cinefilm.tech (Firebase Hosting)
  ├─ / → Frontend files (Next.js)
  └─ /api/** → Rewritten to Cloud Run backend
```

**How it works**:
- `cinefilm.tech` → Firebase Hosting (serves frontend)
- `cinefilm.tech/api/**` → Firebase rewrites to Cloud Run backend
- **No separate domain needed** for API

**Your `firebase.json` configuration**:
```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "cinefilm-backend",
          "region": "us-central1"
        }
      }
    ]
  }
}
```

**Pros**:
- ✅ Single domain (`cinefilm.tech`)
- ✅ Simpler DNS setup
- ✅ Automatic SSL certificates
- ✅ Firebase handles routing

**Cons**:
- ⚠️ All traffic goes through Firebase Hosting
- ⚠️ Slightly more latency for API calls

---

### **Option 2: Separate Domain for API** (Direct Cloud Run Mapping)

```
User → cinefilm.tech (Firebase Hosting) → Frontend
User → api.cinefilm.tech (Cloud Run) → Backend API
```

**How it works**:
- `cinefilm.tech` → Firebase Hosting (frontend only)
- `api.cinefilm.tech` → Cloud Run domain mapping → Backend service
- **Separate domains** for frontend and API

**Setup**:
1. Map `cinefilm.tech` to Firebase Hosting
2. Map `api.cinefilm.tech` to Cloud Run service
3. Update frontend to call `https://api.cinefilm.tech`

**Pros**:
- ✅ Direct connection to Cloud Run (lower latency)
- ✅ Can scale API independently
- ✅ Clear separation of concerns

**Cons**:
- ⚠️ Need to manage two domains
- ⚠️ Need SSL certificates for both
- ⚠️ More complex DNS setup

---

### **Option 3: Hybrid** (Both methods)

```
cinefilm.tech → Firebase Hosting (frontend + API rewrites)
api.cinefilm.tech → Cloud Run (direct API access)
```

**Use case**: 
- Internal services use `api.cinefilm.tech` (direct)
- Web app uses `cinefilm.tech/api/**` (via Firebase rewrites)

---

## 🔍 **Key Differences**

| Feature | Firebase Hosting | Cloud Run Domain Mapping |
|---------|------------------|-------------------------|
| **Purpose** | Serve static files + proxy API | Direct domain to Cloud Run service |
| **SSL** | Automatic (Firebase managed) | Automatic (Google managed) |
| **Routing** | Can rewrite/proxy requests | Direct service mapping |
| **Cost** | Free tier available | Pay per request |
| **Setup** | Add domain in Firebase Console | Map domain in Cloud Run |
| **DNS** | Firebase provides IPs | Cloud Run provides domain |

---

## 🏗️ **Your Current Setup**

### **What You Have**:
- ✅ Firebase Hosting configured with rewrites
- ✅ Cloud Run services (`backend-api`, `main-frontend`)
- ⚠️ Domain `cinefilm.tech` **NOT yet connected**

### **What Your `firebase.json` Does**:
```json
{
  "hosting": {
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "cinefilm-backend",  // ← Points to Cloud Run service
          "region": "us-central1"
        }
      }
    ]
  }
}
```

**This means**:
- When you visit `cinefilm.tech/api/health`
- Firebase Hosting intercepts the request
- Rewrites it to Cloud Run service `cinefilm-backend`
- Returns the response

---

## 🎯 **Recommended Setup for You**

### **Single Domain Approach** (Simplest)

1. **Add `cinefilm.tech` to Firebase Hosting**
   - Go to Firebase Console → Hosting
   - Add custom domain: `cinefilm.tech`
   - Follow DNS instructions

2. **Firebase handles everything**:
   - `cinefilm.tech` → Frontend (Next.js)
   - `cinefilm.tech/api/**` → Backend (Cloud Run via rewrites)

3. **No Cloud Run domain mapping needed** ✅

**Benefits**:
- ✅ One domain to manage
- ✅ Automatic SSL
- ✅ Simple DNS setup
- ✅ Works with your current `firebase.json`

---

## 📋 **When to Use Each**

### **Use Firebase Hosting Rewrites When**:
- ✅ You want a single domain (`cinefilm.tech`)
- ✅ Frontend and API are tightly coupled
- ✅ You want simpler DNS management
- ✅ You're using Firebase for other services (Auth, Firestore)

### **Use Cloud Run Domain Mapping When**:
- ✅ You want separate API domain (`api.cinefilm.tech`)
- ✅ You need direct access to Cloud Run (lower latency)
- ✅ You have multiple backend services
- ✅ You want to expose API independently

---

## 🔧 **How They Work Together**

### **Scenario: User visits cinefilm.tech/api/projects**

1. **DNS resolves** `cinefilm.tech` → Firebase Hosting IP
2. **Firebase Hosting** receives request for `/api/projects`
3. **Firebase checks** `firebase.json` rewrites
4. **Finds match**: `/api/**` → Cloud Run service `cinefilm-backend`
5. **Firebase proxies** request to Cloud Run:
   ```
   GET https://cinefilm-backend-xxx.run.app/api/projects
   ```
6. **Cloud Run** processes request and returns response
7. **Firebase** forwards response back to user

**User never directly hits Cloud Run** - Firebase is the proxy.

---

## ⚠️ **Important Notes**

### **Service Name Must Match**
Your `firebase.json` references:
```json
"serviceId": "cinefilm-backend"
```

But your existing service is:
```
backend-api
```

**Fix**: Either:
1. Update `firebase.json` to use `backend-api`, OR
2. Deploy new service named `cinefilm-backend` (what workflows do)

### **Domain Mapping Priority**
If you map `api.cinefilm.tech` to Cloud Run:
- `api.cinefilm.tech` → Goes directly to Cloud Run (bypasses Firebase)
- `cinefilm.tech/api/**` → Goes through Firebase rewrites

Both can coexist! ✅

---

## 🚀 **Next Steps**

1. **Add `cinefilm.tech` to Firebase Hosting** (single domain approach)
2. **Verify rewrites work** once domain is connected
3. **Optional**: Add `api.cinefilm.tech` if you want direct API access

---

## 📚 **Summary**

- **Firebase Hosting**: Frontend + API proxy (via rewrites)
- **Cloud Run Domain Mapping**: Direct domain to Cloud Run service
- **They complement each other**: Use Firebase rewrites for simplicity, or Cloud Run mapping for direct access
- **Your setup**: Configured for Firebase rewrites (simpler approach)

**Recommendation**: Start with Firebase Hosting + rewrites. Add Cloud Run domain mapping later if needed.

