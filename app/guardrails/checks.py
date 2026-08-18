import re
UNSAFE = re.compile(r"\b(kill|murder|bomb|suicide|self harm|explosive)\b", re.I)
OFF_TOPIC = re.compile(r"\b(weather|stock price|celebrity gossip|football score)\b", re.I)
def input_decision(query: str) -> str | None:
    if UNSAFE.search(query): return "unsafe_input"
    if OFF_TOPIC.search(query): return "off_topic"
    return None
def grounded(answer: str, evidence: list[dict]) -> bool:
    words = {w for w in re.findall(r"\w+", answer.lower()) if len(w)>3}
    context = set().union(*(set(re.findall(r"\w+", x["text"].lower())) for x in evidence)) if evidence else set()
    return bool(words) and len(words & context) / len(words) >= .55

_QUERY_STOPWORDS = {
    "a", "an", "the", "what", "which", "who", "where", "when", "why", "how",
    "is", "are", "was", "were", "of", "in", "to", "for", "and", "does", "do",
}

def evidence_sufficient(query: str, evidence: list[dict]) -> bool:
    """Reject weak one-word matches before generation.

    This intentionally favors an explicit abstention over a plausible but
    incorrect answer when the small local index lacks the requested fact.
    """
    important = {
        word for word in re.findall(r"\w+", query.lower())
        if len(word) > 2 and word not in _QUERY_STOPWORDS
    }
    if not important or not evidence:
        return False
    context = set().union(*(set(re.findall(r"\w+", item["text"].lower())) for item in evidence))
    required = len(important) if len(important) <= 2 else max(2, round(len(important) * .7))
    return len(important & context) >= required
