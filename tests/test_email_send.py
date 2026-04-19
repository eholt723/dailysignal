"""Tests for pipeline/email_send.py"""

import pytest
from unittest.mock import MagicMock, patch, call
from email_send import _markdown_to_html, send_briefing, FAIL_THRESHOLD


class TestMarkdownToHtml:
    def test_h1(self):
        assert _markdown_to_html("# Title") == "<h1>Title</h1>"

    def test_h2(self):
        assert _markdown_to_html("## Section") == "<h2>Section</h2>"

    def test_bullet(self):
        assert _markdown_to_html("- item") == "<li>item</li>"

    def test_empty_line_becomes_br(self):
        assert _markdown_to_html("") == "<br>"

    def test_plain_text_becomes_paragraph(self):
        assert _markdown_to_html("Hello world") == '<p style="margin:0 0 10px 0;">Hello world</p>'

    def test_multiline(self):
        md = "## Top Stories\n- item one\n\nSome text"
        html = _markdown_to_html(md)
        assert "<h2>Top Stories</h2>" in html
        assert "<li>item one</li>" in html
        assert "<br>" in html
        assert '<p style="margin:0 0 10px 0;">Some text</p>' in html


def make_mock_conn(subscribers=None):
    if subscribers is None:
        subscribers = [(1, "user@example.com", "token123")]

    mock_cur = MagicMock()
    mock_cur.fetchall.return_value = subscribers
    mock_cur.__enter__ = lambda s: s
    mock_cur.__exit__ = MagicMock(return_value=False)

    mock_conn = MagicMock()
    mock_conn.__enter__ = lambda s: s
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value = mock_cur
    return mock_conn, mock_cur


class TestSendBriefing:
    def test_sends_to_active_subscribers(self, mocker):
        mock_conn, _ = make_mock_conn(subscribers=[(1, "a@b.com", "tok")])
        mocker.patch("email_send.psycopg2.connect", return_value=mock_conn)
        mock_send = mocker.patch("email_send.resend.Emails.send", return_value={"id": "abc"})

        send_briefing(1, "morning", "## Top Stories\nSome news.", "postgresql://test", "re_key", "https://app.example.com")

        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[0][0]
        assert call_kwargs["to"] == "a@b.com"
        assert "Morning" in call_kwargs["subject"]

    def test_unsubscribe_url_in_html(self, mocker):
        mock_conn, _ = make_mock_conn(subscribers=[(1, "a@b.com", "mytoken")])
        mocker.patch("email_send.psycopg2.connect", return_value=mock_conn)
        mock_send = mocker.patch("email_send.resend.Emails.send", return_value={"id": "abc"})

        send_briefing(1, "morning", "content", "postgresql://test", "re_key", "https://myapp.com")

        call_kwargs = mock_send.call_args[0][0]
        assert "mytoken" in call_kwargs["html"]
        assert "mytoken" in call_kwargs["text"]

    def test_logs_sent_status_to_delivery_log(self, mocker):
        mock_conn, mock_cur = make_mock_conn()
        mocker.patch("email_send.psycopg2.connect", return_value=mock_conn)
        mocker.patch("email_send.resend.Emails.send", return_value={"id": "abc"})

        send_briefing(5, "afternoon", "content", "postgresql://test", "re_key", "https://app.example.com")

        insert_calls = [c for c in mock_cur.execute.call_args_list if "INSERT INTO delivery_log" in str(c)]
        assert len(insert_calls) == 1
        args = insert_calls[0][0][1]
        assert args[0] == 5  # briefing_id
        assert args[2] == "sent"

    def test_logs_failed_status_on_send_error(self, mocker):
        mock_conn, mock_cur = make_mock_conn()
        mocker.patch("email_send.psycopg2.connect", return_value=mock_conn)
        mocker.patch("email_send.resend.Emails.send", side_effect=Exception("SMTP timeout"))

        send_briefing(1, "morning", "content", "postgresql://test", "re_key", "https://app.example.com")

        insert_calls = [c for c in mock_cur.execute.call_args_list if "INSERT INTO delivery_log" in str(c)]
        assert insert_calls[0][0][1][2] == "failed"

    def test_increments_fail_count_on_error(self, mocker):
        mock_conn, mock_cur = make_mock_conn()
        mocker.patch("email_send.psycopg2.connect", return_value=mock_conn)
        mocker.patch("email_send.resend.Emails.send", side_effect=Exception("error"))

        send_briefing(1, "morning", "content", "postgresql://test", "re_key", "https://app.example.com")

        fail_count_calls = [c for c in mock_cur.execute.call_args_list if "fail_count = fail_count + 1" in str(c)]
        assert len(fail_count_calls) == 1

    def test_resets_fail_count_on_success(self, mocker):
        mock_conn, mock_cur = make_mock_conn()
        mocker.patch("email_send.psycopg2.connect", return_value=mock_conn)
        mocker.patch("email_send.resend.Emails.send", return_value={"id": "ok"})

        send_briefing(1, "morning", "content", "postgresql://test", "re_key", "https://app.example.com")

        reset_calls = [c for c in mock_cur.execute.call_args_list if "fail_count = 0" in str(c)]
        assert len(reset_calls) == 1

    def test_deactivates_after_fail_threshold(self, mocker):
        mock_conn, mock_cur = make_mock_conn()
        mocker.patch("email_send.psycopg2.connect", return_value=mock_conn)
        mocker.patch("email_send.resend.Emails.send", side_effect=Exception("error"))

        send_briefing(1, "morning", "content", "postgresql://test", "re_key", "https://app.example.com")

        deactivate_calls = [c for c in mock_cur.execute.call_args_list if "is_active = FALSE" in str(c)]
        assert len(deactivate_calls) == 1
        # confirm threshold value is used
        args = deactivate_calls[0][0][1]
        assert args[1] == FAIL_THRESHOLD

    def test_no_emails_sent_when_no_subscribers(self, mocker):
        mock_conn, _ = make_mock_conn(subscribers=[])
        mocker.patch("email_send.psycopg2.connect", return_value=mock_conn)
        mock_send = mocker.patch("email_send.resend.Emails.send")

        send_briefing(1, "morning", "content", "postgresql://test", "re_key", "https://app.example.com")

        mock_send.assert_not_called()
