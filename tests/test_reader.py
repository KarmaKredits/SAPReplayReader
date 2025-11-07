import pytest

from sapreplayreader.reader import read_replay


def test_read_replay_returns_dict():
    # Local file path that doesn't exist should return an empty dict (placeholder behavior)
    result = read_replay("/does/not/exist")
    assert isinstance(result, dict)


def test_read_replay_fetches_http(monkeypatch):
    # Simulate the API client returning a JSON payload
    called = {}

    def fake_fetch(url, *, auth=None, timeout=30):
        called['url'] = url
        called['auth'] = auth
        return {"replay": "ok"}

    monkeypatch.setattr("sapreplayreader.api_client.fetch_replay", fake_fetch)

    result = read_replay("https://api.example.com/replay", auth={"type": "apikey", "header": "Authorization", "value": "Bearer tok"})
    assert result == {"replay": "ok"}
    assert called['url'] == "https://api.example.com/replay"
