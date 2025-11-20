# AI Tutor - Project Structure

## Overview

This document describes the complete project structure of the AI Tutor application.

## Directory Structure

```
ai-tutor/
├── backend/                    # Flask backend application
│   ├── app.py                 # Main Flask application entry point
│   ├── config.py              # Configuration and environment variables
│   ├── requirements.txt       # Python dependencies
│   ├── env.example            # Environment variables template
│   ├── setup.py               # Setup script for backend
│   ├── run.sh                 # Run script for Linux/Mac
│   ├── run.bat                # Run script for Windows
│   ├── routes/                # Flask route blueprints
│   │   ├── __init__.py
│   │   ├── upload.py          # File upload endpoint
│   │   ├── chat.py            # Chat and message endpoints
│   │   └── audio.py           # Audio file serving endpoint
│   ├── utils/                 # Utility modules
│   │   ├── __init__.py
│   │   ├── document_parser.py # PDF/DOCX parsing and chunking
│   │   ├── embedding_service.py # OpenAI embedding generation
│   │   ├── qdrant_service.py  # Qdrant vector database operations
│   │   ├── llm_service.py     # OpenAI chat completions
│   │   ├── tts_service.py     # gTTS text-to-speech conversion
│   │   ├── supabase_service.py # Supabase database operations
│   │   └── memory_service.py    # Conversational memory management
│   ├── uploads/               # Uploaded documents (created at runtime)
│   ├── audio/                 # Generated audio files (created at runtime)
│   └── temp/                  # Temporary files (created at runtime)
│
├── frontend/                   # React + Vite frontend application
│   ├── package.json           # Node.js dependencies
│   ├── vite.config.js         # Vite configuration
│   ├── index.html             # HTML entry point
│   ├── README.md              # Frontend README
│   └── src/                   # Source code
│       ├── main.jsx           # React entry point
│       ├── App.jsx            # Main application component
│       ├── App.css            # Application styles
│       ├── index.css          # Global styles
│       └── components/        # React components
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
│
├── .gitignore                 # Git ignore file
├── README.md                  # Main project README
├── SETUP.md                   # Setup guide
└── PROJECT_STRUCTURE.md       # This file
```

## Backend Structure

### Main Application (`app.py`)
- Flask application initialization
- CORS configuration
- Blueprint registration
- Directory creation
- Health check endpoint

### Configuration (`config.py`)
- Environment variable loading
- API key configuration
- Database configuration
- File upload configuration
- LangChain configuration
- TTS configuration

### Routes

#### Upload Route (`routes/upload.py`)
- `POST /api/upload/document` - Upload and process document
- Handles file upload
- Parses document (PDF/DOCX)
- Chunks text
- Generates embeddings
- Stores in Qdrant

#### Chat Route (`routes/chat.py`)
- `POST /api/chat/message` - Send message and get AI response
- `GET /api/chat/history/<session_id>` - Get conversation history
- Handles user messages
- Retrieves context from Qdrant
- Generates AI response
- Converts to speech
- Saves to Supabase

#### Audio Route (`routes/audio.py`)
- `GET /api/audio/<filename>` - Get audio file
- Serves generated audio files

### Utilities

#### Document Parser (`utils/document_parser.py`)
- Parses PDF files (PyMuPDF/pdfplumber)
- Parses DOCX files (python-docx)
- Chunks text with overlap
- Extracts metadata

#### Embedding Service (`utils/embedding_service.py`)
- Generates embeddings using OpenAI
- Batch embedding generation
- Error handling

#### Qdrant Service (`utils/qdrant_service.py`)
- Qdrant client initialization
- Collection creation
- Vector storage and retrieval
- Similarity search
- Document deletion

#### LLM Service (`utils/llm_service.py`)
- OpenAI chat completions
- Context building
- Conversation history management
- Multi-language support
- System message generation

