"""Cited public-reference fallback for factual queries missing from MSMARCO-XI."""
import re
from urllib.parse import quote
import httpx

_CACHE: dict[str, dict] = {}

def _topic_query(query: str) -> str:
    """Turn conversational questions into an encyclopedia topic lookup."""
    cleaned = query.strip().rstrip("?.!")
    capital = re.search(r"\bcapital\s+of\s+(.+)$", cleaned, re.I)
    if capital:
        return capital.group(1).strip()
    subject = re.match(r"^(?:what|who|where)\s+(?:is|was|are)\s+(?:the\s+)?(.+)$", cleaned, re.I)
    if subject:
        return subject.group(1).strip()
    return cleaned

def prefers_reference(query: str) -> bool:
    """True for direct entity/fact questions suited to an encyclopedia."""
    cleaned = query.strip().rstrip("?.!")
    return _topic_query(query).casefold() != cleaned.casefold()

async def wikipedia_evidence(query: str) -> dict | None:
    """Return one structured, attributable summary or None on any lookup failure."""
    topic = _topic_query(query)
    cache_key = topic.casefold()
    if cache_key in _CACHE:
        return _CACHE[cache_key]
    params = {"action": "query", "list": "search", "srsearch": topic, "format": "json", "srlimit": 1}
    try:
        headers = {
            "User-Agent": "VoiceRAGDemo/0.1 (contact: local-demo@example.com)",
            "Api-User-Agent": "VoiceRAGDemo/0.1",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=8, headers=headers, follow_redirects=True, trust_env=False) as client:
            # Entity-style questions can go directly to the summary endpoint,
            # avoiding a second network round trip.
            title = topic
            summary_response = await client.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}")
            if summary_response.status_code == 404:
                search_response = await client.get("https://en.wikipedia.org/w/api.php", params=params)
                search_response.raise_for_status()
                matches = search_response.json().get("query", {}).get("search", [])
                if not matches: return None
                title = matches[0]["title"]
                summary_response = await client.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title)}")
            summary_response.raise_for_status()
            summary = summary_response.json()
    except (httpx.HTTPError, ValueError, KeyError):
        return None
    text = summary.get("extract", "").strip()
    if not text: return None
    url = summary.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{quote(title)}")
    result = {"chunk_id": f"wikipedia:{title}", "document_id": "wikipedia", "text": text,
              "source": f"Wikipedia — {title}", "metadata": {"url": url, "fallback": True},
              "score": .95, "retrieval_method": "wikipedia_fallback"}
    _CACHE[cache_key] = result
    return result
