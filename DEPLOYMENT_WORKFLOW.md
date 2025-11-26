# Deployment Workflow - Render.com

## 🔄 How Render Deployment Works

**YES, you need to commit and push to Git for changes to appear on Render.**

Render uses **Git-based deployments**, which means:
- Render watches your Git repository
- When you push changes, Render automatically rebuilds and redeploys
- Your live site always reflects the latest code in your Git repository

---

## 📋 Step-by-Step Workflow

### For Backend Changes (like the vector_store.py fix):

1. **Make your code changes** ✅ (Already done - we fixed `vector_store.py`)

2. **Commit changes to Git:**
   ```bash
   git add backend/utils/vector_store.py
   git commit -m "Fix Qdrant vector name error - use 'default' vector name"
   ```

3. **Push to your repository:**
   ```bash
   git push origin main
   # or
   git push origin master
   ```

4. **Render automatically detects the push:**
   - If **Auto-Deploy** is enabled → Render automatically starts deploying
   - If **Auto-Deploy** is disabled → You need to manually trigger deployment

5. **Wait for deployment to complete:**
   - Check Render dashboard → Your service → Logs
   - Usually takes 3-5 minutes
   - You'll see "Deploy successful" when done

6. **Test your changes:**
   ```bash
   curl https://your-backend-url.onrender.com/api/health
   ```

---

## ⚙️ Render Auto-Deploy Settings

### Check if Auto-Deploy is Enabled:

1. Go to Render Dashboard
2. Click on your backend service
3. Go to **Settings** tab
4. Look for **"Auto-Deploy"** section

**If Enabled:**
- ✅ Every push to your main branch automatically triggers deployment
- No manual action needed after `git push`

**If Disabled:**
- ❌ You need to manually click **"Manual Deploy"** button after pushing
- Or enable Auto-Deploy in settings

---

## 🚀 Quick Commands for Deployment

### Option 1: Commit and Push (Recommended)
```bash
# Stage your changes
git add backend/utils/vector_store.py backend/app.py

# Commit with a descriptive message
git commit -m "Fix Qdrant vector name error and enable auto-reload for development"

# Push to trigger deployment
git push origin main
```

### Option 2: Manual Deploy (if Auto-Deploy is off)
```bash
# After pushing to Git
# 1. Go to Render Dashboard
# 2. Click on your service
# 3. Click "Manual Deploy" button
# 4. Select the branch/commit to deploy
```

---

## 🔍 How to Verify Deployment

### 1. Check Render Logs
- Go to Render Dashboard → Your Service → **Logs** tab
- Look for:
  - ✅ "Build successful"
  - ✅ "Deploy successful"
  - ✅ "Your service is live"

### 2. Test the Health Endpoint
```bash
curl https://your-backend-url.onrender.com/api/health
```
Should return: `{"status": "healthy", "message": "AI Tutor API is running"}`

### 3. Test Your Specific Fix
- Try uploading a document
- The vector name error should be gone
- Check browser console for errors

---

## ⚠️ Important Notes

### What Gets Deployed:
- ✅ **Everything in your Git repository**
- ✅ **Only committed and pushed changes**
- ❌ **Local uncommitted changes are NOT deployed**

### Environment Variables:
- Environment variables are set in Render Dashboard
- They persist across deployments
- You don't need to re-enter them for each deployment

### Build Time:
- First deployment: ~5-10 minutes
- Subsequent deployments: ~3-5 minutes
- Depends on your code size and dependencies

---

## 🛠️ Troubleshooting

### Changes Not Appearing?

1. **Did you commit?**
   ```bash
   git status  # Check if files are committed
   ```

2. **Did you push?**
   ```bash
   git log --oneline -5  # Check recent commits
   ```

3. **Is Auto-Deploy enabled?**
   - Check Render Dashboard → Settings

4. **Is deployment in progress?**
   - Check Render Dashboard → Logs
   - Wait for "Deploy successful" message

5. **Did deployment fail?**
   - Check Render Dashboard → Logs for error messages
   - Common issues:
     - Missing dependencies in `requirements.txt`
     - Syntax errors in code
     - Environment variables missing

---

## 📝 Summary

**To see your backend changes on Render:**

```
Make Changes → Commit → Push → Render Auto-Deploys → Test
     ✅           ✅      ✅            ✅              ✅
```

**You MUST:**
1. ✅ Commit changes to Git
2. ✅ Push to repository
3. ✅ Wait for Render to deploy (or manually trigger)

**You DON'T need to:**
- ❌ Manually restart Render (it restarts automatically)
- ❌ Re-enter environment variables
- ❌ Reconfigure the service

---

## 🎯 For Your Current Fix

Since we fixed `vector_store.py`, here's what to do:

```bash
# 1. Stage the changes
git add backend/utils/vector_store.py backend/app.py backend/run-dev.bat backend/run-dev.sh

# 2. Commit
git commit -m "Fix Qdrant vector name error: use 'default' vector name for all operations"

# 3. Push (this triggers Render deployment)
git push origin main

# 4. Wait 3-5 minutes, then test
curl https://your-backend-url.onrender.com/api/health
```

That's it! Render will automatically deploy your changes. 🚀

