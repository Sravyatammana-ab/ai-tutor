# Backend Integration Guide

## ✅ Your Backend is Live!

**Backend URL:** `https://ai-tutor-bknj.onrender.com`

Your backend is successfully deployed and responding! 🎉

---

## 🔍 How to Check if Backend is Live

### Method 1: Test in Browser

Open these URLs in your browser:

1. **Root Endpoint (API Info):**
   ```
   https://ai-tutor-bknj.onrender.com/
   ```
   Should show: `{"message":"AI Tutor API","version":"1.0.0",...}`

2. **Health Check:**
   ```
   https://ai-tutor-bknj.onrender.com/api/health
   ```
   Should show: `{"status":"healthy","message":"AI Tutor API is running"}`

### Method 2: Test with curl (Command Line)

```bash
# Test root endpoint
curl https://ai-tutor-bknj.onrender.com/

# Test health endpoint
curl https://ai-tutor-bknj.onrender.com/api/health
```

### Method 3: Test with Postman or Browser DevTools

1. Open browser DevTools (F12)
2. Go to Console tab
3. Run:
   ```javascript
   fetch('https://ai-tutor-bknj.onrender.com/api/health')
     .then(r => r.json())
     .then(console.log)
   ```

---

## ✅ Available Endpoints

Based on your API response, these endpoints are available:

- **Health Check:** `GET /api/health`
- **File Upload:** `POST /api/upload/document`
- **Chat:** `POST /api/chat/*`
- **Audio:** `GET /api/audio/*`

---

## 🔗 Next Steps: Integrate with Frontend

### Step 1: Update Frontend Environment Variables

Create or update `.env` file in your `frontend/` directory:

```env
VITE_API_BASE_URL=https://ai-tutor-bknj.onrender.com
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_KEY=your-supabase-anon-key
```

**Important:**
- ✅ No trailing slash after the URL
- ✅ Use `https://` (not `http://`)
- ✅ The frontend already uses `VITE_API_BASE_URL` in all API calls

### Step 2: Rebuild Frontend

After updating `.env`, rebuild your frontend:

```bash
cd frontend
npm run build
```

### Step 3: Test Frontend Locally

```bash
cd frontend
npm run dev
```

Then test:
- Upload a document
- Send a chat message
- Check if audio playback works

---

## 🧪 Complete Testing Checklist

### Backend Tests

- [ ] ✅ Root endpoint works: `https://ai-tutor-bknj.onrender.com/`
- [ ] ✅ Health check works: `https://ai-tutor-bknj.onrender.com/api/health`
- [ ] Test file upload (use Postman or frontend)
- [ ] Test chat endpoint (use Postman or frontend)
- [ ] Test audio endpoint (use Postman or frontend)

### Frontend Integration Tests

- [ ] Frontend `.env` has `VITE_API_BASE_URL` set
- [ ] Frontend rebuilt after `.env` update
- [ ] File upload works from frontend
- [ ] Chat messages work from frontend
- [ ] Audio playback works from frontend

---

## 🐛 Troubleshooting

### If Backend Returns 404

- Check that all routes are registered in `app.py`
- Verify environment variables are set in Render
- Check Render logs for errors

### If Frontend Can't Connect

1. **Check CORS:**
   - Backend has CORS enabled for all origins
   - Should work automatically

2. **Check Environment Variable:**
   - Make sure `VITE_API_BASE_URL` is set correctly
   - No trailing slash
   - Rebuild frontend after changing `.env`

3. **Check Browser Console:**
   - Open DevTools (F12)
   - Look for CORS errors or 404 errors
   - Check Network tab for failed requests

### If Backend is Slow

- Render free tier has cold starts (first request after inactivity)
- First request may take 30-60 seconds
- Subsequent requests are faster
- Consider upgrading to paid plan for better performance

---

## 📝 Quick Reference

**Your Backend URL:**
```
https://ai-tutor-bknj.onrender.com
```

**Frontend Environment Variable:**
```env
VITE_API_BASE_URL=https://ai-tutor-bknj.onrender.com
```

**Test Commands:**
```bash
# Health check
curl https://ai-tutor-bknj.onrender.com/api/health

# Root endpoint
curl https://ai-tutor-bknj.onrender.com/
```

---

## 🎉 Success!

Your backend is live and ready to use! Now integrate it with your frontend and you're all set!

