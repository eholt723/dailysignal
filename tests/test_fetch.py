"""Tests for pipeline/fetch.py"""

import pytest
from unittest.mock import MagicMock, patch
from fetch import _hash, fetch_rss, fetch_hackernews, fetch_product_hunt, fetch_all


class TestHash:
    def test_deterministic(self):
        assert _hash("title", "https://example.com") == _hash("title", "https://example.com")

    def test_different_inputs_differ(self):
        assert _hash("title A", "https://a.com") != _hash("title B", "https://b.com")

    def test_case_insensitive(self):
        assert _hash("Title", "https://Example.com") == _hash("title", "https://example.com")

    def test_returns_64_char_hex(self):
        result = _hash("title", "https://example.com")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)


class TestFetchRss:
    def test_returns_items_from_feed(self, mocker):
        mock_entry = MagicMock()
        mock_entry.get = lambda k, d="": {"title": "Test Article", "link": "https://example.com/1"}.get(k, d)

        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]

        mocker.patch("fetch.feedparser.parse", return_value=mock_feed)

        items = fetch_rss()
        assert len(items) > 0
        assert items[0]["title"] == "Test Article"
        assert items[0]["url"] == "https://example.com/1"
        assert "dedup_hash" in items[0]

    def test_skips_entries_without_title(self, mocker):
        mock_entry = MagicMock()
        mock_entry.get = lambda k, d="": {"title": "", "link": "https://example.com"}.get(k, d)

        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]

        mocker.patch("fetch.feedparser.parse", return_value=mock_feed)

        items = fetch_rss()
        assert items == []

    def test_continues_on_source_failure(self, mocker):
        mocker.patch("fetch.feedparser.parse", side_effect=Exception("timeout"))
        # should not raise
        items = fetch_rss()
        assert items == []

    def test_source_field_matches_feed_name(self, mocker):
        mock_entry = MagicMock()
        mock_entry.get = lambda k, d="": {"title": "Article", "link": "https://techcrunch.com/1"}.get(k, d)
        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]

        mocker.patch("fetch.feedparser.parse", return_value=mock_feed)
        items = fetch_rss()
        sources = {item["source"] for item in items}
        # all sources should be from the RSS_FEEDS list
        assert sources.issubset({"TechCrunch", "VentureBeat", "GitHub Blog", "Hugging Face", "a16z"})


class TestFetchHackerNews:
    def test_returns_items(self, mocker):
        mock_client = MagicMock()
        mock_client.__enter__ = lambda s: s
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.side_effect = [
            MagicMock(json=lambda: [1, 2]),
            MagicMock(json=lambda: {"title": "Story One", "url": "https://example.com/1"}),
            MagicMock(json=lambda: {"title": "Story Two", "url": "https://example.com/2"}),
        ]
        mocker.patch("fetch.httpx.Client", return_value=mock_client)

        items = fetch_hackernews()
        assert len(items) == 2
        assert items[0]["source"] == "HackerNews"
        assert items[0]["title"] == "Story One"

    def test_uses_hn_url_fallback_when_no_url(self, mocker):
        mock_client = MagicMock()
        mock_client.__enter__ = lambda s: s
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.side_effect = [
            MagicMock(json=lambda: [99]),
            MagicMock(json=lambda: {"title": "Ask HN: something", "id": 99}),
        ]
        mocker.patch("fetch.httpx.Client", return_value=mock_client)

        items = fetch_hackernews()
        assert "ycombinator.com" in items[0]["url"]

    def test_handles_network_failure(self, mocker):
        mocker.patch("fetch.httpx.Client", side_effect=Exception("connection refused"))
        items = fetch_hackernews()
        assert items == []


class TestFetchProductHunt:
    def test_returns_items(self, mocker):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "posts": {
                    "edges": [
                        {"node": {"name": "CoolApp", "tagline": "Does cool things", "website": "https://coolapp.io"}},
                    ]
                }
            }
        }
        mock_client = MagicMock()
        mock_client.__enter__ = lambda s: s
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response

        mocker.patch("fetch.httpx.Client", return_value=mock_client)

        items = fetch_product_hunt(api_key="test_key")
        assert len(items) == 1
        assert items[0]["source"] == "Product Hunt"
        assert "CoolApp" in items[0]["title"]
        assert items[0]["url"] == "https://coolapp.io"

    def test_handles_api_failure(self, mocker):
        mock_client = MagicMock()
        mock_client.__enter__ = lambda s: s
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.side_effect = Exception("401 Unauthorized")

        mocker.patch("fetch.httpx.Client", return_value=mock_client)

        items = fetch_product_hunt(api_key="bad_key")
        assert items == []


class TestFetchAll:
    def test_combines_all_sources(self, mocker):
        mocker.patch("fetch.fetch_rss", return_value=[{"source": "TechCrunch", "title": "A", "url": "u1", "dedup_hash": "h1"}])
        mocker.patch("fetch.fetch_hackernews", return_value=[{"source": "HackerNews", "title": "B", "url": "u2", "dedup_hash": "h2"}])
        mocker.patch("fetch.fetch_product_hunt", return_value=[{"source": "Product Hunt", "title": "C", "url": "u3", "dedup_hash": "h3"}])

        items = fetch_all(product_hunt_api_key="key")
        assert len(items) == 3
        sources = {i["source"] for i in items}
        assert sources == {"TechCrunch", "HackerNews", "Product Hunt"}
