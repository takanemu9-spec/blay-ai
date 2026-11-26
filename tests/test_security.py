import pytest
from fastapi import HTTPException

from app.core.security import verify_api_key


def test_valid_api_key(monkeypatch):
    monkeypatch.setenv("BLAY_API_KEY", "test-secret-key")

    assert verify_api_key("test-secret-key") is True


def test_invalid_api_key(monkeypatch):
    monkeypatch.setenv("BLAY_API_KEY", "test-secret-key")

    with pytest.raises(HTTPException) as exc:
        verify_api_key("wrong-key")

    assert exc.value.status_code == 401


def test_missing_api_key(monkeypatch):
    monkeypatch.setenv("BLAY_API_KEY", "test-secret-key")

    with pytest.raises(HTTPException) as exc:
        verify_api_key(None)

    assert exc.value.status_code == 401


def test_unconfigured_api_key(monkeypatch):
    monkeypatch.delenv("BLAY_API_KEY", raising=False)

    with pytest.raises(HTTPException) as exc:
        verify_api_key("test-secret-key")

    assert exc.value.status_code == 503
