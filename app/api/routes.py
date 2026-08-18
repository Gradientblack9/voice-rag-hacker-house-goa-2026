import time
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.models.schemas import QueryRequest, VoiceRAGResponse
from app.harness.pipeline import VoiceRAGPipeline
from app.stt.sarvam import SarvamSTT
from app.config import settings
from app.observability.metrics import metrics

def build_router(pipeline: VoiceRAGPipeline):
    router=APIRouter(prefix="/api/v1")
    @router.post("/query",response_model=VoiceRAGResponse)
    async def query(payload: QueryRequest): return await pipeline.run_text(payload.query)
    @router.post("/voice-query",response_model=VoiceRAGResponse)
    async def voice_query(audio: UploadFile=File(...)):
        start=time.perf_counter()
        try: transcript=await SarvamSTT(settings.sarvam_api_key).transcribe(audio.filename or "audio.webm",await audio.read())
        except ValueError as exc: raise HTTPException(503,detail=str(exc)) from exc
        return await pipeline.run_text(transcript, transcript, (time.perf_counter()-start)*1000)
    @router.get("/metrics")
    async def get_metrics(): return metrics.snapshot()
    return router
