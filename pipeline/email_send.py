"""
Send the briefing to all active subscribers via Resend.
Logs delivery status per subscriber. Deactivates subscribers after 3 consecutive failures.
"""

import re

import resend
import psycopg2

FAIL_THRESHOLD = 3
FROM_ADDRESS = "DailySignal <dailysignal@ericholt.dev>"


def _linkify(text: str) -> str:
    """Convert markdown links [text](url) to HTML anchor tags."""
    return re.sub(
        r'\[([^\]]+)\]\((https?://[^\)]+)\)',
        r'<a href="\2">\1</a>',
        text,
    )


def _markdown_to_html(md: str) -> str:
    """Minimal markdown -> HTML (headers, line breaks, and links)."""
    lines = []
    for line in md.split("\n"):
        if line.startswith("## "):
            lines.append(f"<h2>{_linkify(line[3:])}</h2>")
        elif line.startswith("# "):
            lines.append(f"<h1>{_linkify(line[2:])}</h1>")
        elif line.startswith("- "):
            lines.append(f"<li>{_linkify(line[2:])}</li>")
        elif line.strip() == "":
            lines.append("<br>")
        else:
            lines.append(f"<p>{_linkify(line)}</p>")
    return "\n".join(lines)


def send_briefing(
    briefing_id: int,
    period: str,
    content: str,
    db_url: str,
    resend_api_key: str,
    base_url: str,
) -> None:
    resend.api_key = resend_api_key

    period_label = "Morning" if period == "morning" else "Afternoon"
    subject = f"DailySignal {period_label} Briefing"
    briefing_html = _markdown_to_html(content)

    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, unsubscribe_token FROM subscribers WHERE is_active = TRUE"
            )
            subscribers = cur.fetchall()

        for sub_id, email, token in subscribers:
            unsubscribe_url = f"{base_url}/unsubscribe?token={token}"
            footer = (
                f'<br><br><hr>'
                f'<p style="font-size:12px;color:#888;">No journalists were harmed in the making of this briefing.</p>'
                f'<p style="font-size:12px;color:#888;">Built by Eric Holt &middot; <a href="https://ericholt.dev">ericholt.dev</a></p>'
                f'<p style="font-size:12px;"><a href="{unsubscribe_url}">Unsubscribe</a></p>'
            )
            html = f"<html><body>{briefing_html}{footer}</body></html>"
            text = content + f"\n\nNo journalists were harmed in the making of this briefing.\nBuilt by Eric Holt · ericholt.dev\n\nUnsubscribe: {unsubscribe_url}"

            status = "sent"
            error_msg = None

            try:
                resend.Emails.send({
                    "from": FROM_ADDRESS,
                    "to": email,
                    "subject": subject,
                    "html": html,
                    "text": text,
                })
            except Exception as e:
                status = "failed"
                error_msg = str(e)
                print(f"[email] failed to send to {email}: {e}")

            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO delivery_log (briefing_id, subscriber_id, status, error_msg)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (briefing_id, sub_id, status, error_msg),
                )

                if status == "failed":
                    cur.execute(
                        "UPDATE subscribers SET fail_count = fail_count + 1 WHERE id = %s",
                        (sub_id,),
                    )
                    cur.execute(
                        """
                        UPDATE subscribers SET is_active = FALSE
                        WHERE id = %s AND fail_count >= %s
                        """,
                        (sub_id, FAIL_THRESHOLD),
                    )
                else:
                    cur.execute(
                        "UPDATE subscribers SET fail_count = 0 WHERE id = %s",
                        (sub_id,),
                    )

            conn.commit()

    print(f"[email] delivered briefing {briefing_id} to {len(subscribers)} subscribers")
