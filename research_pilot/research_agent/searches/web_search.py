from . import _extract_results, client


def run_web_search(query: str) -> list[dict[str, str]]:
    """Run one Google web search and return up to 10 clean results."""
    results = client.search({"engine": "google", "q": query})
    return _extract_results(results, "organic_results")
