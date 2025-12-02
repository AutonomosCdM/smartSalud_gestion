"""
File Search Store management for CESFAM roles.

Manages creation, listing, and role-based access to Gemini File Search stores.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional
from google import genai

# Redis import with graceful fallback
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


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

    def __init__(
        self,
        client: Optional[genai.Client] = None,
        redis_url: Optional[str] = None,
        cache_file: Optional[Path] = None
    ):
        """Initialize store manager.

        Args:
            client: Gemini client. If None, creates new one from env.
            redis_url: Redis connection URL. If None, checks REDIS_URL env var.
            cache_file: Path to file cache. If None, uses .store_cache.json.
        """
        if client:
            self.client = client
        else:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not set")
            self.client = genai.Client(api_key=api_key)

        # Setup Redis cache (optional)
        self.cache_backend = None
        redis_url = redis_url or os.getenv("REDIS_URL")
        if redis_url and REDIS_AVAILABLE:
            try:
                self.cache_backend = redis.from_url(redis_url, decode_responses=True)
                self.cache_backend.ping()  # Test connection
                logger.info(f"Redis cache connected: {redis_url}")
            except Exception as e:
                logger.warning(f"Redis unavailable, using file cache: {e}")
                self.cache_backend = None
        elif not REDIS_AVAILABLE:
            logger.info("Redis library not installed, using file cache")

        # File cache as fallback
        self._store_cache_file = cache_file or (Path(__file__).parent / ".store_cache.json")
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
        # Check if already cached
        existing_id = self.get_store_id(name)
        if existing_id:
            print(f"Store '{name}' already exists: {existing_id}")
            return existing_id

        config = STORE_CONFIG.get(name)
        if not config:
            raise ValueError(f"Unknown store: {name}. Valid: {list(STORE_CONFIG.keys())}")

        store = self.client.file_search_stores.create(
            config={"display_name": config["display_name"]}
        )

        # Cache with new method
        self.cache_store_id(name, store.name)

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

    def get_store_id(self, name: str, skip_file_cache: bool = False) -> Optional[str]:
        """Get store ID by name.

        Tries Redis first, then file cache (unless skipped), then API.

        Args:
            name: Store name.
            skip_file_cache: If True, skip file cache lookup (for testing).

        Returns:
            Store ID or None if not found.
        """
        # Try Redis cache first
        redis_checked = False
        redis_failed = False
        if self.cache_backend:
            redis_checked = True
            try:
                cached_id = self.cache_backend.get(f"store:{name}")
                if cached_id:
                    # Handle bytes from mocked Redis (decode_responses=False in tests)
                    if isinstance(cached_id, bytes):
                        cached_id = cached_id.decode('utf-8')
                    logger.debug(f"Redis cache hit for store: {name}")
                    return cached_id
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
                # Redis failed - don't use file cache, go straight to API for fresh data
                redis_failed = True
                redis_checked = True  # We tried, it failed

        # Fallback to file cache (skip if Redis is configured, or if Redis failed)
        if not skip_file_cache and not redis_checked and not redis_failed:
            cached_id = self._store_cache.get(name)
            if cached_id:
                logger.debug(f"File cache hit for store: {name}")
                # Sync to Redis if available
                if self.cache_backend:
                    try:
                        self.cache_backend.set(f"store:{name}", cached_id, ex=86400)
                    except Exception as e:
                        logger.warning(f"Redis set failed: {e}")
                return cached_id

        # Last resort: fetch from API
        store_id = self._fetch_from_api(name)
        if store_id:
            # Cache the API result (if _fetch_from_api didn't already)
            # This handles mocked _fetch_from_api in tests
            self.cache_store_id(name, store_id)
        return store_id

    def _fetch_from_api(self, name: str) -> Optional[str]:
        """Fetch store ID from Gemini API by listing stores.

        Args:
            name: Store name.

        Returns:
            Store ID or None if not found.
        """
        try:
            stores = list(self.client.file_search_stores.list())
            config = STORE_CONFIG.get(name)
            if not config:
                logger.warning(f"Unknown store name: {name}")
                return None

            # Find by display_name
            for store in stores:
                if store.display_name == config["display_name"]:
                    store_id = store.name
                    # Don't cache here - let get_store_id() handle caching
                    return store_id

            logger.warning(f"Store not found in API: {name}")
            return None
        except Exception as e:
            logger.error(f"API fetch failed: {e}")
            return None

    def cache_store_id(self, name: str, store_id: str, ttl: int = 86400):
        """Cache a store ID in Redis and file cache.

        Args:
            name: Store name.
            store_id: Store ID to cache.
            ttl: TTL in seconds (default 24 hours).
        """
        # Cache in Redis
        if self.cache_backend:
            try:
                self.cache_backend.set(f"store:{name}", store_id, ex=ttl)
                logger.debug(f"Cached in Redis: {name} -> {store_id}")
            except Exception as e:
                logger.warning(f"Redis cache failed: {e}")

        # Cache in file (no TTL for file)
        self._store_cache[name] = store_id
        self._save_cache()
        logger.debug(f"Cached in file: {name} -> {store_id}")

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
                # Also delete from Redis
                if self.cache_backend:
                    try:
                        self.cache_backend.delete(f"store:{name}")
                    except Exception as e:
                        logger.warning(f"Redis delete failed: {e}")
        self._save_cache()

        print(f"Deleted store: {store_id}")

    def delete_store_cache(self, name: str):
        """Delete a store from cache (not from API).

        Args:
            name: Store name.
        """
        # Delete from Redis
        if self.cache_backend:
            try:
                self.cache_backend.delete(f"store:{name}")
                logger.debug(f"Deleted from Redis cache: {name}")
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")

        # Delete from file cache
        if name in self._store_cache:
            del self._store_cache[name]
            self._save_cache()
            logger.debug(f"Deleted from file cache: {name}")

    def clear_cache(self):
        """Clear all store cache entries."""
        # Clear Redis cache
        if self.cache_backend:
            try:
                keys = self.cache_backend.keys("store:*")
                if keys:
                    self.cache_backend.delete(*keys)
                    logger.info(f"Cleared {len(keys)} Redis cache entries")
            except Exception as e:
                logger.warning(f"Redis clear failed: {e}")

        # Clear file cache
        self._store_cache.clear()
        self._save_cache()
        logger.info("Cleared file cache")

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
