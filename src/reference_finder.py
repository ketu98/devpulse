from __future__ import annotations

import html
import os
import re
from urllib.parse import quote_plus
import requests


SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "DevPulse/3.0 (+https://github.com/ketu98/devpulse)"
})


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(text or "")).strip()


def _valid_http_url(url: str) -> bool:
    if not url or not url.startswith(("http://", "https://")):
        return False
    try:
        r = SESSION.get(url, timeout=15, allow_redirects=True, stream=True)
        return 200 <= r.status_code < 400
    except requests.RequestException:
        return False


def search_microsoft_learn(topic: str, limit: int = 2):
    """Use Microsoft's public Learn search API; URLs come from the API, never from the LLM."""
    url = "https://learn.microsoft.com/api/search"
    params = {
        "search": topic,
        "locale": "en-us",
        "$top": max(limit * 3, 6)
    }

    results = []
    try:
        r = SESSION.get(url, params=params, timeout=25)
        r.raise_for_status()
        payload = r.json()
        for item in payload.get("results", []):
            item_url = item.get("url")
            title = _clean(item.get("title"))
            description = _clean(item.get("description"))
            if not item_url or not title:
                continue
            if item_url.startswith("/"):
                item_url = "https://learn.microsoft.com" + item_url
            if "learn.microsoft.com" not in item_url:
                continue
            results.append({
                "type": "article",
                "source": "Microsoft Learn",
                "title": title,
                "url": item_url,
                "description": description[:240]
            })
            if len(results) >= limit:
                break
    except Exception as ex:
        print(f"Microsoft Learn search failed: {ex}")

    return results


def search_arxiv(topic: str, limit: int = 1):
    """Fetch an actual arXiv result for AI topics."""
    query = quote_plus(f'all:"{topic}"')
    url = (
        "https://export.arxiv.org/api/query"
        f"?search_query={query}&start=0&max_results={limit}"
        "&sortBy=relevance&sortOrder=descending"
    )

    results = []
    try:
        text = SESSION.get(url, timeout=25).text
        entries = re.findall(r"<entry>(.*?)</entry>", text, flags=re.S)
        for entry in entries[:limit]:
            title_m = re.search(r"<title>(.*?)</title>", entry, flags=re.S)
            id_m = re.search(r"<id>(.*?)</id>", entry, flags=re.S)
            summary_m = re.search(r"<summary>(.*?)</summary>", entry, flags=re.S)
            if not (title_m and id_m):
                continue
            results.append({
                "type": "paper",
                "source": "arXiv",
                "title": _clean(title_m.group(1)),
                "url": _clean(id_m.group(1)),
                "description": _clean(summary_m.group(1) if summary_m else "")[:240]
            })
    except Exception as ex:
        print(f"arXiv search failed: {ex}")
    return results


def search_youtube(topic: str):
    """
    Uses the official YouTube Data API when YOUTUBE_API_KEY is present.
    If no key exists, returns a YouTube search URL rather than inventing a video.
    """
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()

    if not key:
        return {
            "type": "video-search",
            "source": "YouTube",
            "title": f"YouTube results for {topic}",
            "url": f"https://www.youtube.com/results?search_query={quote_plus(topic + ' tutorial')}"
        }

    endpoint = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": topic + " tutorial",
        "type": "video",
        "maxResults": 5,
        "order": "relevance",
        "key": key,
        "safeSearch": "strict"
    }

    try:
        r = SESSION.get(endpoint, params=params, timeout=25)
        r.raise_for_status()
        data = r.json()

        for item in data.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            snippet = item.get("snippet", {})
            title = _clean(snippet.get("title"))
            channel = _clean(snippet.get("channelTitle"))
            if not video_id:
                continue
            return {
                "type": "video",
                "source": "YouTube",
                "title": title,
                "channel": channel,
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }
    except Exception as ex:
        print(f"YouTube search failed: {ex}")

    return {
        "type": "video-search",
        "source": "YouTube",
        "title": f"YouTube results for {topic}",
        "url": f"https://www.youtube.com/results?search_query={quote_plus(topic + ' tutorial')}"
    }


def find_references(category: str, topic: str):
    references = []

    references.extend(search_microsoft_learn(topic, limit=2))

    if category == "ai":
        references.extend(search_arxiv(topic, limit=1))

    # De-duplicate URLs while retaining order.
    seen = set()
    unique = []
    for ref in references:
        url = ref.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        unique.append(ref)

    video = search_youtube(topic)

    return {
        "references": unique[:3],
        "video": video
    }
