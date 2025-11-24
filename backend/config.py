import os
from dotenv import load_dotenv

load_dotenv()


def _get_env(key: str, default=None, strip: bool = True, remove_newlines: bool = True):
    """
    Fetch environment variables with optional stripping of whitespace/newlines.
    Prevents malformed headers (e.g., Qdrant API key with trailing newline).
    """
    value = os.getenv(key, default)
    if isinstance(value, str):
        if strip:
            value = value.strip()
        if remove_newlines:
            value = value.replace('\r', '').replace('\n', '')
        return value
    return value


class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = _get_env('OPENAI_API_KEY')
    OPENAI_EMBEDDING_MODEL = _get_env('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
    OPENAI_CHAT_MODEL = _get_env('OPENAI_CHAT_MODEL', 'gpt-4o-mini')
    
    # Qdrant Configuration
    QDRANT_URL = _get_env('QDRANT_URL')
    QDRANT_API_KEY = _get_env('QDRANT_API_KEY')
    QDRANT_COLLECTION_NAME = _get_env('QDRANT_COLLECTION_NAME', 'ai_tutor_documents')
    QDRANT_VECTOR_SIZE = int(_get_env('QDRANT_VECTOR_SIZE', 1536))
    
    # Supabase Configuration
    SUPABASE_URL = _get_env('SUPABASE_URL')
    SUPABASE_KEY = _get_env('SUPABASE_KEY')
    
    # File Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    AUDIO_FOLDER = 'audio'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    
    # LangChain Configuration
    CHUNK_SIZE = int(_get_env('CHUNK_SIZE', 1000))
    CHUNK_OVERLAP = int(_get_env('CHUNK_OVERLAP', 200))
    
    # TTS Configuration
    TTS_LANGUAGE_MAP = {
        'en-IN': 'en',
        'hi': 'hi',
        'ta': 'ta',
        'te': 'te',
        'kn': 'kn',
        'ml': 'ml',
        'mr': 'mr',
        'gu': 'gu',
        'bn': 'bn',
        'pa': 'pa',
        'or': 'or',
        'as': 'as',
        'ur': 'ur'
    }
    TTS_MAX_CHARACTERS = int(_get_env('TTS_MAX_CHARACTERS', 4000))
    
    # Azure Document Intelligence Configuration
    AZURE_ENDPOINT = _get_env('AZURE_ENDPOINT')
    AZURE_KEY = _get_env('AZURE_KEY')
    
    # Azure Speech Service Configuration
    AZURE_SPEECH_KEY = _get_env('AZURE_SPEECH_KEY') or _get_env('AZURE_KEY')  # Fallback to AZURE_KEY if AZURE_SPEECH_KEY not set
    AZURE_SPEECH_REGION = _get_env('AZURE_SPEECH_REGION', 'eastus')
    
    # Azure TTS Voice Map (Neural Voices)
    # Format: "language-code": "voice-name"
    AZURE_TTS_VOICE_MAP = {
        "en-IN": "en-IN-NeerjaNeural",
        "en": "en-IN-NeerjaNeural",  # Support both formats
        "hi-IN": "hi-IN-MadhurNeural",
        "hi": "hi-IN-MadhurNeural",
        "te-IN": "te-IN-SruthiNeural",
        "te": "te-IN-SruthiNeural",
        "ta-IN": "ta-IN-PallaviNeural",
        "ta": "ta-IN-PallaviNeural",
        "ml-IN": "ml-IN-SobhanaNeural",
        "ml": "ml-IN-SobhanaNeural",
        "kn-IN": "kn-IN-GaganNeural",
        "kn": "kn-IN-GaganNeural",
        "mr": "mr-IN-AarohiNeural",
        "mr-IN": "mr-IN-AarohiNeural",
        "gu": "gu-IN-DhwaniNeural",
        "gu-IN": "gu-IN-DhwaniNeural",
        "bn": "bn-IN-TanishaaNeural",
        "bn-IN": "bn-IN-TanishaaNeural",
        "pa": "pa-IN-GurpreetNeural",
        "pa-IN": "pa-IN-GurpreetNeural",
        "or": "or-IN-MadhurNeural",
        "or-IN": "or-IN-MadhurNeural",
        "as": "as-IN-JyotiNeural",
        "as-IN": "as-IN-JyotiNeural",
        "ur": "ur-IN-GulNeural",
        "ur-IN": "ur-IN-GulNeural",
    }

    # Azure Translator Configuration
    AZURE_TRANSLATOR_KEY = _get_env('AZURE_TRANSLATOR_KEY')
    AZURE_TRANSLATOR_REGION = _get_env('AZURE_TRANSLATOR_REGION', 'eastus')
    AZURE_TRANSLATOR_ENDPOINT = _get_env('AZURE_TRANSLATOR_ENDPOINT', 'https://api.cognitive.microsofttranslator.com')
