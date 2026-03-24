"""
Deduplicate fetched items against hashes already stored in the database.
Returns only items whose dedup_hash is not already in raw_items.
"""

import psycopg2


def filter_new(items: list[dict], db_url: str) -> list[dict]:
    if not items:
        return []

    hashes = [item["dedup_hash"] for item in items]

    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT dedup_hash FROM raw_items WHERE dedup_hash = ANY(%s)",
                (hashes,),
            )
            seen = {row[0] for row in cur.fetchall()}

    new_items = [item for item in items if item["dedup_hash"] not in seen]
    print(f"[dedupe] {len(new_items)} new items (filtered {len(items) - len(new_items)} duplicates)")
    return new_items
