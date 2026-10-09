from . import _extract_results, client


def run_news_search(query: str) -> list[dict[str, str]]:
    """Run one Google News search and return up to 10 clean results."""
    results = client.search({"engine": "google_news", "q": query})
    return _extract_results(results, "news_results")
