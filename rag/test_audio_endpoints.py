#!/usr/bin/env python3
"""
Test audio stub endpoints for Open WebUI compatibility.

These tests verify that /v1/audio/voices and /v1/audio/models return
empty lists with proper authentication, fixing the 50s latency issue
in Open WebUI view switching.
"""

import os
import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv

load_dotenv()

# Import app after env loaded
from rag.api import app

client = TestClient(app)

# Get API key from environment
API_KEY = os.getenv("RAG_API_KEY")
if not API_KEY:
    pytest.skip("RAG_API_KEY not set", allow_module_level=True)


def test_audio_voices_without_auth():
    """Test /v1/audio/voices rejects requests without API key."""
    response = client.get("/v1/audio/voices")
    assert response.status_code == 401
    assert "API key required" in response.json()["detail"]


def test_audio_voices_with_invalid_auth():
    """Test /v1/audio/voices rejects invalid API keys."""
    response = client.get(
        "/v1/audio/voices",
        headers={"Authorization": "Bearer invalid_key"}
    )
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]


def test_audio_voices_with_valid_auth():
    """Test /v1/audio/voices returns empty list with valid API key."""
    response = client.get(
        "/v1/audio/voices",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 0  # Empty list expected


def test_audio_models_without_auth():
    """Test /v1/audio/models rejects requests without API key."""
    response = client.get("/v1/audio/models")
    assert response.status_code == 401
    assert "API key required" in response.json()["detail"]


def test_audio_models_with_invalid_auth():
    """Test /v1/audio/models rejects invalid API keys."""
    response = client.get(
        "/v1/audio/models",
        headers={"Authorization": "Bearer invalid_key"}
    )
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]


def test_audio_models_with_valid_auth():
    """Test /v1/audio/models returns empty list with valid API key."""
    response = client.get(
        "/v1/audio/models",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 0  # Empty list expected


def test_audio_endpoints_response_format():
    """Test both endpoints return OpenAI-compatible format."""
    headers = {"Authorization": f"Bearer {API_KEY}"}

    # Test voices format
    voices_response = client.get("/v1/audio/voices", headers=headers)
    assert voices_response.status_code == 200
    assert voices_response.json() == {"data": []}

    # Test models format
    models_response = client.get("/v1/audio/models", headers=headers)
    assert models_response.status_code == 200
    assert models_response.json() == {"data": []}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
