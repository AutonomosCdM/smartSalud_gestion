"""Tests for smartSalud StoreManager.

Uses AAA pattern (Arrange-Act-Assert) for clarity and testability.
All tests verify real store behavior with actual assertions.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path


class TestStoreConfiguration:
    """Store configuration tests."""

    def test_store_config_has_required_stores(self):
        """ARRANGE: Import STORE_CONFIG
           ACT: Check required stores exist
           ASSERT: All required stores are defined
        """
        # ARRANGE
        from rag.stores import STORE_CONFIG

        # ASSERT - Required stores must exist
        required_stores = [
            "MINSAL_Normativas",
            "MINSAL_Matronas",
            "MINSAL_Medicos",
            "CESFAM_Procedimientos"
        ]
        for store_name in required_stores:
            assert store_name in STORE_CONFIG
            assert "display_name" in STORE_CONFIG[store_name]
            assert "description" in STORE_CONFIG[store_name]
            assert "roles" in STORE_CONFIG[store_name]

    def test_store_config_has_valid_roles(self):
        """ARRANGE: Import STORE_CONFIG
           ACT: Check all roles are valid
           ASSERT: Only valid roles are configured
        """
        # ARRANGE
        from rag.stores import STORE_CONFIG

        valid_roles = {"matrona", "medico", "secretaria"}

        # ACT & ASSERT
        for store_name, config in STORE_CONFIG.items():
            roles = set(config["roles"])
            assert roles.issubset(valid_roles), f"Invalid roles in {store_name}: {roles - valid_roles}"
            assert len(roles) > 0, f"Store {store_name} has no roles"

    def test_store_config_all_stores_accessible(self):
        """ARRANGE: Import STORE_CONFIG
           ACT: Check accessibility
           ASSERT: All stores are accessible to at least one role
        """
        # ARRANGE
        from rag.stores import STORE_CONFIG

        # ACT & ASSERT
        for store_name, config in STORE_CONFIG.items():
            assert len(config["roles"]) > 0, f"Store {store_name} not accessible to any role"

    def test_store_config_display_names_are_strings(self):
        """ARRANGE: Import STORE_CONFIG
           ACT: Check display names
           ASSERT: All display names are non-empty strings
        """
        # ARRANGE
        from rag.stores import STORE_CONFIG

        # ACT & ASSERT
        for store_name, config in STORE_CONFIG.items():
            display_name = config["display_name"]
            assert isinstance(display_name, str), f"Display name for {store_name} is not a string"
            assert len(display_name) > 0, f"Display name for {store_name} is empty"


class TestStoreManager:
    """StoreManager initialization and cache tests."""

    def test_store_manager_requires_api_key(self):
        """ARRANGE: Create StoreManager without API key
           ACT: Try to initialize
           ASSERT: ValueError is raised
        """
        # ARRANGE
        from rag.stores import StoreManager
        import os

        # Temporarily unset API key
        original_key = os.environ.get("GOOGLE_API_KEY")
        if "GOOGLE_API_KEY" in os.environ:
            del os.environ["GOOGLE_API_KEY"]

        try:
            # ACT & ASSERT
            with pytest.raises(ValueError, match="GOOGLE_API_KEY not set"):
                StoreManager()
        finally:
            # Restore original key
            if original_key:
                os.environ["GOOGLE_API_KEY"] = original_key

    def test_store_manager_with_client(self):
        """ARRANGE: Create mock Gemini client
           ACT: Initialize StoreManager with client
           ASSERT: Manager is created successfully
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        mock_client.file_search_stores = Mock()

        # ACT
        manager = StoreManager(client=mock_client)

        # ASSERT
        assert manager.client == mock_client

    def test_store_manager_creates_cache_file_path(self):
        """ARRANGE: Create mock Gemini client
           ACT: Initialize StoreManager
           ASSERT: Cache file path is set correctly
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()

        # ACT
        manager = StoreManager(client=mock_client)

        # ASSERT
        assert manager._store_cache_file is not None
        assert isinstance(manager._store_cache_file, Path)
        assert ".store_cache.json" in str(manager._store_cache_file)


class TestGetStoresForRole:
    """Tests for role-based store access."""

    def test_get_stores_for_role_medico(self):
        """ARRANGE: Create StoreManager with mocked client and cache
           ACT: Get stores for medico role
           ASSERT: Returns stores accessible to medico
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        manager = StoreManager(client=mock_client)

        # Pre-populate cache with store IDs
        manager._store_cache = {
            "MINSAL_Normativas": "stores/normativas-123",
            "MINSAL_Medicos": "stores/medicos-456",
            "MINSAL_Matronas": "stores/matronas-789",
            "CESFAM_Procedimientos": "stores/procedimientos-101"
        }

        # ACT
        stores = manager.get_stores_for_role("medico")

        # ASSERT
        assert isinstance(stores, list)
        assert len(stores) > 0
        # Medico should have access to MINSAL_Normativas and MINSAL_Medicos
        assert "stores/normativas-123" in stores
        assert "stores/medicos-456" in stores
        # Medico should NOT have access to MINSAL_Matronas
        assert "stores/matronas-789" not in stores

    def test_get_stores_for_role_matrona(self):
        """ARRANGE: Create StoreManager with mocked client and cache
           ACT: Get stores for matrona role
           ASSERT: Returns stores accessible to matrona
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        manager = StoreManager(client=mock_client)

        # Pre-populate cache
        manager._store_cache = {
            "MINSAL_Normativas": "stores/normativas-123",
            "MINSAL_Medicos": "stores/medicos-456",
            "MINSAL_Matronas": "stores/matronas-789",
            "CESFAM_Procedimientos": "stores/procedimientos-101"
        }

        # ACT
        stores = manager.get_stores_for_role("matrona")

        # ASSERT
        assert isinstance(stores, list)
        assert len(stores) > 0
        # Matrona should have access to all role-based stores
        assert "stores/normativas-123" in stores
        assert "stores/matronas-789" in stores
        assert "stores/procedimientos-101" in stores
        # Matrona should NOT have access to medico-only stores
        assert "stores/medicos-456" not in stores

    def test_get_stores_for_role_secretaria(self):
        """ARRANGE: Create StoreManager with mocked client and cache
           ACT: Get stores for secretaria role
           ASSERT: Returns stores accessible to secretaria
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        manager = StoreManager(client=mock_client)

        # Pre-populate cache
        manager._store_cache = {
            "MINSAL_Normativas": "stores/normativas-123",
            "MINSAL_Medicos": "stores/medicos-456",
            "MINSAL_Matronas": "stores/matronas-789",
            "CESFAM_Procedimientos": "stores/procedimientos-101"
        }

        # ACT
        stores = manager.get_stores_for_role("secretaria")

        # ASSERT
        assert isinstance(stores, list)
        assert len(stores) > 0
        # Secretaria should have access to general and procedimientos
        assert "stores/normativas-123" in stores
        assert "stores/procedimientos-101" in stores
        # Secretaria should NOT have access to specialized stores
        assert "stores/medicos-456" not in stores
        assert "stores/matronas-789" not in stores

    def test_get_stores_for_role_invalid_returns_empty(self):
        """ARRANGE: Create StoreManager with mocked client and cache
           ACT: Get stores for invalid role
           ASSERT: Returns empty list
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        manager = StoreManager(client=mock_client)

        # Pre-populate cache
        manager._store_cache = {
            "MINSAL_Normativas": "stores/normativas-123",
            "MINSAL_Medicos": "stores/medicos-456"
        }

        # ACT
        stores = manager.get_stores_for_role("invalid_role")

        # ASSERT
        assert isinstance(stores, list)
        assert len(stores) == 0

    def test_get_stores_for_role_case_insensitive(self):
        """ARRANGE: Create StoreManager with mocked client and cache
           ACT: Get stores with different case variations
           ASSERT: Returns same stores regardless of case
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        manager = StoreManager(client=mock_client)

        manager._store_cache = {
            "MINSAL_Normativas": "stores/normativas-123",
            "MINSAL_Medicos": "stores/medicos-456"
        }

        # ACT
        stores_lowercase = manager.get_stores_for_role("medico")
        stores_uppercase = manager.get_stores_for_role("MEDICO")
        stores_mixed = manager.get_stores_for_role("MeDiCo")

        # ASSERT
        assert stores_lowercase == stores_uppercase
        assert stores_lowercase == stores_mixed

    def test_get_stores_for_role_excludes_uncached_stores(self):
        """ARRANGE: Create StoreManager with incomplete cache
           ACT: Get stores for role
           ASSERT: Only returns stores that are in cache
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        manager = StoreManager(client=mock_client)

        # Only cache one store (incomplete)
        manager._store_cache = {
            "MINSAL_Normativas": "stores/normativas-123"
            # Missing MINSAL_Medicos, MINSAL_Matronas, CESFAM_Procedimientos
        }

        # ACT
        stores = manager.get_stores_for_role("medico")

        # ASSERT
        assert isinstance(stores, list)
        # Should only get the cached normativas store
        assert len(stores) == 1
        assert "stores/normativas-123" in stores


class TestGetStoreId:
    """Tests for getting individual store IDs."""

    def test_get_store_id_by_name(self):
        """ARRANGE: Create StoreManager with cached store
           ACT: Get store ID by name
           ASSERT: Returns correct store ID
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        manager = StoreManager(client=mock_client)

        manager._store_cache = {
            "MINSAL_Normativas": "stores/normativas-123"
        }

        # ACT
        store_id = manager.get_store_id("MINSAL_Normativas")

        # ASSERT
        assert store_id == "stores/normativas-123"

    def test_get_store_id_not_found_returns_none(self):
        """ARRANGE: Create StoreManager with cached store
           ACT: Get store ID for non-existent store
           ASSERT: Returns None
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        manager = StoreManager(client=mock_client)

        manager._store_cache = {}

        # ACT
        store_id = manager.get_store_id("NonExistentStore")

        # ASSERT
        assert store_id is None


class TestListStores:
    """Tests for listing stores from API."""

    def test_list_stores_returns_list(self):
        """ARRANGE: Create StoreManager with mocked API response
           ACT: Call list_stores()
           ASSERT: Returns list of store dicts
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        mock_store = Mock()
        mock_store.name = "stores/test-123"
        mock_store.display_name = "Test Store"
        mock_store.create_time = "2024-01-01T00:00:00Z"

        mock_client.file_search_stores.list.return_value = [mock_store]

        manager = StoreManager(client=mock_client)

        # ACT
        stores = manager.list_stores()

        # ASSERT
        assert isinstance(stores, list)
        assert len(stores) > 0

    def test_list_stores_includes_required_fields(self):
        """ARRANGE: Create StoreManager with mocked API response
           ACT: Call list_stores()
           ASSERT: Each store has required fields
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        mock_store = Mock()
        mock_store.name = "stores/test-123"
        mock_store.display_name = "Test Store"
        mock_store.create_time = "2024-01-01T00:00:00Z"

        mock_client.file_search_stores.list.return_value = [mock_store]

        manager = StoreManager(client=mock_client)

        # ACT
        stores = manager.list_stores()

        # ASSERT
        assert len(stores) > 0
        store = stores[0]
        assert "name" in store
        assert "display_name" in store
        assert "create_time" in store
        assert store["name"] == "stores/test-123"
        assert store["display_name"] == "Test Store"

    def test_list_stores_handles_missing_create_time(self):
        """ARRANGE: Create StoreManager with store missing create_time
           ACT: Call list_stores()
           ASSERT: Returns None for missing create_time
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        mock_store = Mock(spec=['name', 'display_name'])
        mock_store.name = "stores/test-123"
        mock_store.display_name = "Test Store"

        mock_client.file_search_stores.list.return_value = [mock_store]

        manager = StoreManager(client=mock_client)

        # ACT
        stores = manager.list_stores()

        # ASSERT
        assert len(stores) > 0
        assert stores[0]["create_time"] is None


