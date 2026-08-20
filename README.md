# Voice RAG — Hacker House Goa 2026

An end-to-end, evidence-first Voice RAG service: audio is transcribed by a replaceable Sarvam adapter, then routed through safety checks, hybrid retrieval, an extractive/local generation adapter, grounding verification, and typed API responses.

The landing experience includes selectable English, Hindi, Bengali, Tamil and Telugu speech/UI modes, Sarvam automatic language detection, persistent light/dark appearance settings, and a microphone-reactive voice button whose glow follows live input volume.

The default assistant is closed-corpus: it answers questions present in the local MSMARCO-XI index and abstains when it cannot verify an answer. Working examples are shown below the voice button, including “What is a corporation?”, “What is honesty?”, and “Why did Rachel Carson write An Obligation to Endure?”. Greetings such as “Hey model” return this guidance directly.

Local ingestion writes the full `data/index.json`, an ignored compact build artifact at `data/index-lite.json`, and a compressed generated Python module containing verified answer rows for serverless deployment. The app automatically reconstructs this embedded index when the full local index is unavailable.

## Architecture

`voice → Sarvam STT → validation/guardrails → hybrid vector + keyword retrieval → grounded generator → grounding check → response`

The harness records per-stage timing and every answer includes provenance citations. It abstains for unsafe, off-topic, insufficient-evidence, or ungrounded requests.

## Dataset and indexing

The ingestion script uses the official `ai4bharat/MSMARCO-XI` dataset. It prints the fields present in the downloaded dataset and indexes passage/text/context fields it finds. Indexing is offline. The chunk router selects sentence-semantic chunks for short text, metadata-aware semantic chunks for structured records, and overlapping sliding windows otherwise. Every chunk preserves its source, document ID, strategy, and position.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install datasets
python scripts/ingest.py --limit 5000
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. Configure `SARVAM_API_KEY` in a private `.env` before voice queries. `POST /api/v1/query` works without provider credentials; `POST /api/v1/voice-query` uses Sarvam. `GET /api/v1/metrics` reports live P50/P70/P100.

## Measured benchmark

Run `python scripts/benchmark.py --queries 100` after indexing. The runner selects 100 distinct source queries spread across the 26,991-chunk MSMARCO-XI index, disables optional network fallback, excludes one-time index loading, reports all required percentiles and per-stage averages, and writes `data/benchmark_results.json`.

Measured locally on August 19, 2026 after bounded hybrid candidate selection:

| Metric | Result |
|---|---:|
| P50 | 18.454 ms |
| P70 | 23.991 ms |
| P100 / max | 45.299 ms |
| Mean | 15.983 ms |
| Errors | 0 / 100 |

This result meets the `<200 ms` target for the local text retrieval, extractive generation, and grounding pipeline. It is not presented as a voice end-to-end result: Sarvam is a remote STT service and must be benchmarked separately with real audio from the final deployment region. The complete machine-readable result is in `data/benchmark_results.json`.

## Limitations

The default generation provider is intentionally extractive for fast, reproducible local operation. Add a production LLM adapter behind `app/generation/` for richer synthesis, then re-run benchmarks. End-to-end under-200ms performance depends on Sarvam network latency and the deployment region; do not claim the voice target until a real-audio benchmark verifies it.
