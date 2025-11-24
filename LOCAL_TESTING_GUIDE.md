# 🧪 Local Testing Guide

**Complete guide for testing Cinefilm Platform locally**

---

## ✅ **Current Status**

All services are **running** and **healthy**:
- ✅ Backend API: http://localhost:8000
- ✅ Frontend: http://localhost:3000
- ✅ PostgreSQL: localhost:5432
- ✅ Redis: localhost:6379
- ✅ n8n: http://localhost:5678

---

## 🚀 **Quick Start**

### **Start Everything**
```bash
# Option 1: Use the helper script
./scripts/dev.sh

# Option 2: Manual start
docker-compose up -d
```

### **Stop Everything**
```bash
docker-compose down
```

### **View Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend-api
docker-compose logs -f frontend
```

---

## 🧪 **Testing Checklist**

### **1. Backend API** ✅

**Health Check**:
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

**API Documentation**:
- Open: http://localhost:8000/docs
- Should show Swagger UI with all endpoints

**Test Endpoints**:
```bash
# Root endpoint
curl http://localhost:8000/

# Projects endpoint (requires auth)
curl http://localhost:8000/api/projects
# Expected: 401 Unauthorized (needs Firebase token)
```

---

### **2. Frontend** ✅

**Landing Page**:
- Open: http://localhost:3000
- Should show landing page with "Enter Studio" button

**Login Page**:
- Open: http://localhost:3000/login
- Should show Google sign-in button

**Projects Page** (after login):
- Open: http://localhost:3000/projects
- Should show projects list or empty state

---

### **3. Authentication Flow** 🔍

**Test Steps**:
1. Go to: http://localhost:3000/login
2. Click "Continue with Google"
3. Authorize in popup
4. Should redirect to `/projects`
5. Check browser console (F12) for:
   - `API Request:` logs (shows token being sent)
   - Any errors

**Expected Behavior**:
- ✅ Google OAuth popup opens
- ✅ User authorizes
- ✅ Redirects to `/projects`
- ✅ API calls include Authorization header
- ✅ Projects page loads (or shows error message)

---

### **4. Database** ✅

**Test Connection**:
```bash
docker exec cinefilm-postgres psql -U postgres -d cinefilm -c "SELECT 1;"
# Expected: Returns 1
```

**Check Tables**:
```bash
docker exec cinefilm-postgres psql -U postgres -d cinefilm -c "\dt"
# Should show tables (if any created)
```

**Note**: Firestore is used for production, PostgreSQL is for local dev/testing.

---

### **5. Redis** ✅

**Test Connection**:
```bash
docker exec cinefilm-redis redis-cli ping
# Expected: PONG
```

**Test Set/Get**:
```bash
docker exec cinefilm-redis redis-cli set test "hello"
docker exec cinefilm-redis redis-cli get test
# Expected: "hello"
```

---

## 🔍 **Troubleshooting**

### **Black Screen After Login**

**Symptoms**: After Google auth, see black screen instead of projects

**Debug Steps**:
1. Open browser DevTools (F12)
2. Check **Console** tab:
   - Look for `API Request:` logs
   - Look for `API Error:` logs
   - Check for any red errors
3. Check **Network** tab:
   - Find `/api/projects` request
   - Check Request Headers → `Authorization`
   - Check Response status and body

**Common Issues**:

**Issue 1: Backend Not Running**
```bash
# Check status
docker-compose ps

# Start if needed
docker-compose up -d backend-api

# Check logs
docker-compose logs backend-api
```

**Issue 2: API URL Wrong**
- Check `web-app/.env.local`:
  ```env
  NEXT_PUBLIC_API_URL=http://localhost:8000
  ```
- Frontend uses `backend-api:8000` internally (Docker networking)
- Browser uses `localhost:8000` (from `.env.local`)

**Issue 3: Token Not Sent**
- Check console for `API Request:` logs
- Should show token in logs
- If missing, check Firebase auth is working

**Issue 4: CORS Error**
- Check backend CORS config in `backend/api/main.py`
- Should allow `http://localhost:3000`

**Issue 5: 401 Unauthorized**
- Token might be invalid
- Check backend logs for auth errors
- Verify Firebase Admin SDK is initialized

---

### **Backend Not Starting**

**Check Logs**:
```bash
docker-compose logs backend-api
```

**Common Issues**:
- Missing `.env` file → Copy from `env.example`
- Firebase credentials wrong → Check `GOOGLE_APPLICATION_CREDENTIALS`
- Port 8000 already in use → Stop other services