class TestGetTargetStore:
    """Tests for document-to-store mapping."""

    def test_get_target_store_for_known_document(self):
        """ARRANGE: Create StoreManager
           ACT: Get target store for known document
           ASSERT: Returns correct store name
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        manager = StoreManager(client=mock_client)

        # ACT
        store = manager.get_target_store("DIABETES-MELLITUS-TIPO-2-1.pdf")

        # ASSERT
        assert store == "MINSAL_Normativas"

    def test_get_target_store_for_unknown_document_returns_default(self):
        """ARRANGE: Create StoreManager
           ACT: Get target store for unknown document
           ASSERT: Returns default store
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        manager = StoreManager(client=mock_client)

        # ACT
        store = manager.get_target_store("UnknownDocument.pdf")

        # ASSERT
        assert store == "MINSAL_Normativas"

    def test_get_target_store_for_medical_guide(self):
        """ARRANGE: Create StoreManager
           ACT: Get target store for medical guide
           ASSERT: Returns MINSAL_Medicos store
        """
        # ARRANGE
        from rag.stores import StoreManager

        mock_client = Mock()
        manager = StoreManager(client=mock_client)

        # ACT
        store = manager.get_target_store("Guia-Practica-Manejo-Clinico-del-DENGUE.pdf")

        # ASSERT
        assert store == "MINSAL_Medicos"
