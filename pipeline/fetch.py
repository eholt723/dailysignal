"""
Fetch content from all sources: HackerNews, Product Hunt, and RSS feeds.
Returns a list of raw item dicts: {source, title, url, dedup_hash}
"""

import hashlib
import httpx
import feedparser

RSS_FEEDS = [
    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("VentureBeat", "https://venturebeat.com/feed/"),
    ("GitHub Blog", "https://github.blog/feed/"),
    ("Hugging Face", "https://huggingface.co/blog/feed.xml"),
    ("a16z", "https://a16z.com/feed/"),
]

HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
HN_LIMIT = 30

PRODUCT_HUNT_GRAPHQL = "https://api.producthunt.com/v2/api/graphql"


def _hash(title: str, url: str) -> str:
    key = f"{title}|{url}".lower().strip()
    return hashlib.sha256(key.encode()).hexdigest()


def fetch_rss() -> list[dict]:
    items = []
    for source, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                if title and link:
                    items.append({
                        "source": source,
                        "title": title,
                        "url": link,
                        "dedup_hash": _hash(title, link),
                    })
        except Exception as e:
            print(f"[fetch_rss] {source} failed: {e}")
    return items


def fetch_hackernews() -> list[dict]:
    items = []
    try:
        with httpx.Client(timeout=10) as client:
            top_ids = client.get(HN_TOP_URL).json()[:HN_LIMIT]
            for story_id in top_ids:
                try:
                    story = client.get(HN_ITEM_URL.format(story_id)).json()
                    title = story.get("title", "").strip()
                    url = story.get("url", f"https://news.ycombinator.com/item?id={story_id}")
                    if title:
                        items.append({
                            "source": "HackerNews",
                            "title": title,
                            "url": url,
                            "dedup_hash": _hash(title, url),
                        })
                except Exception:
                    continue
    except Exception as e:
        print(f"[fetch_hackernews] failed: {e}")
    return items


def fetch_product_hunt(api_key: str) -> list[dict]:
    query = """
    {
      posts(first: 20, order: VOTES) {
        edges {
          node {
            name
            tagline
            website
          }
        }
      }
    }
    """
    items = []
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(
                PRODUCT_HUNT_GRAPHQL,
                json={"query": query},
                headers={"Authorization": f"Bearer {api_key}"},
            )
            resp.raise_for_status()
            edges = resp.json()["data"]["posts"]["edges"]
            for edge in edges:
                node = edge["node"]
                title = f"{node['name']} — {node['tagline']}"
                url = node.get("website", "https://producthunt.com")
                items.append({
                    "source": "Product Hunt",
                    "title": title,
                    "url": url,
                    "dedup_hash": _hash(title, url),
                })
    except Exception as e:
        print(f"[fetch_product_hunt] failed: {e}")
    return items


def fetch_all(product_hunt_api_key: str) -> list[dict]:
    items = []
    items.extend(fetch_rss())
    items.extend(fetch_hackernews())
    items.extend(fetch_product_hunt(product_hunt_api_key))
    print(f"[fetch_all] fetched {len(items)} total items")
    return items
