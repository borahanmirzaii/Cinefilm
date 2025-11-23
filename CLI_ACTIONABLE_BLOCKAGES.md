# 🖥️ CLI-Actionable Blockages (No Stripe Login Required)

**Status**: Firebase CLI available ✅  
**Blockage**: Stripe login unavailable (can skip for now)

---

## ✅ **What We Can Do NOW via CLI**

### **1. Firebase Project Linking** ✅ DONE
```bash
firebase use cinefilm-platform
# ✅ Already completed!
```

### **2. Create Firestore Database** (via gcloud)
```bash
# Try creating Firestore database
gcloud firestore databases create \
  --location=asia-east1 \
  --type=firestore-native \
  --project=cinefilm-platform
```

**Note**: If this fails (database might already exist or need Web UI), we can still deploy rules.

### **3. Deploy Firestore Rules** ✅ CAN DO
```bash
firebase deploy --only firestore:rules
```

### **4. Deploy Storage Rules** ✅ CAN DO
```bash
firebase deploy --only storage:rules
```

### **5. Deploy Both Rules Together** ✅ CAN DO
```bash
firebase deploy --only firestore:rules,storage:rules
```

### **6. Verify Firebase Config**
```bash
# Check current project
firebase use

# List projects
firebase projects:list

# Check Firestore databases
firebase firestore:databases:list
```

---

## ❌ **What We CANNOT Do via CLI (Requires Web UI)**

### **1. Enable Google Auth Provider**
- **Why**: Firebase CLI doesn't support enabling auth providers
- **Action**: Must use Firebase Console → Authentication → Sign-in methods
- **URL**: https://console.firebase.google.com/project/cinefilm-platform/authentication/providers

### **2. Create Firestore Database** (if gcloud fails)
- **Why**: Some Firebase features require Web UI
- **Action**: Firebase Console → Firestore Database → Create database
- **URL**: https://console.firebase.google.com/project/cinefilm-platform/firestore

### **3. Initialize Storage** (if not initialized)
- **Why**: Initial setup requires Web UI
- **Action**: Firebase Console → Storage → Get started
- **URL**: https://console.firebase.google.com/project/cinefilm-platform/storage

### **4. Stripe Webhook** (requires Stripe login)
- **Why**: Need Stripe Dashboard access
- **Action**: Skip for now, do later when Stripe login works
- **Impact**: Payment webhooks won't work until this is done

---

## 🚀 **Quick CLI Commands to Run NOW**

Run these in order:

```bash
# 1. Verify Firebase project (already done ✅)
firebase use cinefilm-platform

# 2. Try creating Firestore database
gcloud firestore databases create \
  --location=asia-east1 \
  --type=firestore-native \
  --project=cinefilm-platform

# 3. Deploy security rules (will work even if DB creation fails)
firebase deploy --only firestore:rules,storage:rules

# 4. Verify deployment
firebase firestore:databases:list
```

---

## 📋 **What Gets Unblocked**

After running CLI commands:

✅ **Unblocked**:
- Firestore rules deployed (security rules active)
- Storage rules deployed (security rules active)
- Firebase project linked (CLI ready)
- Firestore database created (if gcloud command works)

⚠️ **Still Blocked** (need Web UI):
- Google Auth provider enabled
- Firestore database (if gcloud fails)
- Storage initialization (if not done)
- Stripe webhook (need Stripe login)

---

## 🎯 **Next Steps After CLI**

1. **If Firestore DB created**: ✅ One less thing!
2. **If Firestore DB creation fails**: Go to Web UI → Create database
3. **Deploy rules**: ✅ Can do now via CLI
4. **Enable Google Auth**: Web UI only (5 min)
5. **Stripe webhook**: Skip for now, do when Stripe login works

---

## ⏱️ **Time Estimate**

- **CLI Commands**: 2-5 minutes
- **Web UI Tasks**: 15-20 minutes (can do later)
- **Stripe Setup**: Skip for now

**Total CLI Time**: ~5 minutes  
**Can Deploy Rules**: ✅ Yes  
**Can Deploy App**: ⚠️ Partial (need Google Auth enabled)

---

**Status**: Ready to run CLI commands  
**Next**: Run the commands above → Deploy rules → Check what's left

