# Test Your Backend - Quick Guide

## ✅ Your Backend is Live!

**URL:** `https://ai-tutor-bknj.onrender.com`

---

## 🧪 Quick Tests

### Test 1: Root Endpoint (API Info)
**URL:** https://ai-tutor-bknj.onrender.com/

**Expected Response:**
```json
{
  "message": "AI Tutor API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/api/health",
    "upload": "/api/upload/document",
    "chat": "/api/chat",
    "audio": "/api/audio"
  }
}
```

### Test 2: Health Check
**URL:** https://ai-tutor-bknj.onrender.com/api/health

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "AI Tutor API is running"
}
```

---

## 🌐 Test in Browser

1. **Open your browser**
2. **Go to:** `https://ai-tutor-bknj.onrender.com/api/health`
3. **You should see:** `{"status":"healthy","message":"AI Tutor API is running"}`

If you see this, your backend is **LIVE and WORKING!** ✅

---

## 💻 Test with Command Line

### Windows PowerShell:
```powershell
# Test health endpoint
Invoke-WebRequest -Uri "https://ai-tutor-bknj.onrender.com/api/health" | Select-Object -ExpandProperty Content

# Test root endpoint
Invoke-WebRequest -Uri "https://ai-tutor-bknj.onrender.com/" | Select-Object -ExpandProperty Content
```

### Or use curl (if installed):
```bash
curl https://ai-tutor-bknj.onrender.com/api/health
curl https://ai-tutor-bknj.onrender.com/
```

---

## 🔗 Next: Update Frontend

Now that your backend is live, update your frontend:

1. **Create/Update `frontend/.env`:**
   ```env
   VITE_API_BASE_URL=https://ai-tutor-bknj.onrender.com
   VITE_SUPABASE_URL=your-supabase-url
   VITE_SUPABASE_KEY=your-supabase-key
   ```

2. **Rebuild frontend:**
   ```bash
   cd frontend
   npm run build
   ```

3. **Test locally:**
   ```bash
   npm run dev
   ```

---

## ✅ Status Check

- [x] Backend deployed to Render
- [x] Backend URL: `https://ai-tutor-bknj.onrender.com`
- [x] Health endpoint working
- [ ] Frontend updated with backend URL
- [ ] Frontend tested with backend

---

Your backend is **LIVE** and ready to use! 🎉

