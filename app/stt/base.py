from abc import ABC, abstractmethod
class SpeechToTextProvider(ABC):
    @abstractmethod
    async def transcribe(self, filename: str, content: bytes, language_code: str = "unknown") -> str: ...
