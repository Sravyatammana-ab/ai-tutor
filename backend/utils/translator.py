import uuid
from typing import Optional

import requests

from config import Config


class TranslatorService:
    """Lightweight Azure Translator wrapper."""

    def __init__(self):
        self.key = Config.AZURE_TRANSLATOR_KEY
        self.endpoint = (Config.AZURE_TRANSLATOR_ENDPOINT or "https://api.cognitive.microsofttranslator.com").rstrip("/")
        self.region = Config.AZURE_TRANSLATOR_REGION or "eastus"

    def _normalize_language_code(self, language: Optional[str]) -> str:
        if not language:
            return "en"
        lang = language.lower()
        if lang in Config.TTS_LANGUAGE_MAP:
            return Config.TTS_LANGUAGE_MAP[lang]
        if lang in Config.AZURE_TTS_VOICE_MAP:
            # Pull prefix from voice map entry (e.g., hi-IN -> hi)
            mapped_voice = Config.AZURE_TTS_VOICE_MAP[lang]
            if "-IN" in lang and lang.split("-")[0] in Config.TTS_LANGUAGE_MAP.values():
                return lang.split("-")[0]
        if "-" in lang:
            return lang.split("-")[0]
        return lang

    def translate(self, text: str, target_language: Optional[str]) -> str:
        if not text or not target_language:
            return text
        if not self.key:
            return text

        translator_code = self._normalize_language_code(target_language)
        if translator_code in ("en", "english"):
            return text

        params = {
            "api-version": "3.0",
            "to": translator_code,
        }
        headers = {
            "Ocp-Apim-Subscription-Key": self.key,
            "Ocp-Apim-Subscription-Region": self.region,
            "Content-Type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }
        body = [{"text": text}]
        try:
            response = requests.post(
                f"{self.endpoint}/translate",
                params=params,
                headers=headers,
                json=body,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            return data[0]["translations"][0]["text"]
        except Exception as exc:  # noqa: BLE001
            print(f"TranslatorService failed ({target_language}): {exc}")
            return text


