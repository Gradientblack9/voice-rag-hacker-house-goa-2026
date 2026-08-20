"""Fast local provider used until a configured LLM adapter is selected."""
import re
from app.retrieval.hybrid import tokens
def answer(query: str, evidence: list[dict]) -> str:
    if evidence:
        metadata=evidence[0].get("metadata", {})
        uses_indic_script=bool(re.search(r"[^\x00-\x7f]", query))
        supplied=(metadata.get("answer") if uses_indic_script else metadata.get("english_answer")) or ""
        if supplied.strip(): return supplied.strip()
    q = set(tokens(query))
    current_question = any(phrase in query.lower() for phrase in ("what is", "what's", "current", "today"))
    historical = ("in 16", "in 17", "in 18", "in 19", "in 20", "was the capital", "moved the capital", "formerly")
    sentences=[]
    seen=set()
    # Keep synthesis within the strongest passage; mixing lower-ranked passages
    # was producing unrelated sentence combinations.
    for item in evidence[:1]:
        for sentence in re.split(r"(?<=[.!?।])\s+", item["text"].replace("\n", " ")):
            normalized=sentence.strip().lower()
            if not normalized or normalized in seen: continue
            seen.add(normalized)
            # A dated/historical statement cannot safely answer a present-tense
            # factual request unless the user explicitly asks about history.
            if current_question and any(marker in normalized for marker in historical): continue
            score=len(q & set(tokens(sentence)))
            if current_question and re.search(r"\b(?:is|means|refers to|defined as)\b", sentence, re.I): score += .25
            sentences.append((score, sentence.strip()))
    best = [s for score,s in sorted(sentences, reverse=True)[:2] if score]
    return ". ".join(best) + ("." if best else "")
