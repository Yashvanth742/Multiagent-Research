from . import MAX_RESULTS_PER_SEARCH, _payload_dict, _text, client


def run_image_search(query: str) -> list[dict[str, str]]:
    """Run one Google Images search and return useful image fields."""
    results = client.search({"engine": "google_images", "q": query})
    image_results = _payload_dict(results).get("images_results")
    if not isinstance(image_results, list):
        return []

    extracted = []
    for item in image_results:
        if not isinstance(item, dict):
            continue
        record = {
            "title": _text(item.get("title")),
            "thumbnail_url": _text(item.get("thumbnail") or item.get("thumbnail_url")),
            "original_url": _text(item.get("original") or item.get("original_url")),
            "source_page_url": _text(item.get("link") or item.get("source_page_url") or item.get("url")),
            "source_name": _text(item.get("source") or item.get("source_name")),
        }
        if any(record.values()):
            extracted.append(record)
        if len(extracted) == MAX_RESULTS_PER_SEARCH:
            break
    return extracted
