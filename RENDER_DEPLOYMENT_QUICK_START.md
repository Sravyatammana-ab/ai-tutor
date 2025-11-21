# Quick Start: Deploy Backend to Render

## 🚀 Quick Steps

### 1. Push Code to Git
```bash
git add .
git commit -m "Prepare for Render deployment"
git push
```

### 2. Create Web Service on Render

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your repository
4. Configure:
   - **Name**: `ai-tutor-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: 
     - **Option 1 (Recommended)**: Leave it **EMPTY** - Render will automatically use the `Procfile`
     - **Option 2**: If you want to specify manually, use: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

### 3. Add Environment Variables

Click "Environment" and add these **REQUIRED** variables:

```
OPENAI_API_KEY=sk-...
QDRANT_URL=https://...
QDRANT_API_KEY=...
SUPABASE_URL=https://...
SUPABASE_KEY=...
AZURE_ENDPOINT=https://...
AZURE_KEY=...
AZURE_SPEECH_KEY=...
AZURE_TRANSLATOR_KEY=...
```

**Optional** (have defaults):
```
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini
QDRANT_COLLECTION_NAME=ai_tutor_documents
QDRANT_VECTOR_SIZE=1536
AZURE_SPEECH_REGION=eastus
AZURE_TRANSLATOR_REGION=eastus
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TTS_MAX_CHARACTERS=4000
```

### 4. Deploy

Click "Create Web Service" and wait for deployment.

### 5. Get Your Backend URL

After deployment, you'll get a URL like:
```
https://ai-tutor-backend.onrender.com
```

### 6. Update Frontend

In your frontend `.env` file:
```env
VITE_API_BASE_URL=https://ai-tutor-backend.onrender.com
```

Then rebuild:
```bash
cd frontend
npm run build
```

---

## ✅ Test Your Deployment

```bash
curl https://your-backend-url.onrender.com/api/health
```

Should return:
```json
{"status": "healthy", "message": "AI Tutor API is running"}
```

---

## 📋 Complete Environment Variables List

Copy-paste this checklist:

**Required:**
- [ ] `OPENAI_API_KEY`
- [ ] `QDRANT_URL`
- [ ] `QDRANT_API_KEY`
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_KEY`
- [ ] `AZURE_ENDPOINT`
- [ ] `AZURE_KEY`
- [ ] `AZURE_SPEECH_KEY`
- [ ] `AZURE_TRANSLATOR_KEY`

**Optional (with defaults):**
- [ ] `OPENAI_EMBEDDING_MODEL` (default: `text-embedding-3-small`)
- [ ] `OPENAI_CHAT_MODEL` (default: `gpt-4o-mini`)
- [ ] `QDRANT_COLLECTION_NAME` (default: `ai_tutor_documents`)
- [ ] `QDRANT_VECTOR_SIZE` (default: `1536`)
- [ ] `AZURE_SPEECH_REGION` (default: `eastus`)
- [ ] `AZURE_TRANSLATOR_REGION` (default: `eastus`)
- [ ] `CHUNK_SIZE` (default: `1000`)
- [ ] `CHUNK_OVERLAP` (default: `200`)
- [ ] `TTS_MAX_CHARACTERS` (default: `4000`)

---

## 🔗 Integration

Once deployed, use this URL in your frontend:
```
https://your-backend-url.onrender.com
```

No trailing slash needed!

---

For detailed instructions, see `DEPLOYMENT.md`

