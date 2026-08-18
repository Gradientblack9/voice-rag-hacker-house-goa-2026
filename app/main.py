from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.retrieval.hybrid import HybridStore
from app.harness.pipeline import VoiceRAGPipeline
from app.api.routes import build_router

store=HybridStore(settings.index_path); store.load()
app=FastAPI(title="Voice RAG",version="0.1.0")
app.include_router(build_router(VoiceRAGPipeline(store)))
@app.get("/health")
async def health(): return {"status":"ok","indexed_chunks":len(store.records)}
app.mount("/",StaticFiles(directory="frontend",html=True),name="frontend")
