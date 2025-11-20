# AI Tutor - Setup Guide

This guide will help you set up the AI Tutor application step by step.

## Prerequisites

1. **Python 3.8+** - Backend
2. **Node.js 18+** - Frontend
3. **OpenAI API Key** - For embeddings and chat completions
4. **Qdrant Cloud Account** - For vector database (free tier available)
5. **Supabase Account** - For SQL database (free tier available)

## Step 1: Backend Setup

### 1.1 Install Python Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 1.2 Configure Environment Variables

1. Copy `env.example` to `.env`:
   ```bash
   cp env.example .env
   ```

2. Update `.env` with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   QDRANT_URL=your_qdrant_cloud_url
   QDRANT_API_KEY=your_qdrant_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

### 1.3 Create Directories

```bash
mkdir uploads audio temp
```

### 1.4 Run Backend Server

```bash
python app.py
```

The backend will run on `http://localhost:5000`

## Step 2: Frontend Setup

### 2.1 Install Node.js Dependencies

```bash
cd frontend
npm install
```

### 2.2 Run Frontend Server

```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Step 3: Supabase Database Setup

### 3.1 Create Supabase Project

1. Go to https://supabase.com
2. Create a new project
3. Get your project URL and API key

### 3.2 Create Database Table

Run the following SQL in the Supabase SQL Editor:

```sql
CREATE TABLE conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    audio_path TEXT NOT NULL,
    language TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_session_id ON conversations(session_id);
CREATE INDEX idx_document_id ON conversations(document_id);
```

### 3.3 Get API Credentials

1. Go to Project Settings > API
2. Copy the Project URL and anon/public key
3. Update your `.env` file with these values

## Step 4: Qdrant Setup

### 4.1 Create Qdrant Cloud Account

1. Go to https://cloud.qdrant.io
2. Create a free account
3. Create a new cluster (free tier available)

### 4.2 Get Cluster Credentials

1. Go to your cluster dashboard
2. Copy the cluster URL and API key
3. Update your `.env` file with these values

### 4.3 Collection Creation

The application will automatically create the collection on first use. No manual setup required.

## Step 5: Test the Application

### 5.1 Start Backend

```bash
cd backend
python app.py
```

### 5.2 Start Frontend

```bash
cd frontend
npm run dev
```

### 5.3 Test Upload

1. Open `http://localhost:3000` in your browser
2. Upload a PDF or DOCX file
3. Wait for processing
4. Start chatting with the AI tutor

## Troubleshooting

### Backend Issues

1. **Import Errors**: Make sure all dependencies are installed
2. **API Key Errors**: Check your `.env` file has correct API keys
3. **Database Errors**: Verify Supabase table exists and credentials are correct
4. **Qdrant Errors**: Check Qdrant cluster is running and credentials are correct

### Frontend Issues

1. **Connection Errors**: Make sure backend is running on port 5000
2. **CORS Errors**: Check backend CORS configuration
3. **Build Errors**: Make sure all dependencies are installed

### Common Issues

1. **Port Already in Use**: Change port in `app.py` or `vite.config.js`
2. **Missing Dependencies**: Run `pip install -r requirements.txt` or `npm install`
3. **API Key Invalid**: Check your API keys are correct and have sufficient credits

## Next Steps

1. **Customize**: Update the UI, add features, or modify the AI prompts
2. **Deploy**: Deploy to production (Heroku, AWS, etc.)
3. **Monitor**: Set up logging and monitoring
4. **Scale**: Optimize for production use

## Support

For issues and questions, please open an issue on GitHub.


