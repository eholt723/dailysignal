"""Tests for pipeline/synthesize.py"""

import pytest
from unittest.mock import MagicMock
from synthesize import synthesize, MODEL

ITEMS = [
    {"source": "HackerNews", "title": "AI takes over", "url": "https://hn.com/1"},
    {"source": "TechCrunch", "title": "New startup raises $10M", "url": "https://tc.com/2"},
]


def make_mock_groq(response_text: str):
    mock_choice = MagicMock()
    mock_choice.message.content = response_text

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion
    return mock_client


class TestSynthesize:
    def test_returns_string(self, mocker):
        mocker.patch("synthesize.Groq", return_value=make_mock_groq("## Top Stories\nSome content."))
        result = synthesize(ITEMS, "morning", groq_api_key="test_key")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_morning_label_in_prompt(self, mocker):
        mock_groq = make_mock_groq("content")
        mocker.patch("synthesize.Groq", return_value=mock_groq)

        synthesize(ITEMS, "morning", groq_api_key="test_key")

        call_args = mock_groq.chat.completions.create.call_args
        user_message = next(m["content"] for m in call_args.kwargs["messages"] if m["role"] == "user")
        assert "Morning" in user_message

    def test_afternoon_label_in_prompt(self, mocker):
        mock_groq = make_mock_groq("content")
        mocker.patch("synthesize.Groq", return_value=mock_groq)

        synthesize(ITEMS, "afternoon", groq_api_key="test_key")

        call_args = mock_groq.chat.completions.create.call_args
        user_message = next(m["content"] for m in call_args.kwargs["messages"] if m["role"] == "user")
        assert "Afternoon" in user_message

    def test_uses_correct_model(self, mocker):
        mock_groq = make_mock_groq("content")
        mocker.patch("synthesize.Groq", return_value=mock_groq)

        synthesize(ITEMS, "morning", groq_api_key="test_key")

        call_kwargs = mock_groq.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == MODEL

    def test_item_titles_included_in_prompt(self, mocker):
        mock_groq = make_mock_groq("content")
        mocker.patch("synthesize.Groq", return_value=mock_groq)

        synthesize(ITEMS, "morning", groq_api_key="test_key")

        call_args = mock_groq.chat.completions.create.call_args
        user_message = next(m["content"] for m in call_args.kwargs["messages"] if m["role"] == "user")
        assert "AI takes over" in user_message
        assert "New startup raises $10M" in user_message

    def test_strips_whitespace_from_response(self, mocker):
        mocker.patch("synthesize.Groq", return_value=make_mock_groq("  ## Top Stories\n  "))
        result = synthesize(ITEMS, "morning", groq_api_key="test_key")
        assert not result.startswith(" ")
        assert not result.endswith(" ")
