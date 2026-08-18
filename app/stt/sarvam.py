import httpx
from app.stt.base import SpeechToTextProvider
class SarvamSTT(SpeechToTextProvider):
    def __init__(self, api_key: str): self.api_key=api_key
    async def transcribe(self, filename: str, content: bytes) -> str:
        if not self.api_key: raise ValueError("SARVAM_API_KEY is not configured")
        async with httpx.AsyncClient(timeout=12) as client:
            response=await client.post("https://api.sarvam.ai/speech-to-text", headers={"api-subscription-key":self.api_key}, files={"file":(filename,content)})
            response.raise_for_status(); data=response.json()
        return data.get("transcript") or data.get("text") or ""
