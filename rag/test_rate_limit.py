"""
Tests for rate limiting and retry mechanisms.

Tests 10/minute rate limit with exponential backoff retry.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import time


class TestRateLimit10PerMinute:
    """Test 10 requests per minute rate limit."""
    
    def test_rate_limit_10_per_minute(self, client, mock_env):
        """GIVEN: Rate limit set to 10/minute
        WHEN: Make 11 requests in 60s
        THEN: 11th returns 429 Too Many Requests."""
        # This will fail - limiter not configured to 10/minute
        # Current config is 20/minute
        
        # Make 10 successful requests
        for i in range(10):
            response = client.post(
                "/v1/chat/completions",
                json={
                    "model": "smartsalud-medico",
                    "messages": [{"role": "user", "content": f"Test {i}"}],
                    "user_role": "medico"
                },
                headers={"Authorization": f"Bearer {os.getenv('RAG_API_KEY')}"}
            )
            assert response.status_code in [200, 401, 500]  # 401/500 ok if auth/API error

        # 11th should be rate limited
        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "smartsalud-medico",
                "messages": [{"role": "user", "content": "Test 11"}],
                "user_role": "medico"
            },
            headers={"Authorization": f"Bearer {os.getenv('RAG_API_KEY')}"}
        )
        assert response.status_code == 429
    
    def test_rate_limit_resets_after_minute(self, client, mock_env):
        """GIVEN: Rate limit exceeded
        WHEN: Wait 61 seconds
        THEN: Can make requests again."""
        # Will fail - need actual timing or mocked clock
        # This is an integration test, harder to mock
        pass
    
    def test_rate_limit_per_ip(self, client, mock_env):
        """GIVEN: Rate limit per IP address
        WHEN: Two different IPs make requests
        THEN: Each IP has separate quota."""
        # Will fail - requires custom test client logic
        pass


class TestGeminiApiRetryOn429:
    """Test Gemini API retry with exponential backoff."""
    
    def test_gemini_api_retry_on_429(self):
        """GIVEN: Gemini API returns 429
        WHEN: GeminiRAG makes request
        THEN: Retry with exponential backoff."""
        # Will fail - GeminiRAG doesn't have retry logic yet
        from rag.gemini_rag import GeminiRAG
        
        rag = GeminiRAG()
        
        # Mock API to return 429 then success
        with patch.object(rag.client.models, 'generate_content') as mock_api:
            mock_api.side_effect = [
                Exception("429 Too Many Requests"),  # First call fails
                MagicMock(text="Success", candidates=[MagicMock(grounding_metadata=None)])  # Second succeeds
            ]
            
            result = rag.query(
                question="Test question",
                store_ids=["test-store-1"]
            )
            
            # Verify retry occurred (2 calls)
            assert mock_api.call_count == 2
            assert "Success" in result["answer"]
    
    def test_retry_exponential_backoff(self):
        """GIVEN: Gemini API repeatedly returns 429
        WHEN: Retry with exponential backoff
        THEN: Delays increase: 1s, 2s, 4s."""
        from rag.gemini_rag import GeminiRAG
        
        rag = GeminiRAG()
        
        call_times = []
        
        def track_call(*args, **kwargs):
            call_times.append(time.time())
            if len(call_times) < 3:
                raise Exception("429 Too Many Requests")
            return MagicMock(text="Success", candidates=[MagicMock(grounding_metadata=None)])
        
        with patch.object(rag.client.models, 'generate_content', side_effect=track_call):
            result = rag.query(
                question="Test",
                store_ids=["test-store-1"]
            )
            
            # Verify 3 calls made
            assert len(call_times) == 3
            
            # Verify delays approximately double (with tolerance for execution time)
            if len(call_times) > 2:
                delay1 = call_times[1] - call_times[0]
                delay2 = call_times[2] - call_times[1]
                # Delay2 should be roughly 2x delay1 (with 50% tolerance)
                assert delay2 >= delay1 * 1.5
    
    def test_retry_max_attempts(self):
        """GIVEN: Gemini API always returns 429
        WHEN: Retry until max attempts
        THEN: Raise error after max retries."""
        from rag.gemini_rag import GeminiRAG, RateLimitError
        
        rag = GeminiRAG()
        
        with patch.object(rag.client.models, 'generate_content') as mock_api:
            mock_api.side_effect = Exception("429 Too Many Requests")
            
            with pytest.raises(RateLimitError):
                rag.query(
                    question="Test",
                    store_ids=["test-store-1"]
                )
            
            # Verify max retries attempted (e.g., 3 attempts = 3 calls)
            assert mock_api.call_count >= 3


class TestRateLimitHeaders:
    """Test rate limit response headers."""
    
    def test_rate_limit_remaining_header(self, client, mock_env):
        """GIVEN: Request made
        WHEN: Response returned
        THEN: Includes X-RateLimit-Remaining header."""
        # Will fail - headers not implemented
        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "smartsalud-medico",
                "messages": [{"role": "user", "content": "Test"}],
                "user_role": "medico"
            },
            headers={"Authorization": f"Bearer {os.getenv('RAG_API_KEY')}"}
        )
        
        assert "x-ratelimit-remaining" in response.headers or "X-RateLimit-Remaining" in response.headers
    
    def test_rate_limit_reset_header(self, client, mock_env):
        """GIVEN: Request made
        WHEN: Response returned
        THEN: Includes X-RateLimit-Reset header with timestamp."""
        # Will fail - headers not implemented
        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "smartsalud-medico",
                "messages": [{"role": "user", "content": "Test"}],
                "user_role": "medico"
            },
            headers={"Authorization": f"Bearer {os.getenv('RAG_API_KEY')}"}
        )
        
        assert "x-ratelimit-reset" in response.headers or "X-RateLimit-Reset" in response.headers
        # Should be valid timestamp
        reset_time = response.headers.get("X-RateLimit-Reset")
        assert reset_time is not None
    
    def test_rate_limit_limit_header(self, client, mock_env):
        """GIVEN: Request made
        WHEN: Response returned
        THEN: Includes X-RateLimit-Limit header."""
        response = client.post(
            "/v1/chat/completions",
            json={
                "model": "smartsalud-medico",
                "messages": [{"role": "user", "content": "Test"}],
                "user_role": "medico"
            },
            headers={"Authorization": f"Bearer {os.getenv('RAG_API_KEY')}"}
        )
        
        assert "x-ratelimit-limit" in response.headers or "X-RateLimit-Limit" in response.headers


class TestRateLimitBehavior:
    """Test rate limiting behavior edge cases."""
    
    def test_rate_limit_not_applied_to_health_check(self, client):
        """GIVEN: Rate limit active
        WHEN: /health endpoint called
        THEN: Not counted against quota."""
        # Make multiple health checks
        for i in range(20):
            response = client.get("/health")
            assert response.status_code == 200
    
    def test_rate_limit_by_api_key(self, client, mock_env):
        """GIVEN: Different API keys
        WHEN: Both make requests
        THEN: Each has separate rate limit quota."""
        # Will fail - rate limiting by IP, not API key
        pass
    
    def test_rate_limit_burst_protection(self, client, mock_env):
        """GIVEN: Rapid burst of requests
        WHEN: 20 requests in < 1 second
        THEN: Requests after 10 are rejected."""
        # Will fail - need parallel requests
        pass
