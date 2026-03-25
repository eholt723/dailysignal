"""Tests for pipeline/api.py"""

import json
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def make_mock_conn(fetchall_return=None, fetchone_return=None):
    mock_cur = MagicMock()
    mock_cur.fetchall.return_value = fetchall_return or []
    mock_cur.fetchone.return_value = fetchone_return
    mock_cur.rowcount = 1
    mock_cur.__enter__ = lambda s: s
    mock_cur.__exit__ = MagicMock(return_value=False)

    mock_conn = MagicMock()
    mock_conn.__enter__ = lambda s: s
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value = mock_cur
    return mock_conn


class TestSubscribe:
    def test_valid_email_returns_200(self, mocker):
        mocker.patch("api.get_conn", return_value=make_mock_conn())
        res = client.post("/subscribe", json={"email": "user@example.com"})
        assert res.status_code == 200
        assert res.json()["status"] == "subscribed"

    def test_invalid_email_returns_422(self):
        res = client.post("/subscribe", json={"email": "not-an-email"})
        assert res.status_code == 422

    def test_missing_body_returns_422(self):
        res = client.post("/subscribe", json={})
        assert res.status_code == 422


class TestUnsubscribe:
    def test_valid_token_returns_200(self, mocker):
        mocker.patch("api.get_conn", return_value=make_mock_conn())
        res = client.post("/unsubscribe?token=valid_token_abc")
        assert res.status_code == 200
        assert res.json()["status"] == "unsubscribed"

    def test_missing_token_returns_422(self):
        res = client.post("/unsubscribe")
        assert res.status_code == 422

    def test_unknown_token_returns_404(self, mocker):
        mock_conn = make_mock_conn()
        mock_conn.cursor.return_value.rowcount = 0
        mocker.patch("api.get_conn", return_value=mock_conn)
        res = client.post("/unsubscribe?token=nonexistent")
        assert res.status_code == 404


class TestBriefings:
    def test_latest_returns_200(self, mocker):
        mocker.patch("api.get_conn", return_value=make_mock_conn(fetchall_return=[]))
        res = client.get("/briefings/latest")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_history_returns_200(self, mocker):
        mocker.patch("api.get_conn", return_value=make_mock_conn(fetchall_return=[]))
        res = client.get("/briefings/history")
        assert res.status_code == 200
        assert isinstance(res.json(), list)


class TestAdmin:
    def test_stats_returns_200(self, mocker):
        mock_conn = make_mock_conn(fetchone_return=(10, 8, 2))
        mocker.patch("api.get_conn", return_value=mock_conn)
        res = client.get("/admin/stats")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 10
        assert data["active"] == 8
        assert data["inactive"] == 2

    def test_deliveries_returns_200(self, mocker):
        mocker.patch("api.get_conn", return_value=make_mock_conn(fetchall_return=[]))
        res = client.get("/admin/deliveries")
        assert res.status_code == 200
        assert isinstance(res.json(), list)
