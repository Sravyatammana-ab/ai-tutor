# Render Build & Start Commands

## Exact Commands for Render Configuration

When setting up your Web Service on Render, use these exact commands:

### Build Command
```
pip install -r requirements.txt
```

**What it does:** Installs all Python dependencies listed in `requirements.txt` before deployment.

---

### Start Command

You have **two options**:

#### Option 1: Use Procfile (Recommended) ✅
**Leave the Start Command field EMPTY**

Render will automatically detect and use the `Procfile` in your `backend/` directory, which contains:
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

**Why this is better:**
- Cleaner configuration
- Standard practice
- Easier to maintain

---

#### Option 2: Specify Start Command Manually
If you prefer to specify it directly in Render, use:

```
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

**What this does:**
- `gunicorn` - Production WSGI server
- `app:app` - First `app` is the module name (app.py), second `app` is the Flask instance
- `--bind 0.0.0.0:$PORT` - Binds to all interfaces on the port Render provides
- `--workers 2` - Runs 2 worker processes
- `--timeout 120` - 120 second timeout for requests

---

## Complete Render Configuration Summary

| Field | Value |
|-------|-------|
| **Name** | `ai-tutor-backend` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | *(Leave empty - uses Procfile)* OR `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |

---

## Visual Guide

In the Render dashboard, you'll see:

**Build Command:**
```
Render runs this command to build your app before each deploy.
[ pip install -r requirements.txt ]
```

**Start Command:**
```
Render runs this command to start your app with each deploy.
[ (leave empty) ]  ← Recommended
OR
[ gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 ]
```

---

## Important Notes

1. **No `$` prefix needed** - Render automatically handles the command prefix
2. **Root Directory is `backend`** - This tells Render where your Python app is located
3. **Port is automatic** - Render sets `$PORT` automatically, don't hardcode it
4. **Procfile takes precedence** - If you have a Procfile, it will be used even if you specify a Start Command

---

## Troubleshooting

**If build fails:**
- Check that `requirements.txt` exists in the `backend/` directory
- Verify all dependencies are listed correctly

**If start fails:**
- Make sure `app.py` exists in `backend/` directory
- Verify `gunicorn` is in `requirements.txt` (it should be)
- Check logs in Render dashboard for specific errors

