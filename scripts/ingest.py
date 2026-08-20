"""Build a reproducible local JSON index from ai4bharat/MSMARCO-XI."""
import argparse
import sys
from pathlib import Path

# Support `python scripts/ingest.py` as documented, not only module execution.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.chunking.router import chunk_document
from app.retrieval.hybrid import HybridStore
from app.config import settings

def _as_text_list(value) -> list[str]:
    """Normalize Parquet/NumPy passage arrays without stringifying the array."""
    if value is None: return []
    if hasattr(value, "tolist"): value=value.tolist()
    if not isinstance(value, (list, tuple)): value=[value]
    return [str(item).strip() for item in value if item is not None and str(item).strip()]

def _usable_answer(value) -> str:
    answers=_as_text_list(value)
    if not answers: return ""
    text=" ".join(answers).strip()
    normalized=text.casefold().strip(" .")
    no_answer_markers=("कोई उत्तर नहीं मिला", "no answer", "answer not found", "not available", "n/a")
    return "" if any(marker in normalized for marker in no_answer_markers) else text

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--split", default="validation")
    parser.add_argument("--language", default="hi", help="MSMARCO-XI language config, e.g. hi, ta, te")
    parser.add_argument("--limit",type=int,default=5000)
    parser.add_argument("--lite-limit",type=int,default=2000,help="Answered rows bundled for serverless deployment")
    args=parser.parse_args()
    try:
        import pandas as pd
        from huggingface_hub import hf_hub_download
    except ImportError as exc: raise SystemExit("Install datasets: pip install datasets") from exc
    codes = {"hi": "hin", "ta": "tam", "te": "tel", "bn": "ben", "kn": "kan", "ml": "mal", "mr": "mar", "ne": "nep", "or": "ory", "pa": "pan", "sa": "san", "ur": "urd"}
    code = codes.get(args.language, args.language)
    filename = f"{args.split}/{code}{'val' if args.split == 'validation' else 'train'}.parquet"
    try:
        local_file = hf_hub_download(repo_id="ai4bharat/MSMARCO-XI", repo_type="dataset", filename=filename)
    except Exception as exc:
        raise SystemExit(f"Could not download {filename} from MSMARCO-XI: {exc}") from exc
    frame = pd.read_parquet(local_file).head(args.limit)
    store=HybridStore(settings.index_path); store.records=[]
    lite_store=HybridStore("data/index-lite.json"); lite_store.records=[]
    fields = None
    for i, raw_row in frame.iterrows():
        row = raw_row.to_dict()
        fields = list(row.keys())
        passages = row.get("passages", {})
        passage_text = passages.get("English_passages")
        # Parquet decoding returns NumPy arrays here; never use ``or`` with
        # them because their truth value is intentionally ambiguous.
        if passage_text is None or len(passage_text) == 0:
            passage_text = passages.get("Translated_passages")
        if passage_text is None:
            passage_text = []
        text = "\n".join(_as_text_list(passage_text))
        # Keep both ground-truth answers with their passages. Generation can
        # then return the answer matching the query language without trying to
        # synthesize one from unrelated lower-ranked passage sentences.
        translated_answer=_usable_answer(row.get("Answer"))
        english_answer=_usable_answer(row.get("Eng_Answer"))
        text = "\n".join(part for part in [english_answer, translated_answer, text] if part)
        metadata={"fields": fields, "language": args.language, "query": row.get("query", ""), "english_query": row.get("Eng_Query", ""), "answer": translated_answer, "english_answer": english_answer}
        if text: store.add(chunk_document(str(row.get("query_id",i)), text, "ai4bharat/MSMARCO-XI", metadata))
        if len(lite_store.records) < args.lite_limit and (english_answer or translated_answer):
            compact_metadata={key:metadata[key] for key in ("language","query","english_query","answer","english_answer")}
            compact_text="\n".join(part for part in [english_answer,translated_answer] if part)
            lite_store.add(chunk_document(str(row.get("query_id",i)),compact_text,"ai4bharat/MSMARCO-XI",compact_metadata))
    store.save(); lite_store.save()
    print({"dataset_file":filename,"dataset_fields":fields or [],"indexed_chunks":len(store.records),"path":str(store.path),"lite_chunks":len(lite_store.records),"lite_path":str(lite_store.path)})
if __name__=="__main__": main()
