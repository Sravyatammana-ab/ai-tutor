# Render Deployment Troubleshooting

## Error: "Could not open requirements file: requirements.txt"

This error means Render cannot find your `requirements.txt` file. Here are the solutions:

---

## Solution 1: Verify Root Directory Setting ✅

**Most Common Fix:**

1. Go to your Render service dashboard
2. Click on **Settings** tab
3. Scroll to **Build & Deploy** section
4. Check **Root Directory** field:
   - It should be exactly: `backend`
   - **NOT**: `./backend` or `/backend` or empty
   - **NOT**: `backend/` (no trailing slash)

5. If it's wrong, change it to: `backend`
6. Click **Save Changes**
7. **Manual Deploy** → **Deploy latest commit**

---

## Solution 2: Use Full Path in Build Command

If Root Directory isn't working, use the full path in the build command:

**Change Build Command from:**
```
pip install -r requirements.txt
```

**To:**
```
cd backend && pip install -r requirements.txt
```

**OR (if that doesn't work):**
```
pip install -r backend/requirements.txt
```

---

## Solution 3: Verify File is Committed

Make sure `requirements.txt` is committed and pushed to GitHub:

```bash
# Check if file is tracked
git ls-files backend/requirements.txt

# If not showing, add and commit it
git add backend/requirements.txt
git commit -m "Add requirements.txt"
git push
```

---

## Solution 4: Check File Location in Repository

Verify the file structure on GitHub:
- Go to: `https://github.com/Sravyatammana-ab/ai-tutor`
- Navigate to: `backend/requirements.txt`
- Make sure the file exists and has content

---

## Solution 5: Disable Poetry Detection

Render detected Poetry, which might interfere. To disable:

1. In Render Settings → **Build & Deploy**
2. Look for **Poetry** settings
3. Or create a `runtime.txt` file in `backend/` directory:

```
python-3.11.0
```

This tells Render to use pip, not Poetry.

---

## Solution 6: Create runtime.txt (Recommended)

Create a file `backend/runtime.txt` to specify Python version:

```
python-3.11.0
```

This ensures Render uses the correct Python version and pip (not Poetry).

---

## Complete Checklist

Before deploying, verify:

- [ ] `backend/requirements.txt` exists
- [ ] File is committed to git: `git ls-files backend/requirements.txt` shows the file
- [ ] File is pushed to GitHub
- [ ] Root Directory in Render is set to: `backend` (exactly, no slashes)
- [ ] Build Command is: `pip install -r requirements.txt`
- [ ] Start Command is empty (or gunicorn command)
- [ ] `backend/Procfile` exists
- [ ] `backend/app.py` exists

---

## Quick Fix Steps

1. **Verify Root Directory:**
   - Render Dashboard → Your Service → Settings
   - Root Directory: `backend`

2. **Create runtime.txt** (if Poetry is interfering):
   ```bash
   cd backend
   echo python-3.11.0 > runtime.txt
   git add runtime.txt
   git commit -m "Add runtime.txt"
   git push
   ```

3. **Verify requirements.txt is committed:**
   ```bash
   git add backend/requirements.txt
   git commit -m "Ensure requirements.txt is committed"
   git push
   ```

4. **Redeploy:**
   - Render Dashboard → Manual Deploy → Deploy latest commit

---

## Still Not Working?

If none of the above works:

1. **Check Render Logs:**
   - Go to Render Dashboard → Your Service → Logs
   - Look for the exact error message
   - Check what directory Render is running commands from

2. **Try Alternative Build Command:**
   ```
   cd backend; pip install -r requirements.txt
   ```

3. **Contact Render Support:**
   - They can check your specific deployment configuration

