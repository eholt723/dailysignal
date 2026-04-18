"""Tests for the MCP server tools."""

from datetime import datetime
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------

def mock_conn(fetchall_result=None, fetchone_results=None):
    """Build a mock psycopg2 connection."""
    cur = MagicMock()
    cur.fetchall.return_value = fetchall_result or []
    if fetchone_results:
        cur.fetchone.side_effect = fetchone_results
    else:
        cur.fetchone.return_value = (0,)

    ctx_cur = MagicMock()
    ctx_cur.__enter__ = MagicMock(return_value=cur)
    ctx_cur.__exit__ = MagicMock(return_value=False)

    conn = MagicMock()
    conn.cursor.return_value = ctx_cur
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock(return_value=False)
    return conn


class TestGetLatestBriefing:
    def test_returns_briefings(self):
        from pipeline.mcp_server import get_latest_briefing

        rows = [
            {"id": 1, "run_at": datetime(2024, 1, 1, 12), "period": "morning",
             "content": "Morning brief", "source_counts": {"hn": 10}},
            {"id": 2, "run_at": datetime(2024, 1, 1, 20), "period": "afternoon",
             "content": "Afternoon brief", "source_counts": {"hn": 8}},
        ]
        conn = mock_conn(fetchall_result=rows)

        with patch("pipeline.mcp_server.get_conn", return_value=conn):
            result = get_latest_briefing()

        assert "briefings" in result
        assert len(result["briefings"]) == 2
        assert result["briefings"][0]["period"] == "morning"

    def test_empty_db(self):
        from pipeline.mcp_server import get_latest_briefing

        conn = mock_conn(fetchall_result=[])
        with patch("pipeline.mcp_server.get_conn", return_value=conn):
            result = get_latest_briefing()

        assert result == {"briefings": []}


class TestGetRunHistory:
    def test_returns_runs(self):
        from pipeline.mcp_server import get_run_history

        rows = [
            {"id": i, "run_at": datetime(2024, 1, i + 1), "period": "morning",
             "source_counts": {"hn": i}}
            for i in range(5)
        ]
        conn = mock_conn(fetchall_result=rows)

        with patch("pipeline.mcp_server.get_conn", return_value=conn):
            result = get_run_history(limit=5)

        assert len(result["runs"]) == 5

    def test_clamps_limit_to_50(self):
        from pipeline.mcp_server import get_run_history

        conn = mock_conn(fetchall_result=[])
        with patch("pipeline.mcp_server.get_conn", return_value=conn) as mock_get:
            get_run_history(limit=999)

        # Verify the clamped value was passed to execute
        cur = conn.cursor().__enter__()
        call_args = cur.execute.call_args
        assert 50 in call_args[0][1]

    def test_default_limit(self):
        from pipeline.mcp_server import get_run_history

        conn = mock_conn(fetchall_result=[])
        with patch("pipeline.mcp_server.get_conn", return_value=conn):
            result = get_run_history()

        assert "runs" in result


class TestGetSubscriberStats:
    def test_returns_stats(self):
        from pipeline.mcp_server import get_subscriber_stats

        conn = mock_conn(
            fetchone_results=[
                (25, 20, 5),   # subscriber counts
                (100,),        # total briefings
                (98.5,),       # success rate
            ]
        )
        with patch("pipeline.mcp_server.get_conn", return_value=conn):
            result = get_subscriber_stats()

        assert result["total_subscribers"] == 25
        assert result["active"] == 20
        assert result["inactive"] == 5
        assert result["total_briefings"] == 100
        assert result["delivery_success_rate"] == 98.5

    def test_null_success_rate_defaults_to_zero(self):
        from pipeline.mcp_server import get_subscriber_stats

        conn = mock_conn(
            fetchone_results=[
                (0, 0, 0),
                (0,),
                (None,),
            ]
        )
        with patch("pipeline.mcp_server.get_conn", return_value=conn):
            result = get_subscriber_stats()

        assert result["delivery_success_rate"] == 0.0
