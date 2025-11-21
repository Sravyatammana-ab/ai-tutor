import os
import uuid
from typing import Optional

try:
    from azure.cognitiveservices.speech import (
        SpeechConfig,
        SpeechSynthesizer,
        AudioConfig,
        ResultReason
    )
    AZURE_TTS_AVAILABLE = True
except ImportError:
    AZURE_TTS_AVAILABLE = False
    print("WARNING: Azure Speech SDK not available. TTS will not work.")

try:
    from openai import OpenAI
    OPENAI_TTS_AVAILABLE = True
except ImportError:
    OPENAI_TTS_AVAILABLE = False
    print("WARNING: OpenAI SDK not available. OpenAI TTS fallback will not work.")

try:
    from gtts import gTTS
    import io
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("WARNING: gTTS not available. Final fallback TTS will not work.")

from config import Config


class TTSService:
    """TTS service: Azure (primary) -> OpenAI TTS (secondary) -> gTTS (last resort)"""

    # Azure-supported languages with neural voices
    AZURE_SUPPORTED_LANGUAGES = {
        "en-IN": "en-IN-NeerjaNeural",
        "en": "en-IN-NeerjaNeural",
        "hi-IN": "hi-IN-SwaraNeural",
        "hi": "hi-IN-SwaraNeural",
        "gu-IN": "gu-IN-DhwaniNeural",
        "gu": "gu-IN-DhwaniNeural",
        "kn-IN": "kn-IN-SapnaNeural",
        "kn": "kn-IN-SapnaNeural",
        "ml-IN": "ml-IN-SobhanaNeural",
        "ml": "ml-IN-SobhanaNeural",
        "mr-IN": "mr-IN-AarohiNeural",
        "mr": "mr-IN-AarohiNeural",
        "ta-IN": "ta-IN-PallaviNeural",
        "ta": "ta-IN-PallaviNeural",
        "te-IN": "te-IN-SruthiNeural",
        "te": "te-IN-SruthiNeural",
        "ur-IN": "ur-IN-GulNeural",
        "ur": "ur-IN-GulNeural",
    }

    # Languages NOT supported by Azure - use OpenAI TTS or gTTS
    NON_AZURE_LANGUAGES = {
        "pa-IN": "pa",
        "pa": "pa",
        "or-IN": "or",
        "or": "or",
        "bn-IN": "bn",
        "bn": "bn",
        "as-IN": "as",
        "as": "as",
    }

    # OpenAI TTS voice mapping (alloy, echo, fable, onyx, nova, shimmer)
    OPENAI_VOICE_MAP = {
        "pa": "alloy",  # Punjabi
        "or": "echo",   # Odia
        "bn": "nova",   # Bengali
        "as": "shimmer", # Assamese
    }

    # gTTS language code mapping (fallback)
    GTTS_LANG_MAP = {
        "pa": "pa",  # Punjabi
        "or": "or",  # Odia
        "bn": "bn",  # Bengali
        "as": "as",  # Assamese
    }

    def __init__(self) -> None:
        self.audio_folder = Config.AUDIO_FOLDER
        os.makedirs(self.audio_folder, exist_ok=True)
        self.max_chars = getattr(Config, "TTS_MAX_CHARACTERS", 4000)
        
        # Initialize Azure Speech
        self.azure_speech_config = None
        if AZURE_TTS_AVAILABLE:
            try:
                speech_key = Config.AZURE_SPEECH_KEY
                speech_region = Config.AZURE_SPEECH_REGION
                
                if not speech_key:
                    print("WARNING: Azure TTS key not found. Will use fallbacks.")
                    self.azure_speech_config = None
                else:
                    self.azure_speech_config = SpeechConfig(subscription=speech_key, region=speech_region)
                    print(f"Azure TTS initialized successfully with region: {speech_region}")
            except Exception as e:
                print(f"ERROR: Azure TTS initialization failed: {e}")
                self.azure_speech_config = None
        else:
            print("WARNING: Azure Speech SDK not installed. Will use fallbacks.")
        
        # Initialize OpenAI client
        self.openai_client = None
        if OPENAI_TTS_AVAILABLE and Config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                print("OpenAI TTS initialized successfully")
            except Exception as e:
                print(f"WARNING: OpenAI TTS initialization failed: {e}")
                self.openai_client = None
        else:
            print("WARNING: OpenAI TTS not available. Will use gTTS fallback.")
        
        if not GTTS_AVAILABLE:
            print("WARNING: gTTS not installed. Some languages may not have audio support.")

    def _is_azure_supported(self, language: str) -> bool:
        """Check if language is supported by Azure TTS"""
        normalized_lang = language
        if normalized_lang in self.AZURE_SUPPORTED_LANGUAGES:
            return True
        # Check by prefix
        for lang_key in self.AZURE_SUPPORTED_LANGUAGES:
            if normalized_lang.startswith(lang_key.split('-')[0]):
                return True
        return False

    def _is_non_azure_language(self, language: str) -> bool:
        """Check if language is NOT supported by Azure (needs OpenAI/gTTS)"""
        normalized_lang = language
        if normalized_lang in self.NON_AZURE_LANGUAGES:
            return True
        # Check by prefix
        for lang_key in self.NON_AZURE_LANGUAGES:
            if normalized_lang.startswith(lang_key.split('-')[0]):
                return True
        return False

    def _get_azure_voice(self, language: str) -> Optional[str]:
        """Get Azure TTS voice name for the language"""
        normalized_lang = language
        voice_name = self.AZURE_SUPPORTED_LANGUAGES.get(normalized_lang)
        
        if not voice_name:
            # Try to find by prefix
            for lang_key in self.AZURE_SUPPORTED_LANGUAGES:
                if normalized_lang.startswith(lang_key.split('-')[0]):
                    voice_name = self.AZURE_SUPPORTED_LANGUAGES[lang_key]
                    break
        
        return voice_name

    def _synthesize_with_azure(self, text: str, voice_name: str, file_path: str) -> bool:
        """Synthesize audio using Azure TTS"""
        try:
            speech_config = SpeechConfig(subscription=Config.AZURE_SPEECH_KEY, region=Config.AZURE_SPEECH_REGION)
            speech_config.speech_synthesis_voice_name = voice_name
            audio_config = AudioConfig(filename=file_path)
            synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

            result = synthesizer.speak_text_async(text).get()
            
            if hasattr(result, 'reason'):
                if result.reason == ResultReason.SynthesizingAudioCompleted:
                    print(f"Audio generated successfully using Azure voice: {voice_name}")
                    return True
                elif result.reason == ResultReason.Canceled:
                    cancellation_details = result.cancellation_details
                    error_msg = f"Azure TTS canceled: {cancellation_details.reason}"
                    if hasattr(cancellation_details, 'error_details') and cancellation_details.error_details:
                        error_msg += f" - {cancellation_details.error_details}"
                    print(f"ERROR: {error_msg}")
                else:
                    print(f"ERROR: Azure TTS failed with reason: {result.reason}")
            else:
                print(f"WARNING: Unexpected Azure TTS result format")
                return False
        except Exception as e:
            print(f"ERROR: Azure TTS synthesis exception: {e}")
            import traceback
            traceback.print_exc()
        return False

    def _synthesize_with_openai(self, text: str, language: str, file_path: str) -> bool:
        """Synthesize audio using OpenAI TTS"""
        if not OPENAI_TTS_AVAILABLE or not self.openai_client:
            return False
        
        try:
            # Get base language code
            base_lang = language.split('-')[0] if '-' in language else language
            voice = self.OPENAI_VOICE_MAP.get(base_lang, "alloy")
            
            print(f"Using OpenAI TTS for language: {base_lang} (voice: {voice})")
            
            # OpenAI TTS API call
            response = self.openai_client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            # Save audio to file
            response.stream_to_file(file_path)
            
            print(f"Audio generated successfully using OpenAI TTS for language: {base_lang}")
            return True
        except Exception as e:
            print(f"ERROR: OpenAI TTS synthesis failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _synthesize_with_gtts(self, text: str, language: str, file_path: str) -> bool:
        """Synthesize audio using gTTS (last resort fallback)"""
        if not GTTS_AVAILABLE:
            return False
        
        try:
            # Get gTTS language code
            normalized_lang = language
            gtts_lang = self.NON_AZURE_LANGUAGES.get(normalized_lang)
            
            if not gtts_lang:
                base_lang = normalized_lang.split('-')[0] if '-' in normalized_lang else normalized_lang
                gtts_lang = self.GTTS_LANG_MAP.get(base_lang, base_lang)
            
            print(f"Using gTTS for language: {gtts_lang} (requested: {language})")
            
            # Generate audio with gTTS
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            
            # Save to temporary file first
            temp_path = file_path.replace('.mp3', '_temp.mp3')
            tts.save(temp_path)
            
            # Rename to final path
            if file_path.endswith('.mp3'):
                os.rename(temp_path, file_path)
            else:
                # Convert if needed
                try:
                    from pydub import AudioSegment
                    audio = AudioSegment.from_mp3(temp_path)
                    audio.export(file_path, format="mp3")
                    os.remove(temp_path)
                except ImportError:
                    os.rename(temp_path, file_path)
            
            print(f"Audio generated successfully using gTTS for language: {gtts_lang}")
            return True
        except Exception as e:
            print(f"ERROR: gTTS synthesis failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def text_to_speech(
        self,
        text: str,
        language: str = "en-IN",
        session_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate audio file using: Azure (primary) -> OpenAI TTS (secondary) -> gTTS (last resort)
        
        Args:
            text: Text to convert to speech
            language: Language code (e.g., 'en-IN', 'pa-IN', 'as-IN', etc.)
            session_id: Optional session identifier for filename
        
        Returns:
            Audio filename if successful, None otherwise
        """
        safe_text = (text or "").strip()
        if not safe_text:
            return None

        if len(safe_text) > self.max_chars:
            safe_text = safe_text[: self.max_chars]

        filename_prefix = session_id or "audio"
        filename = f"{filename_prefix}_{uuid.uuid4().hex[:8]}.mp3"
        file_path = os.path.join(self.audio_folder, filename)

        # Strategy 1: Azure TTS for supported languages
        if self._is_azure_supported(language):
            if AZURE_TTS_AVAILABLE and self.azure_speech_config:
                voice_name = self._get_azure_voice(language)
                if voice_name:
                    if self._synthesize_with_azure(safe_text, voice_name, file_path):
                        return filename
                    else:
                        print(f"Azure TTS failed for {language}, trying OpenAI TTS fallback")
                        # Fallback to OpenAI if Azure fails
                        if self._synthesize_with_openai(safe_text, language, file_path):
                            return filename
                        # Last resort: gTTS
                        if self._synthesize_with_gtts(safe_text, language, file_path):
                            return filename

        # Strategy 2: Non-Azure languages (pa-IN, or-IN, bn-IN, as-IN)
        elif self._is_non_azure_language(language):
            print(f"Language {language} not supported by Azure, using OpenAI TTS")
            # Try OpenAI TTS first
            if self._synthesize_with_openai(safe_text, language, file_path):
                return filename
            # Fallback to gTTS
            print(f"OpenAI TTS failed for {language}, trying gTTS fallback")
            if self._synthesize_with_gtts(safe_text, language, file_path):
                return filename

        # Strategy 3: Unknown language - try all methods
        else:
            print(f"Unknown language {language}, trying Azure first")
            if AZURE_TTS_AVAILABLE and self.azure_speech_config:
                voice_name = self._get_azure_voice(language)
                if voice_name and self._synthesize_with_azure(safe_text, voice_name, file_path):
                    return filename
            
            # Try OpenAI
            if self._synthesize_with_openai(safe_text, language, file_path):
                return filename
            
            # Try gTTS
            if self._synthesize_with_gtts(safe_text, language, file_path):
                return filename

        # Last resort: Azure English voice
        if AZURE_TTS_AVAILABLE and self.azure_speech_config:
            print(f"All methods failed for {language}, trying Azure English as last resort")
            fallback_voice = self._get_azure_voice("en-IN")
            if fallback_voice and self._synthesize_with_azure(safe_text, fallback_voice, file_path):
                return filename

        print(f"ERROR: All TTS methods failed for language: {language}")
        return None
