"""Benchmark the distinct-query MSMARCO-XI text pipeline.

This intentionally disables optional network fallbacks. Sarvam STT is an
external network stage and must be measured separately with real audio when a
submission environment/API region is selected.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ["ENABLE_WIKIPEDIA_FALLBACK"] = "false"

from app.config import settings
from app.harness.pipeline import VoiceRAGPipeline
from app.retrieval.hybrid import HybridStore


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[int((len(ordered) - 1) * fraction)] if ordered else 0.0


def corpus_queries(store: HybridStore, count: int) -> list[str]:
    """Select distinct source queries evenly across the complete index."""
    unique: list[str] = []
    seen: set[str] = set()
    for record in store.records:
        query = str(record.get("metadata", {}).get("query", "")).strip()
        key = query.casefold()
        if query and key not in seen:
            seen.add(key)
            unique.append(query)
    if len(unique) < count:
        raise RuntimeError(f"Index has only {len(unique)} distinct metadata queries; requested {count}")
    step = len(unique) / count
    return [unique[min(int(i * step), len(unique) - 1)] for i in range(count)]


async def run(count: int, output: Path | None) -> dict:
    load_start = time.perf_counter()
    store = HybridStore(settings.index_path)
    store.load()
    load_ms = (time.perf_counter() - load_start) * 1000
    pipeline = VoiceRAGPipeline(store)
    queries = corpus_queries(store, count)

    responses = [await pipeline.run_text(query) for query in queries]
    stage_names = ("stt", "preprocessing", "embedding", "retrieval", "rerank", "generation", "grounding", "total")
    stages = {name: [getattr(response.latency_ms, name) for response in responses] for name in stage_names}
    totals = stages["total"]
    statuses = {name: sum(response.status == name for response in responses) for name in ("answered", "abstained", "rejected", "error")}
    result = {
        "benchmark": "msmarco_xi_text_pipeline",
        "target_ms": 200,
        "target_met": max(totals, default=0) < 200,
        "queries": len(responses),
        "distinct_queries": len({query.casefold() for query in queries}),
        "index_chunks": len(store.records),
        "index_load_ms_excluded_from_runtime": round(load_ms, 3),
        "p50_ms": round(percentile(totals, .50), 3),
        "p70_ms": round(percentile(totals, .70), 3),
        "p100_ms": round(max(totals, default=0), 3),
        "mean_ms": round(statistics.mean(totals), 3),
        "statuses": statuses,
        "errors": statuses["error"],
        "retries": 0,
        "stage_average_ms": {name: round(statistics.mean(values), 3) for name, values in stages.items()},
        "limitations": "Text pipeline only; measure Sarvam STT separately using real audio and the deployment region.",
    }
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("data/benchmark_results.json"))
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.queries, args.output)), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