#### TTS Service (`utils/tts_service.py`)
- Text-to-speech conversion using gTTS
- Multi-language support
- Audio file generation
- File naming

#### Supabase Service (`utils/supabase_service.py`)
- Supabase client initialization
- Conversation storage
- History retrieval
- Session management
- Error handling

#### Memory Service (`utils/memory_service.py`)
- In-memory conversation storage
- Conversation history management
- Session management
- History trimming
- LangChain-style memory

## Frontend Structure

### Main Application (`App.jsx`)
- Main application component
- State management
- Route handling
- File upload handling
- Language selection
- Message management

### Components

#### File Upload (`components/FileUpload.jsx`)
- File selection
- File validation
- Upload progress
- Error handling
- Success feedback

#### Chat Interface (`components/ChatInterface.jsx`)
- Message display
- Message input
- Audio playback
- Suggested questions
- Loading states
- Error handling

#### Message List (`components/MessageList.jsx`)
- Message rendering
- Empty state
- Scroll management

#### Message (`components/Message.jsx`)
- Individual message display
- User/assistant styling
- Audio playback button
- Timestamp display

#### Message Input (`components/MessageInput.jsx`)
- Text input
- Send button
- Keyboard shortcuts
- Disabled states

#### Language Selector (`components/LanguageSelector.jsx`)
- Language selection
- Multiple language support
- Dropdown menu

#### Audio Player (`components/AudioPlayer.jsx`)
- Audio playback
- Auto-play functionality
- Playback controls
- Hidden component

## Data Flow

### Upload Flow
1. User uploads file
2. Frontend sends file to backend
3. Backend parses document
4. Backend chunks text
5. Backend generates embeddings
6. Backend stores in Qdrant
7. Backend returns document_id

### Chat Flow
1. User sends message
2. Frontend sends message to backend
3. Backend generates query embedding
4. Backend searches Qdrant for similar chunks
5. Backend retrieves conversation history
6. Backend generates AI response
7. Backend converts response to speech
8. Backend saves to Supabase
9. Backend updates memory
10. Backend returns response + audio URL
11. Frontend displays response
12. Frontend plays audio

## Configuration

### Environment Variables
- `OPENAI_API_KEY` - OpenAI API key
- `OPENAI_EMBEDDING_MODEL` - Embedding model
- `OPENAI_CHAT_MODEL` - Chat model
- `QDRANT_URL` - Qdrant cloud URL
- `QDRANT_API_KEY` - Qdrant API key
- `QDRANT_COLLECTION_NAME` - Collection name
- `SUPABASE_URL` - Supabase URL
- `SUPABASE_KEY` - Supabase API key
- `CHUNK_SIZE` - Text chunk size
- `CHUNK_OVERLAP` - Chunk overlap

### Database Schema

#### Supabase Table: `conversations`
- `id` - UUID primary key
- `session_id` - TEXT not null
- `document_id` - TEXT not null
- `user_message` - TEXT not null
- `ai_response` - TEXT not null
- `audio_path` - TEXT not null
- `language` - TEXT not null
- `created_at` - TIMESTAMP with time zone

#### Qdrant Collection: `ai_tutor_documents`
- Vector size: 1536 (OpenAI text-embedding-3-small)
- Distance: COSINE
- Payload: document_id, chunk_index, text, metadata, created_at

## API Endpoints

### Backend API
- `GET /api/health` - Health check
- `POST /api/upload/document` - Upload document
- `POST /api/chat/message` - Send message
- `GET /api/chat/history/<session_id>` - Get history
- `GET /api/audio/<filename>` - Get audio file

## Dependencies

### Backend
- Flask 3.0.0
- Flask-CORS 4.0.0
- python-dotenv 1.0.0
- OpenAI 1.12.0
- qdrant-client 1.7.0
- supabase 2.3.0
- gtts 2.5.1
- PyMuPDF 1.23.8
- pdfplumber 0.10.3
- python-docx 1.1.0
- werkzeug 3.0.1

