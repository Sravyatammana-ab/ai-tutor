# AI Tutor Application

A full-stack AI tutor application that allows users to upload textbooks (PDF or DOCX), ask questions, and receive AI-powered responses with text-to-speech capabilities. The application uses OpenAI for embeddings and chat completions, Qdrant for vector storage, Supabase for conversation history, and gTTS for text-to-speech conversion.

## Project Structure

```
ai-tutor/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── config.py              # Configuration and environment variables
│   ├── requirements.txt       # Python dependencies
│   ├── env.example            # Environment variables template
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── upload.py          # File upload endpoint
│   │   ├── chat.py            # Chat and message endpoints
│   │   └── audio.py           # Audio file serving endpoint
│   └── utils/
│       ├── __init__.py
│       ├── document_parser.py # PDF/DOCX parsing and chunking
│       ├── embedding_service.py # OpenAI embedding generation
│       ├── qdrant_service.py  # Qdrant vector database operations
│       ├── llm_service.py     # OpenAI chat completions
│       ├── tts_service.py     # gTTS text-to-speech conversion
│       ├── supabase_service.py # Supabase database operations
│       └── memory_service.py  # Conversational memory management
├── frontend/
│   ├── package.json           # Node.js dependencies
│   ├── vite.config.js         # Vite configuration
│   ├── index.html             # HTML entry point
│   └── src/
│       ├── main.jsx           # React entry point
│       ├── App.jsx            # Main application component
│       ├── App.css            # Application styles
│       ├── index.css          # Global styles
│       └── components/
│           ├── FileUpload.jsx      # File upload component
│           ├── FileUpload.css
│           ├── ChatInterface.jsx   # Chat interface component
│           ├── ChatInterface.css
│           ├── MessageList.jsx     # Message list component
│           ├── MessageList.css
│           ├── Message.jsx         # Individual message component
│           ├── Message.css
│           ├── MessageInput.jsx    # Message input component
│           ├── MessageInput.css
│           ├── LanguageSelector.jsx # Language selection component
│           ├── LanguageSelector.css
│           ├── AudioPlayer.jsx     # Audio player component
│           └── AudioPlayer.css
├── .gitignore                 # Git ignore file
└── README.md                  # This file
```

## Architecture Overview

### Backend (Flask)

1. **File Upload Route** (`routes/upload.py`)
   - Accepts PDF/DOCX file uploads
   - Parses documents and extracts text
   - Chunks text into manageable pieces
   - Generates embeddings using OpenAI
   - Stores embeddings in Qdrant vector database

2. **Chat Route** (`routes/chat.py`)
   - Handles user messages
   - Retrieves relevant context from Qdrant
   - Generates AI responses using OpenAI
   - Converts responses to speech using gTTS
   - Saves conversations to Supabase

3. **Audio Route** (`routes/audio.py`)
   - Serves generated audio files
   - Handles audio file retrieval

### Frontend (React + Vite)

1. **File Upload Component**
   - Allows users to upload PDF/DOCX files
   - Displays upload progress and status

2. **Chat Interface Component**
   - Displays conversation history
   - Handles user input and message sending
   - Integrates with audio player for voice responses
   - Shows suggested follow-up questions

