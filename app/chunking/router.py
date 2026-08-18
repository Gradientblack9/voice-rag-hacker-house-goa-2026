"""Multiple indexing strategies: semantic sentences, metadata-aware, sliding window."""
import re
from dataclasses import dataclass

@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    text: str
    source: str
    metadata: dict

def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

def semantic_chunks(text: str, limit: int = 90) -> list[str]:
    result, current = [], []
    for sentence in _sentences(text):
        candidate = " ".join(current + [sentence])
        if current and len(candidate.split()) > limit:
            result.append(" ".join(current)); current = [sentence]
        else: current.append(sentence)
    if current: result.append(" ".join(current))
    return result

def sliding_chunks(text: str, size: int = 110, overlap: int = 24) -> list[str]:
    words, result = text.split(), []
    for start in range(0, len(words), max(1, size - overlap)):
        piece = words[start:start + size]
        if piece: result.append(" ".join(piece))
        if start + size >= len(words): break
    return result

def chunk_document(document_id: str, text: str, source: str, metadata: dict | None = None) -> list[Chunk]:
    metadata = metadata or {}
    structured = bool(metadata) or "\n" in text
    if len(text.split()) <= 140:
        strategy, pieces = "semantic", semantic_chunks(text)
    elif structured:
        strategy, pieces = "metadata_aware", semantic_chunks(text, 120)
    else:
        strategy, pieces = "sliding_window", sliding_chunks(text)
    return [Chunk(f"{document_id}:{i}", document_id, piece, source,
                  {**metadata, "chunk_strategy": strategy, "position": i}) for i, piece in enumerate(pieces)]
