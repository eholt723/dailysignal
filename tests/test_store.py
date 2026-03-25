"""Tests for pipeline/store.py"""

import json
import pytest
from unittest.mock import MagicMock, call
from store import save

ITEMS = [
    {"source": "HackerNews", "title": "Story A", "url": "https://a.com", "dedup_hash": "hash_a"},
    {"source": "HackerNews", "title": "Story B", "url": "https://b.com", "dedup_hash": "hash_b"},
    {"source": "TechCrunch", "title": "Story C", "url": "https://c.com", "dedup_hash": "hash_c"},
]


def make_mock_conn(briefing_id: int = 42):
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = (briefing_id,)
    mock_cur.__enter__ = lambda s: s
    mock_cur.__exit__ = MagicMock(return_value=False)

    mock_conn = MagicMock()
    mock_conn.__enter__ = lambda s: s
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value = mock_cur
    return mock_conn, mock_cur


class TestSave:
    def test_returns_briefing_id(self, mocker):
        mock_conn, _ = make_mock_conn(briefing_id=7)
        mocker.patch("store.psycopg2.connect", return_value=mock_conn)

        result = save("briefing content", "morning", ITEMS, db_url="postgresql://test")
        assert result == 7

    def test_inserts_briefing_with_correct_period(self, mocker):
        mock_conn, mock_cur = make_mock_conn()
        mocker.patch("store.psycopg2.connect", return_value=mock_conn)

        save("content", "afternoon", ITEMS, db_url="postgresql://test")

        first_execute = mock_cur.execute.call_args_list[0]
        args = first_execute[0][1]
        assert args[0] == "afternoon"

    def test_source_counts_computed_correctly(self, mocker):
        mock_conn, mock_cur = make_mock_conn()
        mocker.patch("store.psycopg2.connect", return_value=mock_conn)

        save("content", "morning", ITEMS, db_url="postgresql://test")

        first_execute = mock_cur.execute.call_args_list[0]
        source_counts_json = first_execute[0][1][2]
        source_counts = json.loads(source_counts_json)

        assert source_counts["HackerNews"] == 2
        assert source_counts["TechCrunch"] == 1

    def test_calls_executemany_for_raw_items(self, mocker):
        mock_conn, mock_cur = make_mock_conn()
        mocker.patch("store.psycopg2.connect", return_value=mock_conn)

        save("content", "morning", ITEMS, db_url="postgresql://test")

        mock_cur.executemany.assert_called_once()
        _, rows = mock_cur.executemany.call_args[0]
        assert len(rows) == 3

    def test_empty_items_skips_executemany(self, mocker):
        mock_conn, mock_cur = make_mock_conn()
        mocker.patch("store.psycopg2.connect", return_value=mock_conn)

        save("content", "morning", [], db_url="postgresql://test")

        mock_cur.executemany.assert_not_called()

    def test_commits_transaction(self, mocker):
        mock_conn, _ = make_mock_conn()
        mocker.patch("store.psycopg2.connect", return_value=mock_conn)

        save("content", "morning", ITEMS, db_url="postgresql://test")

        mock_conn.commit.assert_called_once()
