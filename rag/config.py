"""
Configuration loader for smartSalud RAG.

Externalizes role and store configuration to JSON files for hot-reload
without code changes.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Configuration file not found or unreadable."""
    pass


class ConfigValidationError(Exception):
    """Configuration validation failed."""
    pass


class ConfigLoader:
    """
    Load and manage configuration from JSON files.

    Supports hot-reload without restart.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize ConfigLoader.

        Args:
            config_dir: Directory containing roles.json and stores.json.
                       Defaults to project_root/config/
        """
        if config_dir:
            self.config_dir = Path(config_dir) if isinstance(config_dir, str) else config_dir
        else:
            self.config_dir = Path(__file__).parent.parent / "config"

        self._roles: Dict[str, Dict[str, Any]] = {}
        self._stores: Dict[str, Dict[str, Any]] = {}

        logger.info(f"ConfigLoader initialized with config_dir: {self.config_dir}")

    def load_roles(self) -> Dict[str, Dict[str, Any]]:
        """
        Load roles from config/roles.json.

        Returns:
            Dict mapping role names to role configuration.

        Raises:
            ConfigError: If roles.json not found or unreadable.
            ConfigValidationError: If role config missing required fields.
        """
        roles_file = self.config_dir / "roles.json"

        if not roles_file.exists():
            raise ConfigError(f"Roles configuration not found: {roles_file}")

        try:
            with open(roles_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise ConfigError(f"Failed to load roles.json: {e}")

        # Handle nested "roles" key from test fixture
        if "roles" in data:
            roles_data = data["roles"]
        else:
            roles_data = data

        # Validate required fields
        for role_name, role_config in roles_data.items():
            required_fields = ["nombre", "especialidad", "stores", "temperature", "max_tokens"]
            for field in required_fields:
                if field not in role_config:
                    raise ConfigValidationError(
                        f"Role '{role_name}' missing required field: {field}"
                    )

        self._roles = roles_data
        logger.info(f"Loaded {len(self._roles)} roles from {roles_file}")
        return self._roles

    def load_stores(self, raise_on_missing: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        Load stores from config/stores.json.

        Args:
            raise_on_missing: If False, return empty dict if file missing (for hot reload).

        Returns:
            Dict mapping store names to store configuration.

        Raises:
            ConfigError: If stores.json not found or unreadable (when raise_on_missing=True).
        """
        stores_file = self.config_dir / "stores.json"

        if not stores_file.exists():
            if raise_on_missing:
                raise ConfigError(f"Stores configuration not found: {stores_file}")
            else:
                logger.warning(f"Stores config not found (skipping): {stores_file}")
                self._stores = {}
                return self._stores

        try:
            with open(stores_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise ConfigError(f"Failed to load stores.json: {e}")

        # Handle nested "stores" key from test fixture
        if "stores" in data:
            stores_data = data["stores"]
        else:
            stores_data = data

        self._stores = stores_data
        logger.info(f"Loaded {len(self._stores)} stores from {stores_file}")
        return self._stores

    def reload(self) -> Dict[str, Dict[str, Any]]:
        """
        Hot reload configuration from disk without restart.

        Returns:
            Updated roles configuration.
        """
        logger.info("Reloading configuration...")
        self._roles.clear()
        self._stores.clear()

        # Reload both files (stores.json optional for hot reload)
        self.load_roles()
        self.load_stores(raise_on_missing=False)

        return self._roles

    def validate_config(self):
        """
        Validate that role store references exist in store config.

        Raises:
            ConfigValidationError: If role references nonexistent store.
        """
        if not self._roles:
            self.load_roles()
        if not self._stores:
            self.load_stores()

        for role_name, role_config in self._roles.items():
            for store_name in role_config.get("stores", []):
                if store_name not in self._stores:
                    raise ConfigValidationError(
                        f"Role '{role_name}' references nonexistent store: {store_name}"
                    )

        logger.info("Configuration validation passed")

    def get_role(self, name: str) -> Optional[Dict[str, Any]]:
        """Get role configuration by name."""
        if not self._roles:
            self.load_roles()
        return self._roles.get(name)

    def get_store(self, name: str) -> Optional[Dict[str, Any]]:
        """Get store configuration by name."""
        if not self._stores:
            self.load_stores()
        return self._stores.get(name)

    def get_stores_for_role(self, role: str) -> list[str]:
        """Get list of store names for a given role."""
        role_config = self.get_role(role)
        if not role_config:
            return []
        return role_config.get("stores", [])

    def list_roles(self) -> list[str]:
        """List all role names."""
        if not self._roles:
            self.load_roles()
        return list(self._roles.keys())

    def list_stores(self) -> list[str]:
        """List all store names."""
        if not self._stores:
            self.load_stores()
        return list(self._stores.keys())
