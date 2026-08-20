import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.retrieval.hybrid import HybridStore
from app.harness.pipeline import VoiceRAGPipeline
from app.api.routes import build_router

ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"
INDEX_PATH = ROOT_DIR / settings.index_path
if not INDEX_PATH.exists():
    INDEX_PATH = ROOT_DIR / "data" / "index-lite.json"

store = HybridStore(str(INDEX_PATH))
try:
    store.load()
except (OSError, ValueError) as exc:
    # A production deployment uses an external/vector-backed index. Do not
    # bring down the entire UI when the large local development index is absent.
    logging.getLogger(__name__).exception("Index could not be loaded: %s", exc)
app=FastAPI(title="Voice RAG",version="0.1.0")
app.include_router(build_router(VoiceRAGPipeline(store)))
@app.get("/health")
async def health():
    return {"status":"ok","indexed_chunks":len(store.records),"index_available":bool(store.records)}

if FRONTEND_DIR.is_dir():
    app.mount("/",StaticFiles(directory=str(FRONTEND_DIR), html=True),name="frontend")
else:
    logging.getLogger(__name__).error("Frontend directory is missing: %s", FRONTEND_DIR)