3. **Language Selector Component**
   - Allows users to select response language
   - Supports multiple languages (English, Spanish, French, etc.)

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│  (React Frontend - File Upload, Chat Interface, Language Select) │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FLASK BACKEND API                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. Upload Route (/api/upload/document)                   │  │
│  │    - Accepts PDF/DOCX file                               │  │
│  │    - Calls DocumentParser to extract text                │  │
│  │    - Chunks text into segments                           │  │
│  │    - Generates embeddings via OpenAI                     │  │
│  │    - Stores embeddings in Qdrant                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 2. Chat Route (/api/chat/message)                        │  │
│  │    - Receives user message                               │  │
│  │    - Generates query embedding                           │  │
│  │    - Searches Qdrant for similar chunks                  │  │
│  │    - Retrieves conversation history from Memory          │  │
│  │    - Sends context + history to OpenAI LLM               │  │
│  │    - Generates AI response                               │  │
│  │    - Converts response to speech via gTTS                │  │
│  │    - Saves conversation to Supabase                      │  │
│  │    - Updates memory with new conversation                │  │
│  │    - Returns response + audio URL                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 3. Audio Route (/api/audio/<filename>)                   │  │
│  │    - Serves generated audio files                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   OpenAI     │  │   Qdrant     │  │   Supabase   │
│   - Embeddings│  │   - Vector   │  │   - SQL DB   │
│   - Chat API │  │   - Storage   │  │   - History  │
└──────────────┘  └──────────────┘  └──────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│  - OpenAI API (Embeddings + Chat Completions)                   │
│  - Qdrant Cloud (Vector Database)                               │
│  - Supabase (SQL Database for Conversations)                    │
│  - gTTS (Text-to-Speech - Local Generation)                     │
└─────────────────────────────────────────────────────────────────┘
```

## Detailed Workflow

### 1. Document Upload Flow

```
User uploads file
    ↓
Flask receives file
    ↓
DocumentParser extracts text (PDF: PyMuPDF/pdfplumber, DOCX: python-docx)
    ↓
Text is chunked into segments (with overlap)
    ↓
Each chunk → OpenAI Embedding API → Vector embedding
    ↓
Embeddings + metadata stored in Qdrant
    ↓
Returns document_id to frontend
```

### 2. Chat Flow

```
User sends message
    ↓
Flask receives message + document_id + session_id + language
    ↓
Generate embedding for user query (OpenAI)
    ↓
Search Qdrant for similar chunks (vector similarity search)
    ↓
Retrieve conversation history from Memory Service
    ↓
Build context: Retrieved chunks + Conversation history
    ↓
Send to OpenAI Chat API (with context)
    ↓
Generate AI response
    ↓
Convert response to speech (gTTS)
    ↓
Save conversation to Supabase
    ↓
Update Memory Service with new conversation
    ↓
Return response + audio URL to frontend
    ↓
Frontend displays response and plays audio
```

### 3. Memory Management

- **In-Memory Service**: Maintains conversation history during session
- **Supabase**: Persists conversation history for long-term storage
- **LangChain-style**: Conversation context maintained across messages

## Setup Instructions

### Prerequisites

1. **Python 3.8+** - Backend
2. **Node.js 18+** - Frontend
3. **OpenAI API Key** - For embeddings and chat completions
4. **Qdrant Cloud Account** - For vector database (free tier available)
5. **Supabase Account** - For SQL database (free tier available)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file** (copy from `env.example`):
   ```bash
   cp env.example .env
   ```

5. **Configure environment variables** in `.env`:
   ```
   OPENAI_API_KEY=your_openai_api_key
   QDRANT_URL=your_qdrant_cloud_url
   QDRANT_API_KEY=your_qdrant_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

6. **Create directories**:
   ```bash
   mkdir uploads audio temp
   ```

7. **Run Flask server**:
   ```bash
   python app.py
   ```

   Server will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```

   Frontend will run on `http://localhost:3000`

### Supabase Database Setup

1. **Create a new project** in Supabase
2. **Create a table** called `conversations` with the following schema:

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

3. **Get your Supabase URL and API key** from the project settings

### Qdrant Setup

1. **Create a free Qdrant Cloud account** at https://cloud.qdrant.io
2. **Create a new cluster** (free tier available)
3. **Get your cluster URL and API key**
4. **The application will automatically create the collection** on first use

## Usage

1. **Start the backend server**:
   ```bash
   cd backend
   python app.py
   ```

2. **Start the frontend server**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open your browser** and navigate to `http://localhost:3000`

4. **Upload a PDF or DOCX file** using the file upload interface

5. **Wait for processing** - The document will be parsed, chunked, and embedded

6. **Start chatting** - Ask questions about the uploaded textbook

7. **Listen to responses** - AI responses will be converted to speech and played automatically

8. **Select language** - Choose your preferred language for responses

9. **Ask follow-up questions** - Use suggested questions or ask your own

## API Endpoints

### Backend API