### Frontend
- React 18.2.0
- React-DOM 18.2.0
- Axios 1.6.0
- Vite 5.0.0
- @vitejs/plugin-react 4.2.0

## File Purposes

### Backend Files

#### `app.py`
- Main Flask application
- CORS configuration
- Blueprint registration
- Directory creation
- Health check

#### `config.py`
- Configuration management
- Environment variable loading
- API key configuration
- Database configuration

#### `routes/upload.py`
- File upload handling
- Document parsing
- Text chunking
- Embedding generation
- Qdrant storage

#### `routes/chat.py`
- Message handling
- Context retrieval
- AI response generation
- Speech conversion
- Conversation storage

#### `routes/audio.py`
- Audio file serving
- File retrieval

#### `utils/document_parser.py`
- PDF parsing
- DOCX parsing
- Text chunking
- Metadata extraction

#### `utils/embedding_service.py`
- Embedding generation
- OpenAI API integration
- Batch processing

#### `utils/qdrant_service.py`
- Qdrant client
- Vector storage
- Similarity search
- Collection management

#### `utils/llm_service.py`
- OpenAI chat completions
- Context building
- Conversation management
- Multi-language support

#### `utils/tts_service.py`
- Text-to-speech conversion
- gTTS integration
- Audio file generation

#### `utils/supabase_service.py`
- Supabase client
- Conversation storage
- History retrieval
- Session management

#### `utils/memory_service.py`
- In-memory storage
- Conversation history
- Session management
- LangChain-style memory

### Frontend Files

#### `App.jsx`
- Main application component
- State management
- Route handling
- File upload
- Language selection

#### `components/FileUpload.jsx`
- File selection
- Upload handling
- Progress display
- Error handling

#### `components/ChatInterface.jsx`
- Chat interface
- Message display
- Message input
- Audio playback
- Suggested questions

#### `components/MessageList.jsx`
- Message list rendering
- Empty state
- Scroll management

#### `components/Message.jsx`
- Individual message
- User/assistant styling
- Audio playback
- Timestamp

#### `components/MessageInput.jsx`
- Text input
- Send button
- Keyboard shortcuts

#### `components/LanguageSelector.jsx`
- Language selection
- Dropdown menu
- Multiple languages

#### `components/AudioPlayer.jsx`
- Audio playback
- Auto-play
- Hidden component

## Setup and Deployment

### Development Setup
1. Install backend dependencies
2. Install frontend dependencies
3. Configure environment variables
4. Set up Supabase database
5. Set up Qdrant cluster
6. Run backend server
7. Run frontend server

### Production Deployment
1. Build frontend
2. Configure production environment
3. Set up production database
4. Deploy backend
5. Deploy frontend
6. Configure reverse proxy
7. Set up SSL certificates

## Testing

### Backend Testing
- Unit tests for utilities
- Integration tests for routes
- API endpoint testing
- Error handling testing

### Frontend Testing
- Component testing
- Integration testing
- User interface testing
- API integration testing

## Monitoring and Logging

### Backend Logging
- Application logs
- Error logs
- API request logs
- Performance logs

### Frontend Logging
- Console logs
- Error handling
- API request logs
- User interaction logs

## Security

### Backend Security
- API key management
- File upload validation
- CORS configuration
- Error handling
- Input validation

### Frontend Security
- Input validation
- XSS prevention
- CSRF protection
- Secure API calls

## Performance

### Backend Performance
- Caching
- Database optimization
- API response optimization
- File processing optimization

### Frontend Performance
- Code splitting
- Lazy loading
- Image optimization
- API request optimization

## Future Enhancements

- User authentication
- Multiple document support
- Advanced search
- Custom voice selection
- Offline TTS support
- Real-time updates
- Mobile app support
- Analytics and monitoring
- Advanced chunking strategies
- Conversation export
- Multi-user support

