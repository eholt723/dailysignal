"""
Main pipeline entrypoint. Called by GitHub Actions.
Usage: python run.py --period morning|afternoon
"""

import argparse
import os
import sys

from dotenv import load_dotenv

load_dotenv()

from fetch import fetch_all
from dedupe import filter_new
from synthesize import synthesize
from store import save
from email_send import send_briefing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", required=True, choices=["morning", "afternoon"])
    parser.add_argument("--force", action="store_true", help="skip dedup and send regardless of new items")
    args = parser.parse_args()

    db_url = os.environ["DATABASE_URL"]
    groq_api_key = os.environ["GROQ_API_KEY"]
    product_hunt_api_key = os.environ["PRODUCT_HUNT_API_KEY"]
    resend_api_key = os.environ["RESEND_API_KEY"]
    base_url = os.environ.get("BASE_URL", "https://eholt723-dailysignal.hf.space")

    print(f"[run] starting {args.period} pipeline")

    items = fetch_all(product_hunt_api_key)
    new_items = items if args.force else filter_new(items, db_url)

    if not new_items:
        print("[run] no new items after dedup — skipping briefing")
        sys.exit(0)

    content = synthesize(new_items, args.period, groq_api_key)
    briefing_id = save(content, args.period, new_items, db_url)
    send_briefing(briefing_id, args.period, content, db_url, resend_api_key, base_url)

    print(f"[run] pipeline complete — briefing {briefing_id}")


if __name__ == "__main__":
    main()
