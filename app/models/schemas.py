from typing import Literal
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)

class Citation(BaseModel):
    chunk_id: str
    source: str
    score: float

class Latency(BaseModel):
    stt: float = 0
    preprocessing: float = 0
    embedding: float = 0
    retrieval: float = 0
    rerank: float = 0
    generation: float = 0
    grounding: float = 0
    total: float = 0

class VoiceRAGResponse(BaseModel):
    request_id: str
    transcript: str
    status: Literal["answered", "abstained", "rejected", "error"]
    answer: str
    grounded: bool
    confidence: float = 0
    citations: list[Citation] = []
    reason: str | None = None
    latency_ms: Latency