- `POST /api/upload/document` - Upload and process document
- `POST /api/chat/message` - Send message and get AI response
- `GET /api/chat/history/<session_id>` - Get conversation history
- `GET /api/audio/<filename>` - Get audio file
- `GET /api/health` - Health check

### Request/Response Examples

#### Upload Document
```json
POST /api/upload/document
Content-Type: multipart/form-data

Response:
{
  "success": true,
  "document_id": "uuid-here",
  "chunks_processed": 50,
  "total_chunks": 50,
  "message": "Document uploaded and processed successfully"
}
```

#### Send Message
```json
POST /api/chat/message
Content-Type: application/json

{
  "message": "What is the main topic of this chapter?",
  "document_id": "uuid-here",
  "session_id": "session-id-here",
  "language": "en"
}

Response:
{
  "success": true,
  "session_id": "session-id-here",
  "response": "The main topic is...",
  "audio_url": "/api/audio/audio-file.mp3",
  "context_used": 5
}
```

## Features

- ✅ **PDF and DOCX Support** - Upload and parse textbooks
- ✅ **Intelligent Chunking** - Text is chunked with overlap for better context
- ✅ **Vector Search** - Semantic search using embeddings
- ✅ **Conversational AI** - Context-aware responses using OpenAI
- ✅ **Text-to-Speech** - Voice responses using gTTS
- ✅ **Multi-language Support** - Responses in multiple languages
- ✅ **Conversation History** - Persistent storage in Supabase
- ✅ **Memory Management** - LangChain-style conversational memory
- ✅ **Modern UI** - Clean, responsive React interface
- ✅ **Audio Playback** - Automatic and manual audio playback

## Technologies Used

### Backend
- **Flask** - Web framework
- **OpenAI** - Embeddings and chat completions
- **Qdrant** - Vector database
- **Supabase** - SQL database
- **gTTS** - Text-to-speech
- **PyMuPDF/pdfplumber** - PDF parsing
- **python-docx** - DOCX parsing

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **Axios** - HTTP client
- **CSS** - Styling

## Configuration

### Environment Variables

- `OPENAI_API_KEY` - OpenAI API key (required)
- `OPENAI_EMBEDDING_MODEL` - Embedding model (default: text-embedding-3-small)
- `OPENAI_CHAT_MODEL` - Chat model (default: gpt-4-turbo-preview)
- `QDRANT_URL` - Qdrant cloud URL (required)
- `QDRANT_API_KEY` - Qdrant API key (optional)
- `QDRANT_COLLECTION_NAME` - Collection name (default: ai_tutor_documents)
- `SUPABASE_URL` - Supabase URL (required)
- `SUPABASE_KEY` - Supabase API key (required)
- `CHUNK_SIZE` - Text chunk size (default: 1000)
- `CHUNK_OVERLAP` - Chunk overlap (default: 200)

## Troubleshooting

### Common Issues

1. **OpenAI API Error**
   - Check your API key in `.env`
   - Verify you have sufficient credits
   - Check rate limits

2. **Qdrant Connection Error**
   - Verify Qdrant URL and API key
   - Check network connectivity
   - Ensure collection is created

3. **Supabase Connection Error**
   - Verify Supabase URL and API key
   - Check table schema matches requirements
   - Verify database permissions

4. **Document Parsing Error**
   - Ensure PDF/DOCX file is not corrupted
   - Check file size limits
   - Verify document has extractable text

5. **Audio Generation Error**
   - Check internet connection (gTTS requires internet)
   - Verify language code is supported
   - Check audio folder permissions

## Future Enhancements

- [ ] Support for more document formats (TXT, EPUB)
- [ ] User authentication and multiple users
- [ ] Advanced chunking strategies
- [ ] Conversation export functionality
- [ ] Multiple document support per session
- [ ] Advanced search and filtering
- [ ] Custom voice selection for TTS
- [ ] Offline TTS support
- [ ] Real-time chat updates
- [ ] Mobile app support

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.

---

**Note**: This is an MVP version. For production use, consider adding:
- User authentication
- Rate limiting
- Error handling improvements
- Logging and monitoring
- Security enhancements
- Performance optimizations
- Testing suite