**Rebuild**:
```bash
docker-compose build --no-cache backend-api
docker-compose up -d backend-api
```

---

### **Frontend Not Starting**

**Check Logs**:
```bash
docker-compose logs frontend
```

**Common Issues**:
- Missing `.env.local` → Copy from `env.example`
- Port 3000 already in use → Stop other services
- Node modules issue → Rebuild container

**Rebuild**:
```bash
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

### **Database Connection Issues**

**Check PostgreSQL**:
```bash
docker-compose logs postgres
docker exec cinefilm-postgres psql -U postgres -d cinefilm -c "SELECT 1;"
```

**Reset Database**:
```bash
docker-compose down -v  # Removes volumes
docker-compose up -d postgres
```

---

## 🧪 **Full Test Flow**

### **End-to-End Test**

1. **Start Services**:
   ```bash
   ./scripts/dev.sh
   ```

2. **Verify Services**:
   - Backend: http://localhost:8000/health ✅
   - Frontend: http://localhost:3000 ✅
   - API Docs: http://localhost:8000/docs ✅

3. **Test Authentication**:
   - Go to: http://localhost:3000/login
   - Click "Continue with Google"
   - Authorize
   - Should redirect to `/projects`

4. **Test Projects Page**:
   - Should see projects list or empty state
   - Click "New Project" button
   - Fill form and create project
   - Should appear in list

5. **Test API Directly**:
   ```bash
   # Get Firebase token (from browser console after login)
   # Then test:
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/projects
   ```

---

## 📊 **Monitoring**

### **View All Logs**
```bash
docker-compose logs -f
```

### **View Specific Service**
```bash
docker-compose logs -f backend-api
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### **Check Resource Usage**
```bash
docker stats
```

---

## 🔧 **Development Workflow**

### **Hot Reload**
- ✅ **Backend**: Auto-reloads on file changes (uvicorn --reload)
- ✅ **Frontend**: Auto-reloads on file changes (Next.js dev mode)

### **Make Changes**
1. Edit files in `backend/` or `web-app/`
2. Changes auto-reload in containers
3. Check logs if issues: `docker-compose logs -f [service]`

### **Rebuild After Dependency Changes**
```bash
# Backend dependencies changed
docker-compose build backend-api
docker-compose up -d backend-api

# Frontend dependencies changed
docker-compose build frontend
docker-compose up -d frontend
```

---

## 🌐 **Access Points**

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | - |
| **Backend API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **PostgreSQL** | localhost:5432 | postgres/postgres |
| **Redis** | localhost:6379 | - |
| **n8n** | http://localhost:5678 | admin/changeme |

---

## 🐛 **Debugging Tips**

### **Browser Console**
- Open DevTools (F12)
- Check Console for errors
- Check Network tab for API calls
- Look for `API Request:` and `API Error:` logs

### **Backend Logs**
```bash
# Follow logs in real-time
docker-compose logs -f backend-api

# Look for:
# - Application startup
# - API requests
# - Errors
```

### **Frontend Logs**
```bash
# Follow logs in real-time
docker-compose logs -f frontend

# Look for:
# - Compilation status
# - Page requests
# - Errors
```

### **Database Logs**
```bash
docker-compose logs -f postgres
```

---

## ✅ **Verification Checklist**

- [ ] All services running (`docker-compose ps`)
- [ ] Backend health check passes (`curl http://localhost:8000/health`)
- [ ] Frontend loads (http://localhost:3000)
- [ ] Login page works (http://localhost:3000/login)
- [ ] Google OAuth works (can authenticate)
- [ ] Projects page loads after auth
- [ ] API calls include Authorization header (check Network tab)
- [ ] No errors in browser console
- [ ] No errors in backend logs

---

## 🚀 **Quick Commands**

```bash
# Start everything
./scripts/dev.sh

# Or manually
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Restart a service
docker-compose restart backend-api

# Rebuild a service
docker-compose build backend-api
docker-compose up -d backend-api

# Check status
docker-compose ps

# Check health
curl http://localhost:8000/health
```

---

## 📝 **Next Steps**

1. **Test Authentication**: Login with Google
2. **Test Projects**: Create a project
3. **Check Console**: Verify no errors
4. **Check Network**: Verify API calls work
5. **Test API Directly**: Use API docs at http://localhost:8000/docs

---

**Status**: ✅ All services running and ready for testing!  
**Start**: Open http://localhost:3000 and test the full flow

