"""Build a reproducible local JSON index from ai4bharat/MSMARCO-XI."""
import argparse
import sys
from pathlib import Path

# Support `python scripts/ingest.py` as documented, not only module execution.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.chunking.router import chunk_document
from app.retrieval.hybrid import HybridStore
from app.config import settings
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--split", default="validation")
    parser.add_argument("--language", default="hi", help="MSMARCO-XI language config, e.g. hi, ta, te")
    parser.add_argument("--limit",type=int,default=5000)
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
        text = "\n".join(passage_text) if isinstance(passage_text, list) else str(passage_text)
        # The answer is indexed with its retrieved passages so both facts and
        # source provenance remain available at query time.
        text = "\n".join(part for part in [row.get("Answer", ""), text] if part)
        if text: store.add(chunk_document(str(row.get("query_id",i)), text, "ai4bharat/MSMARCO-XI", {"fields": fields, "language": args.language, "query": row.get("query", "")}))
    store.save(); print({"dataset_file":filename,"dataset_fields":fields or [],"indexed_chunks":len(store.records),"path":str(store.path)})
if __name__=="__main__": main()
