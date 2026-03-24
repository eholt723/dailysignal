"""
Store the briefing and raw items in PostgreSQL.
Returns the new briefing_id.
"""

import json
from collections import Counter

import psycopg2


def save(briefing_content: str, period: str, items: list[dict], db_url: str) -> int:
    source_counts = dict(Counter(item["source"] for item in items))

    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO briefings (period, content, source_counts)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (period, briefing_content, json.dumps(source_counts)),
            )
            briefing_id = cur.fetchone()[0]

            if items:
                cur.executemany(
                    """
                    INSERT INTO raw_items (briefing_id, source, title, url, dedup_hash)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (dedup_hash) DO NOTHING
                    """,
                    [
                        (briefing_id, item["source"], item["title"], item["url"], item["dedup_hash"])
                        for item in items
                    ],
                )

        conn.commit()

    print(f"[store] saved briefing {briefing_id} with {len(items)} items")
    return briefing_id
