"""
File Search Store management for CESFAM roles.

Manages creation, listing, and role-based access to Gemini File Search stores.
"""

import os
import json
from pathlib import Path
from typing import Optional
from google import genai


# Store configuration by role
STORE_CONFIG = {
    "MINSAL_Normativas": {
        "display_name": "MINSAL Normativas Generales",
        "description": "Guías clínicas y normativas públicas del MINSAL",
        "roles": ["matrona", "medico", "secretaria"],  # All roles
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

# Document to store mapping
DOCUMENT_STORE_MAP = {
    "RE-GPC-Ca-de-Mama_06122023.pdf": "MINSAL_Normativas",
    "Guia-Practica-Manejo-Clinico-del-DENGUE.pdf": "MINSAL_Medicos",
    "RES.-EXENTA-N%C2%B0-741-GUIA-ASMA_2024.pdf": "MINSAL_Medicos",
    "08.-RE_GPC-ACV_2018v3.pdf": "MINSAL_Medicos",
    "DIABETES-MELLITUS-TIPO-2-1.pdf": "MINSAL_Normativas",
    "Orientacion-Tecnica-Cuidados-Paliativos-Universales.pdf": "MINSAL_Normativas",
}


class StoreManager:
    """Manages Gemini File Search stores for CESFAM."""

    def __init__(self, client: Optional[genai.Client] = None):
        """Initialize store manager.

        Args:
            client: Gemini client. If None, creates new one from env.
        """
        if client:
            self.client = client
        else:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not set")
            self.client = genai.Client(api_key=api_key)

        self._store_cache_file = Path(__file__).parent / ".store_cache.json"
        self._store_cache: dict = {}
        self._load_cache()

    def _load_cache(self):
        """Load store ID cache from disk."""
        if self._store_cache_file.exists():
            self._store_cache = json.loads(self._store_cache_file.read_text())

    def _save_cache(self):
        """Save store ID cache to disk."""
        self._store_cache_file.write_text(json.dumps(self._store_cache, indent=2))

    def create_store(self, name: str) -> str:
        """Create a File Search store.

        Args:
            name: Store name (key in STORE_CONFIG).

        Returns:
            Store ID (name from API).
        """
        if name in self._store_cache:
            print(f"Store '{name}' already exists: {self._store_cache[name]}")
            return self._store_cache[name]

        config = STORE_CONFIG.get(name)
        if not config:
            raise ValueError(f"Unknown store: {name}. Valid: {list(STORE_CONFIG.keys())}")

        store = self.client.file_search_stores.create(
            config={"display_name": config["display_name"]}
        )

        self._store_cache[name] = store.name
        self._save_cache()

        print(f"Created store '{name}': {store.name}")
        return store.name

    def create_all_stores(self) -> dict[str, str]:
        """Create all configured stores.

        Returns:
            Dict mapping store names to IDs.
        """
        result = {}
        for name in STORE_CONFIG:
            result[name] = self.create_store(name)
        return result

    def get_store_id(self, name: str) -> Optional[str]:
        """Get store ID by name.

        Args:
            name: Store name.

        Returns:
            Store ID or None if not found.
        """
        return self._store_cache.get(name)

    def get_stores_for_role(self, role: str) -> list[str]:
        """Get store IDs accessible by a role.

        Args:
            role: User role ('matrona', 'medico', 'secretaria').

        Returns:
            List of store IDs the role can access.
        """
        role = role.lower()
        store_ids = []

        for name, config in STORE_CONFIG.items():
            if role in config["roles"]:
                store_id = self._store_cache.get(name)
                if store_id:
                    store_ids.append(store_id)

        return store_ids

    def list_stores(self) -> list[dict]:
        """List all stores from API.

        Returns:
            List of store info dicts.
        """
        stores = list(self.client.file_search_stores.list())
        return [
            {
                "name": s.name,
                "display_name": s.display_name,
                "create_time": str(s.create_time) if hasattr(s, 'create_time') else None
            }
            for s in stores
        ]

    def delete_store(self, store_id: str):
        """Delete a store by ID.

        Args:
            store_id: The store ID to delete.
        """
        self.client.file_search_stores.delete(name=store_id)

        # Remove from cache
        for name, cached_id in list(self._store_cache.items()):
            if cached_id == store_id:
                del self._store_cache[name]
        self._save_cache()

        print(f"Deleted store: {store_id}")

    def get_target_store(self, filename: str) -> str:
        """Get target store name for a document.

        Args:
            filename: Document filename.

        Returns:
            Store name for the document.
        """
        return DOCUMENT_STORE_MAP.get(filename, "MINSAL_Normativas")


# CLI usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage File Search stores")
    parser.add_argument("action", choices=["create", "list", "delete", "role"])
    parser.add_argument("--name", help="Store name")
    parser.add_argument("--role", help="Role for 'role' action")
    args = parser.parse_args()

    manager = StoreManager()

    if args.action == "create":
        if args.name:
            manager.create_store(args.name)
        else:
            manager.create_all_stores()

    elif args.action == "list":
        stores = manager.list_stores()
        print(f"\nStores ({len(stores)}):")
        for s in stores:
            print(f"  - {s['display_name']}: {s['name']}")

    elif args.action == "delete" and args.name:
        store_id = manager.get_store_id(args.name) or args.name
        manager.delete_store(store_id)

    elif args.action == "role" and args.role:
        stores = manager.get_stores_for_role(args.role)
        print(f"\nStores for role '{args.role}':")
        for s in stores:
            print(f"  - {s}")
