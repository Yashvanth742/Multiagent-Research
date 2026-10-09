"""Direct SerpApi search helpers used by the research workflow."""

import os
from typing import Any

import serpapi
from dotenv import load_dotenv

load_dotenv()

client = serpapi.Client(api_key=os.getenv("SERPAPI_API_KEY"))
MAX_RESULTS_PER_SEARCH = 10


def _payload_dict(results: Any) -> dict[str, Any]:
    if hasattr(results, "as_dict"):
        results = results.as_dict()
    return results if isinstance(results, dict) else {}


def _text(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("summary") or value.get("name") or value.get("date") or ""
    elif isinstance(value, list):
        value = "; ".join(str(part) for part in value if part)
    return " ".join(str(value or "").split())


def _extract_results(results: Any, collection: str) -> list[dict[str, str]]:
    """Keep human-facing result evidence and discard SerpApi metadata."""
    candidates = _payload_dict(results).get(collection)
    if not isinstance(candidates, list):
        return []

    extracted = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        publication = item.get("publication_info")
        if isinstance(publication, dict):
            publication_source = publication.get("summary") or publication.get("source")
            publication_date = publication.get("date")
        else:
            publication_source = publication
            publication_date = None

        record = {
            "title": _text(item.get("title")),
            "snippet": _text(item.get("snippet") or item.get("description")),
            "url": _text(item.get("link") or item.get("url")),
            "source": _text(item.get("source") or item.get("publisher") or publication_source),
            "date": _text(item.get("date") or item.get("published") or publication_date),
        }
        if any(record.values()):
            extracted.append(record)
        if len(extracted) == MAX_RESULTS_PER_SEARCH:
            break
    return extracted
