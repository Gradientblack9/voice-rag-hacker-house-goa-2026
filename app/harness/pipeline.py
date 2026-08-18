import time, uuid
from collections import OrderedDict
from app.config import settings
from app.models.schemas import VoiceRAGResponse, Citation, Latency
from app.retrieval.hybrid import HybridStore
from app.guardrails.checks import evidence_sufficient, input_decision, grounded
from app.generation.extractive import answer
from app.observability.metrics import metrics
from app.retrieval.wikipedia import prefers_reference, wikipedia_evidence

class VoiceRAGPipeline:
    def __init__(self, store: HybridStore): self.store, self._cache = store, OrderedDict()
    async def run_text(self, query: str, transcript: str | None = None, stt_ms: float = 0) -> VoiceRAGResponse:
        start=time.perf_counter(); latency=Latency(stt=stt_ms); request_id=str(uuid.uuid4())
        stage=time.perf_counter(); decision=input_decision(query); latency.preprocessing=(time.perf_counter()-stage)*1000
        if decision: return self._abstain(request_id, transcript or query, decision, latency, start, "I can only help with safe questions grounded in the indexed corpus.")
        cache_key=" ".join(query.lower().split())
        if cache_key in self._cache:
            cached=self._cache[cache_key].model_copy(deep=True); cached.request_id=request_id; cached.transcript=transcript or query
            cached.latency_ms=Latency(stt=stt_ms,total=stt_ms+(time.perf_counter()-start)*1000); metrics.record(cached); self._cache.move_to_end(cache_key); return cached
        stage=time.perf_counter(); hits=[]
        if settings.enable_wikipedia_fallback and prefers_reference(query):
            fallback=await wikipedia_evidence(query)
            if fallback and evidence_sufficient(query, [fallback]): hits=[fallback]
        if not hits:
            embed_stage=time.perf_counter(); qv=self.store.embed_query(query); latency.embedding=(time.perf_counter()-embed_stage)*1000
            hits, keyword_ms, rerank_ms=self.store.search_timed(query, settings.top_k, qv)
            latency.retrieval=keyword_ms; latency.rerank=rerank_ms
        else:
            latency.retrieval=(time.perf_counter()-stage)*1000
        local_is_sufficient = bool(hits) and hits[0]["score"] >= settings.grounding_threshold and evidence_sufficient(query, hits[:settings.rerank_top_k])
        if not local_is_sufficient and settings.enable_wikipedia_fallback:
            stage=time.perf_counter(); fallback=await wikipedia_evidence(query); latency.retrieval += (time.perf_counter()-stage)*1000
            if fallback: hits=[fallback]
        if (not hits or hits[0]["score"] < settings.grounding_threshold
                or not evidence_sufficient(query, hits[:settings.rerank_top_k])):
            return self._abstain(request_id, transcript or query, "insufficient_context", latency, start, "I could not find enough information in the provided knowledge base to answer reliably.")
        stage=time.perf_counter(); text=answer(query,hits[:settings.rerank_top_k]); latency.generation=(time.perf_counter()-stage)*1000
        stage=time.perf_counter(); is_grounded=grounded(text,hits); latency.grounding=(time.perf_counter()-stage)*1000
        if (not text or not is_grounded) and settings.enable_wikipedia_fallback and hits[0].get("retrieval_method") != "wikipedia_fallback":
            stage=time.perf_counter(); fallback=await wikipedia_evidence(query); latency.retrieval += (time.perf_counter()-stage)*1000
            if fallback and evidence_sufficient(query, [fallback]):
                hits=[fallback]
                stage=time.perf_counter(); text=answer(query,hits); latency.generation += (time.perf_counter()-stage)*1000
                stage=time.perf_counter(); is_grounded=grounded(text,hits); latency.grounding += (time.perf_counter()-stage)*1000
        if not text or not is_grounded: return self._abstain(request_id, transcript or query, "ungrounded_answer", latency, start, "I cannot answer reliably from the retrieved evidence.")
        latency.total=stt_ms+(time.perf_counter()-start)*1000
        response=VoiceRAGResponse(request_id=request_id,transcript=transcript or query,status="answered",answer=text,grounded=True,confidence=hits[0]["score"],citations=[Citation(chunk_id=x["chunk_id"],source=x["source"],score=x["score"]) for x in hits[:2]],latency_ms=latency)
        self._cache[cache_key]=response.model_copy(deep=True)
        if len(self._cache)>256: self._cache.popitem(last=False)
        metrics.record(response); return response
    def _abstain(self, rid, transcript, reason, latency, start, text):
        latency.total=latency.stt+(time.perf_counter()-start)*1000
        response=VoiceRAGResponse(request_id=rid,transcript=transcript,status="rejected" if reason in {"unsafe_input","off_topic"} else "abstained",answer=text,grounded=False,reason=reason,latency_ms=latency); metrics.record(response); return response
