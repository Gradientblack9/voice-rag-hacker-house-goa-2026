from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

def env_int(name: str, default: int) -> int:
    value = os.getenv(name, "").strip()
    try:
        return int(value) if value else default
    except ValueError:
        return default

def env_float(name: str, default: float) -> float:
    value = os.getenv(name, "").strip()
    try:
        return float(value) if value else default
    except ValueError:
        return default

@dataclass(frozen=True)
class Settings:
    top_k: int = env_int("TOP_K", 4)
    rerank_top_k: int = env_int("RERANK_TOP_K", 3)
    grounding_threshold: float = env_float("GROUNDING_THRESHOLD", 0.18)
    max_retries: int = env_int("MAX_RETRIES", 2)
    index_path: str = os.getenv("INDEX_PATH", "data/index.json")
    stt_provider: str = os.getenv("STT_PROVIDER", "sarvam")
    sarvam_api_key: str = os.getenv("SARVAM_API_KEY", "")
    # External reference lookup is opt-in: it is neither MSMARCO-XI grounded nor
    # compatible with the sub-200 ms local runtime target.
    enable_wikipedia_fallback: bool = os.getenv("ENABLE_WIKIPEDIA_FALLBACK", "false").lower() == "true"
    retrieval_candidates: int = env_int("RETRIEVAL_CANDIDATES", 64)

settings = Settings()
