"""Fast local provider used until a configured LLM adapter is selected."""
from app.retrieval.hybrid import tokens
def answer(query: str, evidence: list[dict]) -> str:
    q = set(tokens(query))
    current_question = any(phrase in query.lower() for phrase in ("what is", "what's", "current", "today"))
    historical = ("in 16", "in 17", "in 18", "in 19", "in 20", "was the capital", "moved the capital", "formerly")
    sentences=[]
    seen=set()
    for item in evidence:
        for sentence in item["text"].replace("\n", " ").split("."):
            normalized=sentence.strip().lower()
            if not normalized or normalized in seen: continue
            seen.add(normalized)
            # A dated/historical statement cannot safely answer a present-tense
            # factual request unless the user explicitly asks about history.
            if current_question and any(marker in normalized for marker in historical): continue
            score=len(q & set(tokens(sentence)))
            sentences.append((score, sentence.strip()))
    best = [s for score,s in sorted(sentences, reverse=True)[:2] if score]
    return ". ".join(best) + ("." if best else "")
