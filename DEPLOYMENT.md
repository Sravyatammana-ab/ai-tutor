# Deployment Guide - Render.com

This guide will walk you through deploying the AI Tutor backend to Render.com and integrating it with your frontend.

## Prerequisites

1. A Render.com account (sign up at https://render.com)
2. Your backend code pushed to a Git repository (GitHub, GitLab, or Bitbucket)
3. All your API keys and service credentials ready

---

## Step 1: Prepare Your Backend for Deployment

### 1.1 Ensure Required Files Exist

Make sure you have these files in your `backend/` directory:
- ✅ `Procfile` (already created)
- ✅ `requirements.txt` (with gunicorn added)
- ✅ `app.py` (main Flask application)

### 1.2 Commit Your Changes

```bash
git add backend/Procfile backend/requirements.txt
git commit -m "Add Render deployment configuration"
git push
```

---

## Step 2: Deploy to Render.com

### 2.1 Create a New Web Service

1. **Log in to Render Dashboard**
   - Go to https://dashboard.render.com
   - Sign in or create an account

2. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"

3. **Connect Your Repository**
   - Connect your GitHub/GitLab/Bitbucket account if not already connected
   - Select your repository containing the AI Tutor backend

### 2.2 Configure the Web Service

Fill in the following settings:

- **Name**: `ai-tutor-backend` (or your preferred name)
- **Region**: Choose closest to your users (e.g., `Oregon (US West)`)
- **Branch**: `main` (or your default branch)
- **Root Directory**: `backend` (important!)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: Leave empty (Render will use the Procfile)

### 2.3 Set Environment Variables

Click on "Environment" tab and add ALL the following variables:

#### Required Environment Variables

**OpenAI Configuration:**
```
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini
```

**Qdrant Configuration:**
```
QDRANT_URL=https://your-qdrant-instance-url.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=ai_tutor_documents
QDRANT_VECTOR_SIZE=1536
```

**Supabase Configuration:**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

**Azure Services Configuration:**
```
AZURE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_KEY=your-azure-key
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=eastus
AZURE_TRANSLATOR_KEY=your-azure-translator-key
AZURE_TRANSLATOR_REGION=eastus
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com
```

**Optional Configuration (with defaults):**
```
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TTS_MAX_CHARACTERS=4000
```

**Render Auto-Generated (Don't set manually):**
```
PORT=10000
```
Render automatically sets the PORT variable - don't add this manually.

### 2.4 Advanced Settings (Optional)

- **Auto-Deploy**: Enable to automatically deploy on every push to main branch
- **Health Check Path**: `/api/health`
- **Plan**: Choose based on your needs (Free tier available for testing)

### 2.5 Deploy

1. Click "Create Web Service"
2. Render will start building and deploying your service
3. Wait for deployment to complete (usually 5-10 minutes)
4. Once deployed, you'll see a URL like: `https://ai-tutor-backend.onrender.com`

---

## Step 3: Test Your Backend

### 3.1 Test Health Endpoint

Open your browser or use curl:
```bash
curl https://your-backend-url.onrender.com/api/health
```

Expected response:
```json
{"status": "healthy", "message": "AI Tutor API is running"}
```

### 3.2 Test Root Endpoint

```bash
curl https://your-backend-url.onrender.com/
```

---

## Step 4: Update Frontend Configuration

### 4.1 Update Frontend Environment Variables

In your frontend project, create or update `.env` file (or `.env.production` for production):

```env
VITE_API_BASE_URL=https://your-backend-url.onrender.com
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_KEY=your-supabase-anon-key
```

**Important Notes:**
- Remove trailing slashes from `VITE_API_BASE_URL`
- The frontend uses `VITE_API_BASE_URL` to make API calls
- If `VITE_API_BASE_URL` is not set, it defaults to empty string (relative paths)

### 4.2 Rebuild Frontend

```bash
cd frontend
npm run build
```

The built files in `frontend/dist/` will now use the Render backend URL.

---

## Step 5: Deploy Frontend (Optional)

If you want to deploy the frontend to Render as well:

1. Create a new **Static Site** on Render
2. Connect your repository
3. Set:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Add environment variables:
   - `VITE_API_BASE_URL=https://your-backend-url.onrender.com`
   - `VITE_SUPABASE_URL=...`
   - `VITE_SUPABASE_KEY=...`

---

## Troubleshooting

### Backend Not Starting

1. **Check Logs**: Go to Render dashboard → Your service → Logs
2. **Common Issues**:
   - Missing environment variables
   - Build command failing
   - Port not configured correctly (should use `$PORT` from Render)

### CORS Errors

- The backend already has CORS enabled for all origins
- If you still see CORS errors, check that your frontend URL is correct

### Environment Variables Not Working

- Make sure variable names match exactly (case-sensitive)
- Restart the service after adding new environment variables
- Check for typos in variable names

### Build Failures

- Check that `requirements.txt` has all dependencies
- Ensure Python version is compatible (Render uses Python 3.11+ by default)
- Check build logs for specific error messages

### Timeout Issues

- Render free tier has request timeout limits
- Consider upgrading to paid plan for longer timeouts
- Optimize your code for faster response times

---

## Environment Variables Summary

Here's a complete checklist of all environment variables needed:

### Backend (Render)
- [ ] `OPENAI_API_KEY`
- [ ] `OPENAI_EMBEDDING_MODEL` (optional, defaults to `text-embedding-3-small`)
- [ ] `OPENAI_CHAT_MODEL` (optional, defaults to `gpt-4o-mini`)
- [ ] `QDRANT_URL`
- [ ] `QDRANT_API_KEY`
- [ ] `QDRANT_COLLECTION_NAME` (optional, defaults to `ai_tutor_documents`)
- [ ] `QDRANT_VECTOR_SIZE` (optional, defaults to `1536`)
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_KEY`
- [ ] `AZURE_ENDPOINT`
- [ ] `AZURE_KEY`
- [ ] `AZURE_SPEECH_KEY` (or use `AZURE_KEY` as fallback)
- [ ] `AZURE_SPEECH_REGION` (optional, defaults to `eastus`)
- [ ] `AZURE_TRANSLATOR_KEY`
- [ ] `AZURE_TRANSLATOR_REGION` (optional, defaults to `eastus`)
- [ ] `AZURE_TRANSLATOR_ENDPOINT` (optional, defaults to Azure endpoint)
- [ ] `CHUNK_SIZE` (optional, defaults to `1000`)
- [ ] `CHUNK_OVERLAP` (optional, defaults to `200`)
- [ ] `TTS_MAX_CHARACTERS` (optional, defaults to `4000`)

### Frontend
- [ ] `VITE_API_BASE_URL` (your Render backend URL)
- [ ] `VITE_SUPABASE_URL`
- [ ] `VITE_SUPABASE_KEY`

---

## Next Steps

1. ✅ Backend deployed to Render
2. ✅ Backend URL obtained
3. ✅ Frontend configured with backend URL
4. ✅ Test the integration
5. ✅ Deploy frontend (if needed)

Your backend is now live and ready to serve your frontend application!

---

## Support

If you encounter any issues:
1. Check Render logs for error messages
2. Verify all environment variables are set correctly
3. Test endpoints using curl or Postman
4. Check Render status page for service outages

