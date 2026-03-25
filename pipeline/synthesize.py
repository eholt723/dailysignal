"""
Synthesize a structured briefing from new items using Groq.
Returns the briefing as a string.
"""

from groq import Groq

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are DailySignal, an AI that writes concise, high-signal tech and AI briefings for busy professionals.

Your briefings are structured into three sections:
1. Top Stories — the 3-5 most significant items across all sources
2. Product & Launch Highlights — notable new products or releases from Product Hunt and tech blogs
3. From the Community — interesting discussions or trends from HackerNews

Rules:
- Write in plain English, no jargon
- Each item: one sentence max, link the source name to the article URL using markdown format: ([SourceName](url))
- No filler phrases like "In today's briefing..." or "That's all for now"
- If a section has nothing relevant, omit it entirely
- Total length: 250-400 words
"""


def synthesize(items: list[dict], period: str, groq_api_key: str) -> str:
    client = Groq(api_key=groq_api_key)

    period_label = "Morning" if period == "morning" else "Afternoon"
    items_text = "\n".join(
        f"- [{item['source']}] {item['title']} ({item['url']})"
        for item in items
    )

    user_prompt = f"""Write the {period_label} DailySignal briefing for the following items:

{items_text}

Format your response with markdown headers (## Top Stories, etc.)."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=1024,
    )

    content = response.choices[0].message.content.strip()
    print(f"[synthesize] generated {len(content)} chars")
    return content
