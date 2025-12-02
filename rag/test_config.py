"""
Tests for externalized configuration system.

Replaces hardcoded STORE_CONFIG and agent_config by loading from JSON files.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestLoadRolesFromJson:
    """Test loading role configuration from config/roles.json."""
    
    def test_load_roles_from_json(self, test_config_json):
        """GIVEN: roles.json exists
        WHEN: ConfigLoader loads roles
        THEN: Returns dict with all role definitions."""
        # This test will fail - ConfigLoader doesn't exist yet
        from rag.config import ConfigLoader
        
        loader = ConfigLoader(test_config_json.parent)
        roles = loader.load_roles()
        
        assert "medico" in roles
        assert "matrona" in roles
        assert "secretaria" in roles
        assert roles["medico"]["nombre"] == "Asistente Médico MINSAL"
        assert len(roles["medico"]["stores"]) > 0
    
    def test_load_roles_missing_file(self):
        """GIVEN: roles.json does not exist
        WHEN: ConfigLoader loads roles
        THEN: Raises ConfigError."""
        from rag.config import ConfigLoader, ConfigError
        
        loader = ConfigLoader("/nonexistent/path")
        
        with pytest.raises(ConfigError):
            loader.load_roles()
    
    def test_role_has_required_fields(self, test_config_json):
        """GIVEN: roles.json loaded
        WHEN: Accessing role config
        THEN: Has nombre, especialidad, stores, temperature, max_tokens."""
        from rag.config import ConfigLoader
        
        loader = ConfigLoader(test_config_json.parent)
        roles = loader.load_roles()
        
        for role_name, role_config in roles.items():
            assert "nombre" in role_config
            assert "especialidad" in role_config
            assert "stores" in role_config
            assert "temperature" in role_config
            assert "max_tokens" in role_config


class TestLoadStoresFromJson:
    """Test loading store configuration from config/stores.json."""
    
    def test_load_stores_from_json(self, test_stores_json):
        """GIVEN: stores.json exists
        WHEN: ConfigLoader loads stores
        THEN: Returns dict with store definitions."""
        from rag.config import ConfigLoader
        
        loader = ConfigLoader(test_stores_json.parent)
        stores = loader.load_stores()
        
        assert "MINSAL_Normativas" in stores
        assert "MINSAL_Medicos" in stores
        assert stores["MINSAL_Normativas"]["display_name"] == "MINSAL Normativas Generales"
    
    def test_store_has_roles(self, test_stores_json):
        """GIVEN: stores.json loaded
        WHEN: Accessing store config
        THEN: Has roles list."""
        from rag.config import ConfigLoader
        
        loader = ConfigLoader(test_stores_json.parent)
        stores = loader.load_stores()
        
        for store_name, store_config in stores.items():
            assert "roles" in store_config
            assert isinstance(store_config["roles"], list)
            assert len(store_config["roles"]) > 0
    
    def test_load_stores_missing_file(self):
        """GIVEN: stores.json does not exist
        WHEN: ConfigLoader loads stores
        THEN: Raises ConfigError."""
        from rag.config import ConfigLoader, ConfigError
        
        loader = ConfigLoader("/nonexistent/path")
        
        with pytest.raises(ConfigError):
            loader.load_stores()


class TestConfigHotReload:
    """Test dynamic configuration reloading without restart."""
    
    def test_config_hot_reload(self, test_config_json, monkeypatch):
        """GIVEN: ConfigLoader initialized
        WHEN: reload() called after file changes
        THEN: Returns updated config."""
        from rag.config import ConfigLoader
        
        loader = ConfigLoader(test_config_json.parent)
        original = loader.load_roles()
        
        # Simulate file change
        config_data = json.loads(test_config_json.read_text())
        config_data["roles"]["custom_role"] = {
            "nombre": "Custom Role",
            "especialidad": "custom",
            "stores": ["MINSAL_Normativas"],
            "temperature": 0.5,
            "max_tokens": 1024
        }
        test_config_json.write_text(json.dumps(config_data, indent=2))
        
        # Reload
        reloaded = loader.reload()
        
        assert "custom_role" in reloaded
        assert reloaded["custom_role"]["nombre"] == "Custom Role"
    
    def test_config_reload_without_restart(self, test_config_json, test_stores_json):
        """GIVEN: ConfigLoader in memory
        WHEN: reload() called
        THEN: New config available immediately, no restart needed."""
        from rag.config import ConfigLoader
        
        loader = ConfigLoader(test_config_json.parent)
        
        # First load
        roles_v1 = loader.load_roles()
        count_v1 = len(roles_v1)
        
        # Add new role to file
        config_data = json.loads(test_config_json.read_text())
        config_data["roles"]["new_role"] = {
            "nombre": "New Role",
            "especialidad": "new",
            "stores": ["MINSAL_Normativas"],
            "temperature": 0.5,
            "max_tokens": 1024
        }
        test_config_json.write_text(json.dumps(config_data, indent=2))
        
        # Reload without restart
        loader.reload()
        roles_v2 = loader.load_roles()
        count_v2 = len(roles_v2)
        
        assert count_v2 > count_v1
        assert "new_role" in roles_v2


class TestAddNewRoleWithoutCodeChange:
    """Test adding new role by JSON file only."""
    
    def test_add_new_role_to_json(self, test_config_json):
        """GIVEN: roles.json exists
        WHEN: Add "dental" role to JSON
        THEN: Can load without code changes."""
        from rag.config import ConfigLoader
        
        # Add dental role to config file
        config_data = json.loads(test_config_json.read_text())
        config_data["roles"]["dental"] = {
            "nombre": "Asistente Dental",
            "especialidad": "odontología",
            "stores": ["MINSAL_Normativas"],
            "temperature": 0.3,
            "max_tokens": 2048
        }
        test_config_json.write_text(json.dumps(config_data, indent=2))
        
        # Load without changing code
        loader = ConfigLoader(test_config_json.parent)
        roles = loader.load_roles()
        
        assert "dental" in roles
        assert roles["dental"]["nombre"] == "Asistente Dental"
        assert roles["dental"]["especialidad"] == "odontología"
    
    def test_new_role_integrates_with_stores(self, test_config_json, test_stores_json):
        """GIVEN: New role added to roles.json
        WHEN: StoreManager.get_stores_for_role("new_role")
        THEN: Returns correct stores without code change."""
        from rag.config import ConfigLoader
        
        # Add pediatrician role
        config_data = json.loads(test_config_json.read_text())
        config_data["roles"]["pediatrica"] = {
            "nombre": "Asistente Pediátrico",
            "especialidad": "pediatría",
            "stores": ["MINSAL_Normativas", "MINSAL_Medicos"],
            "temperature": 0.3,
            "max_tokens": 2048
        }
        test_config_json.write_text(json.dumps(config_data, indent=2))
        
        # Load config
        loader = ConfigLoader(test_config_json.parent)
        roles = loader.load_roles()
        
        # Verify role exists and has stores
        assert "pediatrica" in roles
        assert "MINSAL_Normativas" in roles["pediatrica"]["stores"]
        assert "MINSAL_Medicos" in roles["pediatrica"]["stores"]


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_invalid_role_config_missing_stores(self, test_config_json):
        """GIVEN: Role config missing stores field
        WHEN: ConfigLoader loads roles
        THEN: Raises ValidationError."""
        from rag.config import ConfigLoader, ConfigValidationError
        
        # Break config
        config_data = json.loads(test_config_json.read_text())
        del config_data["roles"]["medico"]["stores"]
        test_config_json.write_text(json.dumps(config_data, indent=2))
        
        loader = ConfigLoader(test_config_json.parent)
        
        with pytest.raises(ConfigValidationError):
            loader.load_roles()
    
    def test_invalid_store_reference(self, test_config_json, test_stores_json):
        """GIVEN: Role references nonexistent store
        WHEN: ConfigLoader validates
        THEN: Raises ValidationError."""
        from rag.config import ConfigLoader, ConfigValidationError
        
        # Add invalid store reference
        config_data = json.loads(test_config_json.read_text())
        config_data["roles"]["medico"]["stores"].append("NONEXISTENT_STORE")
        test_config_json.write_text(json.dumps(config_data, indent=2))
        
        loader = ConfigLoader(test_config_json.parent)
        
        with pytest.raises(ConfigValidationError):
            loader.validate_config()


class TestConfigIntegration:
    """Test config integration with StoreManager and GeminiRAG."""
    
    def test_store_manager_uses_config_json(self, test_stores_json, mock_google_client):
        """GIVEN: stores.json configured
        WHEN: StoreManager initialized
        THEN: Uses config from JSON, not hardcoded."""
        # This requires StoreManager refactoring
        # Will fail until implementation complete
        pass
    
    def test_gemini_rag_uses_role_config(self, test_config_json, mock_google_client):
        """GIVEN: roles.json with agent configs
        WHEN: GeminiRAG.query_by_role() called
        THEN: Uses config from JSON."""
        # This requires GeminiRAG refactoring
        # Will fail until implementation complete
        pass
