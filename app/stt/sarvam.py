import httpx
from app.stt.base import SpeechToTextProvider

SUPPORTED_LANGUAGE_CODES = {
    "unknown", "en-IN", "hi-IN", "bn-IN", "ta-IN", "te-IN",
    "mr-IN", "gu-IN", "kn-IN", "ml-IN", "pa-IN", "od-IN", "ur-IN",
}

def normalize_language_code(language_code: str) -> str:
    return language_code if language_code in SUPPORTED_LANGUAGE_CODES else "unknown"

class SarvamSTT(SpeechToTextProvider):
    def __init__(self, api_key: str): self.api_key=api_key
    async def transcribe(self, filename: str, content: bytes, language_code: str = "unknown") -> str:
        if not self.api_key: raise ValueError("SARVAM_API_KEY is not configured")
        async with httpx.AsyncClient(timeout=12) as client:
            response=await client.post(
                "https://api.sarvam.ai/speech-to-text",
                headers={"api-subscription-key":self.api_key},
                files={"file":(filename,content)},
                data={"model":"saaras:v3","mode":"transcribe","language_code":normalize_language_code(language_code)},
            )
            response.raise_for_status(); data=response.json()
        return data.get("transcript") or data.get("text") or ""
