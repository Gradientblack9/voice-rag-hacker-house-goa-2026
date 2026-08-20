import logging
import base64
import gzip
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.retrieval.hybrid import HybridStore, vector
from app.harness.pipeline import VoiceRAGPipeline
from app.api.routes import build_router

ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"
INDEX_PATH = ROOT_DIR / settings.index_path

store = HybridStore(str(INDEX_PATH))
try:
    store.load()
except (OSError, ValueError) as exc:
    # A production deployment uses an external/vector-backed index. Do not
    # bring down the entire UI when the large local development index is absent.
    logging.getLogger(__name__).exception("Index could not be loaded: %s", exc)
if not store.records:
    try:
        from app.index_lite_data import DATA
        store.records=json.loads(gzip.decompress(base64.b85decode(DATA)).decode("utf-8"))
        for record in store.records: record["vector"]=vector(record["text"])
        store._build_index()
    except (ImportError, OSError, ValueError, json.JSONDecodeError) as exc:
        logging.getLogger(__name__).exception("Embedded index could not be loaded: %s", exc)
app=FastAPI(title="Voice RAG",version="0.1.0")
app.include_router(build_router(VoiceRAGPipeline(store)))
@app.get("/health")
async def health():
    return {"status":"ok","indexed_chunks":len(store.records),"index_available":bool(store.records)}

if FRONTEND_DIR.is_dir():
    app.mount("/",StaticFiles(directory=str(FRONTEND_DIR), html=True),name="frontend")
else:
    logging.getLogger(__name__).error("Frontend directory is missing: %s", FRONTEND_DIR)
