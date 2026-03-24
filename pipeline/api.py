"""
FastAPI backend — serves the frontend and handles subscribe/unsubscribe.
Run with: uvicorn api:app --host 0.0.0.0 --port 8000
"""

import os
import secrets

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])


# ---------------------------------------------------------------------------
# Briefings
# ---------------------------------------------------------------------------

@app.get("/briefings/latest")
def latest_briefings():
    """Return the two most recent briefings (one morning, one afternoon)."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT DISTINCT ON (period) id, run_at, period, content, source_counts
                FROM briefings
                ORDER BY period, run_at DESC
            """)
            rows = cur.fetchall()
    return [dict(r) for r in rows]


@app.get("/briefings/history")
def briefing_history():
    """Return the last 50 runs with timestamp, period, and source counts."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, run_at, period, source_counts
                FROM briefings
                ORDER BY run_at DESC
                LIMIT 50
            """)
            rows = cur.fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Subscribe / Unsubscribe
# ---------------------------------------------------------------------------

class SubscribeRequest(BaseModel):
    email: EmailStr


@app.post("/subscribe")
def subscribe(body: SubscribeRequest):
    token = secrets.token_urlsafe(32)
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO subscribers (email, unsubscribe_token)
                    VALUES (%s, %s)
                    ON CONFLICT (email) DO UPDATE
                        SET is_active = TRUE, fail_count = 0
                """, (body.email, token))
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "subscribed"}


@app.post("/unsubscribe")
def unsubscribe(token: str = Query(...)):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE subscribers SET is_active = FALSE
                WHERE unsubscribe_token = %s
            """, (token,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Token not found")
        conn.commit()
    return {"status": "unsubscribed"}


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

@app.get("/admin/stats")
def admin_stats():
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
    return {"total": row[0], "active": row[1], "inactive": row[2]}


@app.get("/admin/deliveries")
def admin_deliveries():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    dl.status,
                    dl.attempted_at,
                    dl.error_msg,
                    s.email,
                    b.period
                FROM delivery_log dl
                JOIN subscribers s ON s.id = dl.subscriber_id
                JOIN briefings b ON b.id = dl.briefing_id
                ORDER BY dl.attempted_at DESC
                LIMIT 10
            """)
            rows = cur.fetchall()
    return [dict(r) for r in rows]
