# Fix GitHub Authentication Issue

## Problem
Git is trying to use cached credentials for "krishna777s" instead of your account "Sravyatammana-ab".

## Solution: Use Personal Access Token (PAT)

### Step 1: Create a Personal Access Token on GitHub

1. Go to GitHub.com and sign in as **Sravyatammana-ab**
2. Click your profile picture (top right) → **Settings**
3. Scroll down to **Developer settings** (left sidebar)
4. Click **Personal access tokens** → **Tokens (classic)**
5. Click **Generate new token** → **Generate new token (classic)**
6. Give it a name: `AI Tutor Repository Access`
7. Set expiration: **90 days** (or your preference)
8. Select scopes:
   - ✅ **repo** (Full control of private repositories)
   - ✅ **workflow** (if you use GitHub Actions)
9. Click **Generate token**
10. **COPY THE TOKEN IMMEDIATELY** (you won't see it again!)

### Step 2: Use the Token When Pushing

When you run `git push`, it will prompt for:
- **Username**: `Sravyatammana-ab`
- **Password**: **Paste your Personal Access Token** (not your GitHub password)

### Step 3: Push Your Changes

```bash
git push -u origin main
```

When prompted:
- Username: `Sravyatammana-ab`
- Password: `[paste your PAT token here]`

---

## Alternative: Use GitHub Desktop

If you prefer a GUI:
1. Download GitHub Desktop: https://desktop.github.com/
2. Sign in with your **Sravyatammana-ab** account
3. Open your repository
4. Commit and push from the GUI

---

## Alternative: Use SSH Instead of HTTPS

If you want to avoid tokens:

1. **Generate SSH key** (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "tammanasravya1122@gmail.com"
   ```

2. **Add SSH key to GitHub**:
   - Copy the public key: `cat ~/.ssh/id_ed25519.pub`
   - GitHub → Settings → SSH and GPG keys → New SSH key
   - Paste and save

3. **Update remote URL to use SSH**:
   ```bash
   git remote set-url origin git@github.com:Sravyatammana-ab/ai-tutor.git
   ```

4. **Push**:
   ```bash
   git push -u origin main
   ```

---

## Quick Fix Summary

**Current Status:**
- ✅ Cached credentials cleared
- ✅ Remote URL updated to include your username
- ⏳ Need to create PAT and use it when pushing

**Next Steps:**
1. Create Personal Access Token on GitHub
2. Run `git push -u origin main`
3. Enter username: `Sravyatammana-ab`
4. Enter password: `[your PAT token]`

---

## Verify Your Setup

After successful push, verify:
```bash
git remote -v
# Should show: https://Sravyatammana-ab@github.com/Sravyatammana-ab/ai-tutor.git
```

