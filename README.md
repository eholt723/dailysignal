---
title: DailySignal
emoji: 📡
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

[![CI](https://github.com/eholt723/dailysignal/actions/workflows/ci.yml/badge.svg)](https://github.com/eholt723/dailysignal/actions/workflows/ci.yml)

# DailySignal

Automated AI news briefing service. Fetches from HackerNews, Product Hunt, and RSS feeds twice daily, synthesizes a briefing via Groq, and emails it to subscribers.

Built by [Eric Holt](https://ericholt.dev)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Scheduler | GitHub Actions (cron, `workflow_dispatch`) |
| Data Fetching | feedparser 6.0.11, httpx 0.27.0 |
| LLM | Groq — llama-3.3-70b-versatile |
| Database | PostgreSQL on Neon (psycopg2-binary 2.9.9) |
| Email | Resend 2.26.0 |
| API | FastAPI 0.115.0 + uvicorn 0.30.6 |
| Frontend | React 19, Vite 8, Tailwind CSS 4, react-router-dom 7, Recharts 3 |
| Hosting | Hugging Face Spaces (Docker) |
| Runtime | nginx + supervisord |

---

## Project Structure

```
dailysignal/
├── pipeline/
│   ├── fetch.py          # Pull items from HackerNews, Product Hunt, and 5 RSS feeds
│   ├── dedupe.py         # Filter already-seen items using SHA-256 hashes stored in Neon
│   ├── synthesize.py     # Send new items to Groq; returns structured briefing text
│   ├── store.py          # Write briefing + raw items to PostgreSQL
│   ├── email_send.py     # Deliver briefing to active subscribers via Resend
│   ├── api.py            # FastAPI — /briefings, /subscribe, /unsubscribe, /admin
│   ├── run.py            # CLI entrypoint: python run.py --period morning|afternoon
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Root component — nav, routing
│   │   └── pages/
│   │       ├── Home.jsx       # Latest morning + afternoon briefings
│   │       ├── History.jsx    # Run history feed
│   │       ├── Admin.jsx      # Subscriber stats and delivery log
│   │       ├── Subscribe.jsx  # Email sign-up form
│   │       ├── Unsubscribe.jsx # Token-based unsubscribe
│   │       └── About.jsx      # Portfolio/showcase page
│   ├── nginx.conf         # nginx config: serves frontend on 7860, proxies /api/* to FastAPI
│   ├── supervisord.conf   # Runs nginx + uvicorn as co-processes inside the container
│   └── package.json
├── .github/workflows/
│   ├── morning.yml        # Cron at 12:00 UTC — triggers full pipeline
│   └── afternoon.yml      # Cron at 20:00 UTC — triggers full pipeline
├── Dockerfile             # Multi-stage: Node builder → python:3.12-slim runtime
├── schema.sql             # PostgreSQL schema: briefings, raw_items, subscribers, delivery_log
└── tests/
    ├── test_fetch.py
    ├── test_dedupe.py
    ├── test_synthesize.py
    ├── test_store.py
    ├── test_email_send.py
    └── test_api.py
```

---

## Architecture

```
┌──────────────────────────────────────────┐
│    GitHub Actions  (cron 12pm / 8pm)     │
└─────────────────────┬────────────────────┘
                      │
           ┌──────────▼──────────┐
           │      fetch.py       │◀── HackerNews · Product Hunt · 5 RSS feeds
           └──────────┬──────────┘
                      │ ~87 raw items
           ┌──────────▼──────────┐     ┌─────────────────┐
           │     dedupe.py       │────▶│ Neon (raw_items) │
           │  (SHA-256 hashing)  │◀────│                  │
           └──────────┬──────────┘     └─────────────────┘
                      │ new items only
           ┌──────────▼──────────┐
           │    synthesize.py    │◀── Groq API (llama-3.3-70b-versatile)
           └──────────┬──────────┘
                      │ briefing text
           ┌──────────▼──────────┐     ┌──────────────────┐
           │      store.py       │────▶│ Neon (briefings)  │
           └──────────┬──────────┘     └──────────────────┘
                      │ briefing_id
           ┌──────────▼──────────┐
           │    email_send.py    │────▶ Resend API ──▶ subscribers
           └─────────────────────┘

           ┌─────────────────────────────────────┐
           │       Hugging Face Spaces            │     ┌───────────────┐
           │  nginx (7860) ──▶ React/Vite         │     │   Neon DB     │
           │  supervisord   ──▶ FastAPI (8000)    │◀───▶│  (read-only)  │
           └─────────────────────────────────────┘     └───────────────┘
```

| Layer | Responsibility |
|---|---|
| GitHub Actions | Cron scheduling — runs the full pipeline twice daily, no server required |
| fetch.py | Pulls up to 87 items per run from HackerNews, Product Hunt, and 5 RSS feeds |
| dedupe.py | Hashes each item and filters against previously stored hashes in Neon |
| synthesize.py | Sends new items to Groq; receives structured briefing in three sections |
| store.py | Persists the briefing and raw items; returns `briefing_id` for delivery logging |
| email_send.py | Sends per-subscriber emails via Resend with unique unsubscribe tokens |
| api.py + FastAPI | Serves briefing data and handles subscribe/unsubscribe from the frontend |
| React/Vite frontend | Renders briefings, history, admin stats, and subscriber management |
