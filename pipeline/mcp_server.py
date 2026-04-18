import os

import psycopg2
import psycopg2.extras
from fastmcp import FastMCP

mcp = FastMCP("DailySignal")


def get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])


@mcp.tool()
def get_latest_briefing() -> dict:
    """Return the most recent morning and afternoon briefings."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT DISTINCT ON (period) id, run_at, period, content, source_counts
                FROM briefings
                ORDER BY period, run_at DESC
            """)
            rows = cur.fetchall()
    return {"briefings": [dict(r) for r in rows]}


@mcp.tool()
def get_run_history(limit: int = 20) -> dict:
    """Return recent pipeline runs with timestamps and source counts. Max 50."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, run_at, period, source_counts
                FROM briefings
                ORDER BY run_at DESC
                LIMIT %s
            """, (min(limit, 50),))
            rows = cur.fetchall()
    return {"runs": [dict(r) for r in rows]}


@mcp.tool()
def get_subscriber_stats() -> dict:
    """Return subscriber counts and overall delivery success rate."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE is_active) AS active,
                    COUNT(*) FILTER (WHERE NOT is_active) AS inactive
                FROM subscribers
            """)
            row = cur.fetchone()
            cur.execute("SELECT COUNT(*) FROM briefings")
            total_briefings = cur.fetchone()[0]
            cur.execute("""
                SELECT ROUND(
                    100.0 * COUNT(*) FILTER (WHERE status = 'sent') / NULLIF(COUNT(*), 0), 1
                ) FROM delivery_log
            """)
            rate = cur.fetchone()[0]
    return {
        "total_subscribers": row[0],
        "active": row[1],
        "inactive": row[2],
        "total_briefings": total_briefings,
        "delivery_success_rate": float(rate) if rate else 0.0,
    }
