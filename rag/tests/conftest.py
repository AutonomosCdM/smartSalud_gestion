"""Test configuration and fixtures for smartSalud RAG API tests."""

import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def test_api_key():
    """Provide a test API key."""
    return "test-api-key-smartsalud"


@pytest.fixture
def mock_api_key(monkeypatch, test_api_key):
    """Mock the API_KEY environment variable for testing."""
    monkeypatch.setenv("RAG_API_KEY", test_api_key)
    # Reload the api module to pick up the new env var
    import sys
    if "rag.api" in sys.modules:
        del sys.modules["rag.api"]
    return test_api_key


@pytest.fixture(autouse=True)
def mock_slowapi(monkeypatch):
    """Automatically mock slowapi limiter for all tests to avoid rate limiting."""
    # Create a mock limiter that returns a no-op decorator
    mock_limiter_obj = MagicMock()
    mock_limiter_obj.limit = lambda x: lambda f: f  # No-op decorator
    mock_limiter_obj.key_func = MagicMock()

    # Patch slowapi.Limiter before any imports
    monkeypatch.setattr("slowapi.Limiter", lambda key_func: mock_limiter_obj)
    # Also patch the get_remote_address function
    monkeypatch.setattr("slowapi.util.get_remote_address", lambda x: "127.0.0.1")


@pytest.fixture
def test_client(mock_api_key):
    """Create a FastAPI TestClient with mocked dependencies.

    This fixture:
    - Sets up a test API key
    - Mocks GeminiRAG and StoreManager
    - Returns a TestClient ready for API testing
    """
    from rag import api

    # Mock the global RAG and manager instances
    mock_rag = Mock()
    mock_rag.query_by_role.return_value = {
        "answer": "Test answer from RAG",
        "citations": []
    }

    mock_manager = Mock()
    mock_manager.list_stores.return_value = [
        {
            "name": "stores/test-store-1",
            "display_name": "MINSAL Normativas Generales",
            "create_time": "2024-01-01T00:00:00Z"
        }
    ]

    # Patch the get_rag and get_manager functions
    with patch.object(api, 'get_rag', return_value=mock_rag):
        with patch.object(api, 'get_manager', return_value=mock_manager):
            client = TestClient(api.app)
            client.mock_rag = mock_rag
            client.mock_manager = mock_manager
            yield client


@pytest.fixture
def mock_gemini_response():
    """Mock a Gemini API response.

    Returns a dict with the structure returned by GeminiRAG.query()
    """
    return {
        "answer": "Según la guía MINSAL, el manejo de diabetes incluye: 1. Control glucémico, 2. Cambios en estilo de vida. [DIABETES-MELLITUS-TIPO-2-1.pdf, p.15]",
        "citations": [
            {
                "source": "DIABETES-MELLITUS-TIPO-2-1.pdf",
                "uri": "file:///documents/diabetes.pdf",
                "text": "Manejo integral de diabetes mellitus tipo 2"
            }
        ]
    }


@pytest.fixture
def mock_store_config():
    """Mock store configuration for testing."""
    return {
        "MINSAL_Normativas": {
            "display_name": "MINSAL Normativas Generales",
            "description": "Guías clínicas y normativas públicas del MINSAL",
            "roles": ["matrona", "medico", "secretaria"],
        },
        "MINSAL_Matronas": {
            "display_name": "MINSAL Protocolos Matronas",
            "description": "Protocolos de maternidad, control prenatal y ginecología",
            "roles": ["matrona"],
        },
        "MINSAL_Medicos": {
            "display_name": "MINSAL Guías Médicos",
            "description": "Guías clínicas especializadas para médicos",
            "roles": ["medico"],
        },
        "CESFAM_Procedimientos": {
            "display_name": "CESFAM Procedimientos Internos",
            "description": "Procedimientos administrativos y operativos del CESFAM",
            "roles": ["matrona", "medico", "secretaria"],
        },
    }
