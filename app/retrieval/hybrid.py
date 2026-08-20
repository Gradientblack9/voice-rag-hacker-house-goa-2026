import hashlib, heapq, json, math, re, time
from pathlib import Path
from collections import Counter, defaultdict
from app.chunking.router import Chunk
from app.config import settings

def tokens(text: str) -> list[str]: return re.findall(r"[\w']+", text.lower())
def vector(text: str, dimensions: int = 256) -> list[float]:
    values = [0.0] * dimensions
    for word in tokens(text): values[int(hashlib.sha256(word.encode()).hexdigest(), 16) % dimensions] += 1
    norm = math.sqrt(sum(x*x for x in values)) or 1
    return [x/norm for x in values]
def query_vector(text: str, dimensions: int = 256) -> dict[int, float]:
    """Sparse query vector compatible with the stored dense document vectors."""
    counts = Counter(int(hashlib.sha256(word.encode()).hexdigest(), 16) % dimensions for word in tokens(text))
    norm = math.sqrt(sum(value * value for value in counts.values())) or 1
    return {index: value / norm for index, value in counts.items()}
def cosine(a, b): return sum(x*y for x,y in zip(a,b))

class HybridStore:
    def __init__(self, path: str):
        self.path, self.records = Path(path), []
        self._postings, self._token_counts, self._indexed_count = defaultdict(set), [], 0
    def load(self):
        if self.path.exists():
            self.records = json.loads(self.path.read_text(encoding="utf-8"))
            self._build_index()
    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(f"{self.path.name}.tmp")
        temporary.write_text(json.dumps(self.records), encoding="utf-8")
        temporary.replace(self.path)
    def add(self, chunks: list[Chunk]):
        self.records.extend({"chunk_id": c.chunk_id, "document_id": c.document_id, "text": c.text, "source": c.source,
                             "metadata": c.metadata, "vector": vector(c.text)} for c in chunks)
    def _build_index(self):
        self._postings, self._token_counts = defaultdict(set), []
        for index, item in enumerate(self.records):
            # MSMARCO-XI's source query is useful retrieval metadata. Index it
            # with the passage while preserving passage-only answer context.
            metadata = item.get("metadata", {})
            source_query = str(metadata.get("query", ""))
            english_query = str(metadata.get("english_query", ""))
            counts = Counter(tokens(f'{source_query} {english_query} {item["text"]}'))
            self._token_counts.append(counts)
            for word in counts: self._postings[word].add(index)
        self._indexed_count = len(self.records)
    def embed_query(self, query: str) -> dict[int, float]:
        return query_vector(query)
    def search(self, query: str, k: int = 4) -> list[dict]:
        return self.search_timed(query, k)[0]
    def search_timed(self, query: str, k: int = 4, qv: dict[int, float] | None = None) -> tuple[list[dict], float, float]:
        keyword_start = time.perf_counter()
        if self._indexed_count != len(self.records): self._build_index()
        qtokens = tokens(query)
        normalized_query = " ".join(qtokens)
        stopwords = {"a","an","the","what","which","who","where","when","why","how","is","are","was","were","of","in","to","for","and","does","do"}
        meaningful = {word for word in qtokens if len(word) > 2 and word not in stopwords} or set(qtokens)
        total_docs = max(1, len(self.records))
        # Cheap keyword/IDF preselection bounds the expensive Python vector
        # rerank. This removes long-tail scans over tens of thousands of chunks.
        preliminary = defaultdict(float)
        for word in meaningful:
            posting = self._postings.get(word)
            if not posting: continue
            weight = math.log((total_docs + 1) / (len(posting) + 1))
            for index in posting: preliminary[index] += weight
        if not preliminary: return [], (time.perf_counter() - keyword_start) * 1000, 0.0
        limit = max(k, settings.retrieval_candidates)
        if len(preliminary) > limit:
            candidates = heapq.nlargest(limit, preliminary, key=preliminary.get)
        else:
            candidates = preliminary.keys()
        keyword_ms = (time.perf_counter() - keyword_start) * 1000
        rerank_start = time.perf_counter()
        qv, scored = qv or query_vector(query), []
        for index in candidates:
            item, counts = self.records[index], self._token_counts[index]
            matched = meaningful & counts.keys()
            coverage = len(matched) / max(1, len(meaningful))
            rarity = sum(math.log((total_docs + 1) / (len(self._postings[word]) + 1)) for word in matched)
            rarity_norm = rarity / max(1.0, len(meaningful) * math.log(total_docs + 1))
            semantic = sum(item["vector"][position] * weight for position, weight in qv.items())
            phrase_bonus = .08 if " ".join(qtokens) in item["text"].lower() else 0
            metadata = item.get("metadata", {})
            source_queries = {
                " ".join(tokens(str(metadata.get("query", "")))),
                " ".join(tokens(str(metadata.get("english_query", "")))),
            }
            source_query_bonus = .18 if normalized_query and normalized_query in source_queries else 0
            score = .68 * coverage + .22 * rarity_norm + .10 * semantic + phrase_bonus + source_query_bonus
            scored.append({**item, "score": round(min(score, 1.0), 4), "retrieval_method": "hybrid"})
        hits = heapq.nlargest(k, scored, key=lambda item: item["score"])
        return hits, keyword_ms, (time.perf_counter() - rerank_start) * 1000
