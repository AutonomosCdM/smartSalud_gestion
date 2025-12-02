"""
Tests for Redis cache system.

Replaces .store_cache.json with Redis-based caching for store IDs.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import json


class TestRedisStoreCacheGet:
    """Test Redis cache retrieval for store IDs."""
    
    def test_redis_store_cache_get(self, mock_redis):
        """GIVEN: Redis client connected
        WHEN: StoreManager.get_store_id("MINSAL_Medicos")
        THEN: Query Redis first."""
        # Will fail - StoreManager.cache_backend doesn't exist yet
        from rag.stores import StoreManager
        
        with patch('rag.stores.redis.Redis', return_value=mock_redis):
            manager = StoreManager()
            manager.cache_backend = mock_redis
            
            # Mock Redis response
            mock_redis.get.return_value = b"projects/test/locations/us/fileStores/12345"
            
            store_id = manager.get_store_id("MINSAL_Medicos")
            
            # Verify Redis was called first
            mock_redis.get.assert_called_once()
            assert store_id == "projects/test/locations/us/fileStores/12345"
    
    def test_redis_get_cache_hit(self, mock_redis):
        """GIVEN: Store ID exists in Redis
        WHEN: get_store_id() called
        THEN: Returns cached ID immediately."""
        from rag.stores import StoreManager
        
        with patch('rag.stores.redis.Redis', return_value=mock_redis):
            manager = StoreManager()
            manager.cache_backend = mock_redis
            
            # Setup cache hit
            cached_id = "projects/test/locations/us/fileStores/99999"
            mock_redis.get.return_value = cached_id.encode()
            
            result = manager.get_store_id("MINSAL_Normativas")
            
            assert result == cached_id
            mock_redis.get.assert_called_with("store:MINSAL_Normativas")
    
    def test_redis_cache_key_format(self, mock_redis):
        """GIVEN: Redis cache
        WHEN: Storing store ID
        THEN: Uses consistent key format: store:{name}."""
        from rag.stores import StoreManager
        
        with patch('rag.stores.redis.Redis', return_value=mock_redis):
            manager = StoreManager()
            manager.cache_backend = mock_redis
            
            manager.cache_store_id("MINSAL_Medicos", "store-id-123")
            
            # Verify key format
            mock_redis.set.assert_called()
            call_args = mock_redis.set.call_args
            assert call_args[0][0] == "store:MINSAL_Medicos"


class TestCacheMissFallbackToApi:
    """Test fallback to Gemini API when cache misses."""
    
    def test_cache_miss_fallback_to_api(self, mock_redis, mock_google_client):
        """GIVEN: Store ID not in Redis
        WHEN: get_store_id() called
        THEN: Fetch from Gemini API."""
        from rag.stores import StoreManager
        
        with patch('rag.stores.redis.Redis', return_value=mock_redis):
            # Cache miss
            mock_redis.get.return_value = None
            
            manager = StoreManager(client=mock_google_client)
            manager.cache_backend = mock_redis
            
            # Mock API call
            api_store_id = "projects/test/locations/us/fileStores/api-result"
            with patch.object(manager, '_fetch_from_api', return_value=api_store_id):
                result = manager.get_store_id("MINSAL_Medicos")
            
            assert result == api_store_id
            # Verify fallback to API
            mock_redis.get.assert_called()
    
    def test_cache_result_after_api_fetch(self, mock_redis, mock_google_client):
        """GIVEN: Cache miss, API returns ID
        WHEN: get_store_id() completes
        THEN: Cache result for future requests."""
        from rag.stores import StoreManager
        
        with patch('rag.stores.redis.Redis', return_value=mock_redis):
            mock_redis.get.return_value = None
            
            manager = StoreManager(client=mock_google_client)
            manager.cache_backend = mock_redis
            
            api_result = "projects/test/locations/us/fileStores/123"
            with patch.object(manager, '_fetch_from_api', return_value=api_result):
                manager.get_store_id("MINSAL_Medicos")
            
            # Verify result was cached
            mock_redis.set.assert_called()
            call_args = mock_redis.set.call_args
            assert api_result in str(call_args)


class TestRedisFailureGracefulDegradation:
    """Test graceful fallback when Redis fails."""
    
    def test_redis_connection_failure_fallback(self, mock_google_client):
        """GIVEN: Redis connection fails
        WHEN: get_store_id() called
        THEN: Direct API calls without crash."""
        from rag.stores import StoreManager
        
        # Simulate Redis connection error
        broken_redis = MagicMock()
        broken_redis.get.side_effect = Exception("Redis connection refused")
        
        with patch('rag.stores.redis.Redis', return_value=broken_redis):
            manager = StoreManager(client=mock_google_client)
            manager.cache_backend = broken_redis
            
            # Should not crash, should use API
            with patch.object(manager, '_fetch_from_api', return_value="fallback-store-id"):
                result = manager.get_store_id("MINSAL_Medicos")
            
            assert result == "fallback-store-id"
    
    def test_redis_timeout_graceful_degradation(self, mock_google_client):
        """GIVEN: Redis timeout occurs
        WHEN: get_store_id() called
        THEN: Uses API instead of crashing."""
        from rag.stores import StoreManager
        
        timeout_redis = MagicMock()
        timeout_redis.get.side_effect = TimeoutError("Redis timeout")
        
        with patch('rag.stores.redis.Redis', return_value=timeout_redis):
            manager = StoreManager(client=mock_google_client)
            manager.cache_backend = timeout_redis
            
            with patch.object(manager, '_fetch_from_api', return_value="api-store-id"):
                result = manager.get_store_id("MINSAL_Medicos")
            
            # Should succeed via API
            assert result == "api-store-id"
    
    def test_no_crash_on_redis_error(self, mock_google_client):
        """GIVEN: Any Redis error occurs
        WHEN: Cache operation fails
        THEN: Does not raise, continues to API."""
        from rag.stores import StoreManager
        
        error_redis = MagicMock()
        error_redis.get.side_effect = RuntimeError("Redis unknown error")
        error_redis.set.side_effect = RuntimeError("Redis unknown error")
        
        with patch('rag.stores.redis.Redis', return_value=error_redis):
            manager = StoreManager(client=mock_google_client)
            manager.cache_backend = error_redis
            
            # Should complete without raising
            try:
                with patch.object(manager, '_fetch_from_api', return_value="store-id"):
                    manager.get_store_id("MINSAL_Medicos")
                succeeded = True
            except Exception:
                succeeded = False
            
            assert succeeded


class TestCacheInvalidation:
    """Test cache invalidation and refresh."""
    
    def test_invalidate_cache_entry(self, mock_redis):
        """GIVEN: Store ID cached
        WHEN: delete_store() called
        THEN: Remove from cache."""
        from rag.stores import StoreManager
        
        with patch('rag.stores.redis.Redis', return_value=mock_redis):
            manager = StoreManager()
            manager.cache_backend = mock_redis
            
            manager.delete_store_cache("MINSAL_Medicos")
            
            # Verify Redis delete called
            mock_redis.delete.assert_called_with("store:MINSAL_Medicos")
    
    def test_clear_all_cache(self, mock_redis):
        """GIVEN: Multiple stores cached
        WHEN: clear_cache() called
        THEN: Remove all store cache entries."""
        from rag.stores import StoreManager
        
        with patch('rag.stores.redis.Redis', return_value=mock_redis):
            manager = StoreManager()
            manager.cache_backend = mock_redis
            
            # Mock pattern search
            mock_redis.keys.return_value = [
                b"store:MINSAL_Normativas",
                b"store:MINSAL_Medicos",
                b"store:MINSAL_Matronas"
            ]
            
            manager.clear_cache()
            
            # Verify all keys deleted
            mock_redis.keys.assert_called()
            mock_redis.delete.assert_called()


class TestCacheExpiration:
    """Test cache TTL and expiration."""
    
    def test_cache_entry_ttl(self, mock_redis):
        """GIVEN: Store ID cached
        WHEN: set() called
        THEN: Set TTL for expiration."""
        from rag.stores import StoreManager
        
        with patch('rag.stores.redis.Redis', return_value=mock_redis):
            manager = StoreManager()
            manager.cache_backend = mock_redis
            
            manager.cache_store_id("MINSAL_Medicos", "store-id-123")
            
            # Verify TTL was set (24 hours = 86400 seconds)
            call_args = mock_redis.set.call_args
            assert 'ex' in call_args.kwargs or len(call_args.args) > 2
    
    def test_cache_expiration_triggers_refresh(self, mock_redis, mock_google_client):
        """GIVEN: Cache entry expired
        WHEN: get_store_id() called
        THEN: Refresh from API."""
        from rag.stores import StoreManager
        
        with patch('rag.stores.redis.Redis', return_value=mock_redis):
            # Simulate expiration (cache returns None)
            mock_redis.get.return_value = None
            
            manager = StoreManager(client=mock_google_client)
            manager.cache_backend = mock_redis
            
            with patch.object(manager, '_fetch_from_api', return_value="refreshed-id"):
                result = manager.get_store_id("MINSAL_Medicos")
            
            assert result == "refreshed-id"
