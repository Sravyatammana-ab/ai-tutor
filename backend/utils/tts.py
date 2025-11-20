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

from config import Config


class TTSService:
    """TTS service using Azure Speech Services ONLY (no fallback)"""

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
                    print("WARNING: Azure TTS key not found. TTS will not work.")
                    self.azure_speech_config = None
                else:
                    self.azure_speech_config = SpeechConfig(subscription=speech_key, region=speech_region)
                    print(f"Azure TTS initialized successfully with region: {speech_region}")
            except Exception as e:
                print(f"ERROR: Azure TTS initialization failed: {e}")
                self.azure_speech_config = None
        else:
            print("ERROR: Azure Speech SDK not installed. Please install azure-cognitiveservices-speech.")

    def _get_azure_voice(self, language: str) -> str:
        """Get Azure TTS voice name for the language"""
        # Normalize language code (handle both 'en-IN' and 'en' formats)
        normalized_lang = language
        
        # Get voice from config map
        voice_name = Config.AZURE_TTS_VOICE_MAP.get(normalized_lang)
        
        if not voice_name:
            # Try to find by prefix (e.g., 'en' matches 'en-IN')
            for lang_key in Config.AZURE_TTS_VOICE_MAP:
                if normalized_lang.startswith(lang_key.split('-')[0]):
                    voice_name = Config.AZURE_TTS_VOICE_MAP[lang_key]
                    break
        
        # Default to English (India) if not found
        if not voice_name:
            voice_name = Config.AZURE_TTS_VOICE_MAP.get("en-IN", "en-IN-NeerjaNeural")
            print(f"WARNING: Voice not found for language '{language}', using default: {voice_name}")
        
        return voice_name

    def _synthesize_with_voice(self, text: str, voice_name: str, file_path: str) -> bool:
        speech_config = SpeechConfig(subscription=Config.AZURE_SPEECH_KEY, region=Config.AZURE_SPEECH_REGION)
        speech_config.speech_synthesis_voice_name = voice_name
        audio_config = AudioConfig(filename=file_path)
        synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        result = synthesizer.speak_text_async(text).get()
        if result.reason == ResultReason.SynthesizingAudioCompleted:
            print(f"Audio generated successfully using {voice_name}")
            return True
        if result.reason == ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            error_msg = f"Azure TTS canceled: {cancellation_details.reason}"
            if cancellation_details.error_details:
                error_msg += f" - {cancellation_details.error_details}"
            print(f"ERROR: {error_msg}")
        else:
            print(f"ERROR: Azure TTS failed with reason: {result.reason}")
        return False

    def text_to_speech(
        self,
        text: str,
        language: str = "en-IN",
        session_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate audio file using Azure TTS ONLY
        """
        safe_text = (text or "").strip()
        if not safe_text:
            return None

        if len(safe_text) > self.max_chars:
            safe_text = safe_text[: self.max_chars]

        filename_prefix = session_id or "audio"
        filename = f"{filename_prefix}_{uuid.uuid4().hex[:8]}.mp3"
        file_path = os.path.join(self.audio_folder, filename)

        if not AZURE_TTS_AVAILABLE:
            print("ERROR: Azure Speech SDK not available. Cannot generate audio.")
            return None
        
        if not self.azure_speech_config:
            print("ERROR: Azure TTS not initialized. Check your AZURE_SPEECH_KEY and AZURE_SPEECH_REGION.")
            return None

        try:
            requested_voice = self._get_azure_voice(language)
            if self._synthesize_with_voice(safe_text, requested_voice, file_path):
                return filename

            if language != "en-IN":
                print(f"Falling back to English TTS voice for language {language}")
                fallback_voice = self._get_azure_voice("en-IN")
                if self._synthesize_with_voice(safe_text, fallback_voice, file_path):
                    return filename

            return None
        except Exception as exc:
            print(f"ERROR: Azure TTS generation failed: {exc}")
            import traceback
            traceback.print_exc()
            return None
