---
title: DailySignal
emoji: 📡
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

[![CI/CD](https://github.com/eholt723/dailysignal/actions/workflows/ci.yml/badge.svg)](https://github.com/eholt723/dailysignal/actions/workflows/ci.yml)

# DailySignal

Automated AI news briefing service. Fetches from HackerNews, Product Hunt, and RSS feeds twice daily, synthesizes a briefing via Groq, and emails it to subscribers.

Built by [Eric Holt](https://ericholt.dev)

---

## Deployment

Every push to `main` triggers the CI/CD workflow. If all tests pass, the changes are automatically deployed to [Hugging Face Spaces](https://huggingface.co/spaces/eholt723/dailysignal). No manual deploy step required.

---

## MCP Server

DailySignal exposes a [Model Context Protocol](https://modelcontextprotocol.io) server at `https://eholt723-dailysignal.hf.space/mcp` using FastMCP 3.2.4 (Streamable HTTP transport). It provides three read-only tools:

| Tool | Description |
|---|---|
| `get_latest_briefing` | Returns the most recent morning and afternoon briefings |
| `get_run_history` | Returns recent pipeline runs with timestamps and source counts (max 50) |
| `get_subscriber_stats` | Returns subscriber counts and overall delivery success rate |

To connect from a compatible MCP client (Claude Desktop, Cursor, etc.), point it at the `/mcp` URL above.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Scheduler | GitHub Actions (cron, `workflow_dispatch`) |
| Data Fetching | feedparser 6.0.11, httpx 0.27.0 |
| LLM | Groq — llama-3.3-70b-versatile |
| Database | PostgreSQL on Neon (psycopg2-binary 2.9.9) |
| Email | Resend 2.26.0 |
| API | FastAPI 0.136.0 + uvicorn 0.30.6 |
| MCP Server | FastMCP 3.2.4 — Streamable HTTP, mounted at `/mcp` |
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
│   ├── api.py            # FastAPI — /briefings, /subscribe, /unsubscribe, /admin; mounts MCP at /mcp
│   ├── mcp_server.py     # FastMCP server — get_latest_briefing, get_run_history, get_subscriber_stats
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
    ├── test_api.py
    └── test_mcp_server.py
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
           ┌──────────▼──────────┐      ┌─────────────────┐
           │     dedupe.py       │────▶│ Neon (raw_items) │
           │  (SHA-256 hashing)  │◀────│                  │
           └──────────┬──────────┘      └─────────────────┘
                      │ new items only
           ┌──────────▼──────────┐
           │    synthesize.py    │◀── Groq API (llama-3.3-70b-versatile)
           └──────────┬──────────┘
                      │ briefing text
           ┌──────────▼──────────┐      ┌──────────────────┐
           │      store.py       │────▶│ Neon (briefings)  │
           └──────────┬──────────┘      └──────────────────┘
                      │ briefing_id
           ┌──────────▼──────────┐
           │    email_send.py    │────▶ Resend API ──▶ subscribers
           └─────────────────────┘

           ┌─────────────────────────────────────┐
           │       Hugging Face Spaces           │      ┌───────────────┐
           │  nginx (7860) ──▶ React/Vite       │      │   Neon DB     │
           │  supervisord   ──▶ FastAPI (8000)  │◀───▶│  (read-only)  │
           │                   └─▶ /mcp (MCP)   │      └───────────────┘
           └─────────────────────────────────────┘
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
| mcp_server.py + FastMCP | Exposes briefing data as MCP tools at `/mcp` (Streamable HTTP) |
| React/Vite frontend | Renders briefings, history, admin stats, and subscriber management |
