"""
Pytest fixtures for smartSalud RAG tests.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi.testclient import TestClient
import json
from pathlib import Path


@pytest.fixture
def mock_redis():
    """Mock Redis client for cache testing."""
    redis_mock = MagicMock()
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = True
    redis_mock.exists.return_value = False
    return redis_mock


@pytest.fixture
def mock_google_client():
    """Mock Google Genai client."""
    client_mock = MagicMock()
    
    # Mock file search stores
    store_mock = MagicMock()
    store_mock.name = "projects/test-project/locations/us/fileStores/12345"
    store_mock.display_name = "Test Store"
    
    client_mock.file_search_stores.create.return_value = store_mock
    client_mock.file_search_stores.list.return_value = [store_mock]
    client_mock.file_search_stores.delete.return_value = None
    
    # Mock chat completions
    response_mock = MagicMock()
    response_mock.text = "Test response"
    response_mock.candidates = [MagicMock()]
    response_mock.candidates[0].grounding_metadata = None
    
    client_mock.models.generate_content.return_value = response_mock
    
    return client_mock


@pytest.fixture
def mock_store_cache(tmp_path):
    """Mock store cache file."""
    cache_file = tmp_path / ".store_cache.json"
    cache_data = {
        "MINSAL_Normativas": "projects/test/locations/us/fileStores/11111",
        "MINSAL_Medicos": "projects/test/locations/us/fileStores/22222",
        "MINSAL_Matronas": "projects/test/locations/us/fileStores/33333",
        "CESFAM_Procedimientos": "projects/test/locations/us/fileStores/44444",
    }
    cache_file.write_text(json.dumps(cache_data))
    return cache_file


@pytest.fixture
def client():
    """FastAPI test client."""
    from rag.api import app
    return TestClient(app)


@pytest.fixture
def mock_env(monkeypatch):
    """Set required environment variables."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key-12345")
    monkeypatch.setenv("RAG_API_KEY", "test-rag-api-key-67890")
    return monkeypatch


@pytest.fixture
def test_config_json(tmp_path):
    """Create test config/roles.json."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    roles_data = {
        "roles": {
            "medico": {
                "nombre": "Asistente Médico MINSAL",
                "especialidad": "guías clínicas",
                "stores": ["MINSAL_Normativas", "MINSAL_Medicos"],
                "temperature": 0.3,
                "max_tokens": 2048
            },
            "matrona": {
                "nombre": "Asistente Matrona MINSAL",
                "especialidad": "maternidad",
                "stores": ["MINSAL_Normativas", "MINSAL_Matronas"],
                "temperature": 0.3,
                "max_tokens": 2048
            },
            "secretaria": {
                "nombre": "Asistente Administrativo",
                "especialidad": "procedimientos",
                "stores": ["CESFAM_Procedimientos"],
                "temperature": 0.3,
                "max_tokens": 1024
            }
        }
    }
    
    config_file = config_dir / "roles.json"
    config_file.write_text(json.dumps(roles_data, indent=2))
    return config_file


@pytest.fixture
def test_stores_json(tmp_path):
    """Create test config/stores.json."""
    config_dir = tmp_path / "config"
    config_dir.mkdir(exist_ok=True)
    
    stores_data = {
        "stores": {
            "MINSAL_Normativas": {
                "display_name": "MINSAL Normativas Generales",
                "description": "Test normativas",
                "roles": ["matrona", "medico", "secretaria"]
            },
            "MINSAL_Medicos": {
                "display_name": "MINSAL Guías Médicos",
                "description": "Test guías médicos",
                "roles": ["medico"]
            },
            "MINSAL_Matronas": {
                "display_name": "MINSAL Protocolos Matronas",
                "description": "Test maternidad",
                "roles": ["matrona"]
            },
            "CESFAM_Procedimientos": {
                "display_name": "CESFAM Procedimientos",
                "description": "Test procedimientos",
                "roles": ["matrona", "medico", "secretaria"]
            }
        }
    }
    
    stores_file = config_dir / "stores.json"
    stores_file.write_text(json.dumps(stores_data, indent=2))
    return stores_file
