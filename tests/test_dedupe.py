"""Tests for pipeline/dedupe.py"""

import pytest
from unittest.mock import MagicMock, patch
from dedupe import filter_new

ITEMS = [
    {"source": "HackerNews", "title": "Story A", "url": "https://a.com", "dedup_hash": "hash_a"},
    {"source": "TechCrunch", "title": "Story B", "url": "https://b.com", "dedup_hash": "hash_b"},
    {"source": "Product Hunt", "title": "App C", "url": "https://c.com", "dedup_hash": "hash_c"},
]


def make_mock_conn(seen_hashes):
    mock_cur = MagicMock()
    mock_cur.fetchall.return_value = [(h,) for h in seen_hashes]
    mock_cur.__enter__ = lambda s: s
    mock_cur.__exit__ = MagicMock(return_value=False)

    mock_conn = MagicMock()
    mock_conn.__enter__ = lambda s: s
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value = mock_cur
    return mock_conn


class TestFilterNew:
    def test_returns_all_when_none_seen(self, mocker):
        mocker.patch("dedupe.psycopg2.connect", return_value=make_mock_conn([]))
        result = filter_new(ITEMS, db_url="postgresql://test")
        assert len(result) == 3

    def test_filters_seen_hashes(self, mocker):
        mocker.patch("dedupe.psycopg2.connect", return_value=make_mock_conn(["hash_a", "hash_b"]))
        result = filter_new(ITEMS, db_url="postgresql://test")
        assert len(result) == 1
        assert result[0]["dedup_hash"] == "hash_c"

    def test_keeps_all_new_hashes(self, mocker):
        mocker.patch("dedupe.psycopg2.connect", return_value=make_mock_conn(["hash_x"]))
        result = filter_new(ITEMS, db_url="postgresql://test")
        assert len(result) == 3

    def test_empty_input_returns_empty(self, mocker):
        mock_connect = mocker.patch("dedupe.psycopg2.connect")
        result = filter_new([], db_url="postgresql://test")
        assert result == []
        mock_connect.assert_not_called()

    def test_all_seen_returns_empty(self, mocker):
        mocker.patch("dedupe.psycopg2.connect", return_value=make_mock_conn(["hash_a", "hash_b", "hash_c"]))
        result = filter_new(ITEMS, db_url="postgresql://test")
        assert result == []
