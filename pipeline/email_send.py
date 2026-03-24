"""
Send the briefing to all active subscribers via Gmail SMTP.
Logs delivery status per subscriber. Deactivates subscribers after 3 consecutive failures.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import psycopg2

FAIL_THRESHOLD = 3


def _build_email(to: str, subject: str, briefing_html: str, unsubscribe_url: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = "DailySignal <noreply@dailysignal>"
    msg["To"] = to

    footer = f'\n\n---\n<a href="{unsubscribe_url}">Unsubscribe</a>'
    html = f"<html><body>{briefing_html}{footer}</body></html>"
    msg.attach(MIMEText(briefing_html + f"\n\nUnsubscribe: {unsubscribe_url}", "plain"))
    msg.attach(MIMEText(html, "html"))
    return msg


def _markdown_to_html(md: str) -> str:
    """Minimal markdown → HTML (headers and line breaks only)."""
    lines = []
    for line in md.split("\n"):
        if line.startswith("## "):
            lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("- "):
            lines.append(f"<li>{line[2:]}</li>")
        elif line.strip() == "":
            lines.append("<br>")
        else:
            lines.append(f"<p>{line}</p>")
    return "\n".join(lines)


def send_briefing(
    briefing_id: int,
    period: str,
    content: str,
    db_url: str,
    gmail_user: str,
    gmail_password: str,
    base_url: str,
) -> None:
    period_label = "Morning" if period == "morning" else "Afternoon"
    subject = f"DailySignal {period_label} Briefing"
    briefing_html = _markdown_to_html(content)

    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, unsubscribe_token FROM subscribers WHERE is_active = TRUE"
            )
            subscribers = cur.fetchall()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail_user, gmail_password)

            for sub_id, email, token in subscribers:
                unsubscribe_url = f"{base_url}/unsubscribe?token={token}"
                msg = _build_email(email, subject, briefing_html, unsubscribe_url)
                status = "sent"
                error_msg = None

                try:
                    smtp.sendmail(gmail_user, email, msg.as_string())
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
