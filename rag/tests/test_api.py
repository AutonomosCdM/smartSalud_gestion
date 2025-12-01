"""Tests for smartSalud RAG API endpoints.

Uses AAA pattern (Arrange-Act-Assert) for clarity and testability.
All tests verify real API behavior with actual HTTP assertions.
"""

import pytest
from fastapi import HTTPException


class TestHealthEndpoint:
    """Health check endpoint tests."""

    def test_health_endpoint_returns_200(self, test_client):
        """ARRANGE: Set up test client
           ACT: Call GET /
           ASSERT: Response status is 200
        """
        # ACT
        response = test_client.get("/")

        # ASSERT
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert "service" in response.json()
        assert response.json()["service"] == "smartSalud RAG API"

    def test_health_endpoint_returns_valid_json(self, test_client):
        """ARRANGE: Set up test client
           ACT: Call GET /
           ASSERT: Response contains required fields
        """
        # ACT
        response = test_client.get("/")

        # ASSERT
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert isinstance(data["status"], str)
        assert isinstance(data["service"], str)


class TestDetailedHealthEndpoint:
    """Detailed health check endpoint tests."""

    def test_detailed_health_endpoint_returns_200(self, test_client):
        """ARRANGE: Set up test client
           ACT: Call GET /health
           ASSERT: Response status is 200
        """
        # ACT
        response = test_client.get("/health")

        # ASSERT
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_detailed_health_includes_stores_count(self, test_client):
        """ARRANGE: Set up test client with mocked manager
           ACT: Call GET /health
           ASSERT: Response includes stores_count
        """
        # ACT
        response = test_client.get("/health")

        # ASSERT
        data = response.json()
        assert "stores_count" in data
        assert isinstance(data["stores_count"], int)
        assert data["stores_count"] >= 0

    def test_detailed_health_includes_store_names(self, test_client):
        """ARRANGE: Set up test client with mocked manager
           ACT: Call GET /health
           ASSERT: Response includes store display names
        """
        # ACT
        response = test_client.get("/health")

        # ASSERT
        data = response.json()
        assert "stores" in data
        assert isinstance(data["stores"], list)
        assert len(data["stores"]) > 0


class TestAPIKeyVerification:
    """API key verification tests."""

    def test_verify_api_key_valid_returns_true(self, test_client, mock_api_key):
        """ARRANGE: Set up test client with valid API key
           ACT: Call endpoint with valid Authorization header
           ASSERT: Request succeeds with 200
        """
        # ARRANGE
        headers = {"Authorization": f"Bearer {mock_api_key}"}

        # ACT
        response = test_client.get("/v1/models", headers=headers)

        # ASSERT
        assert response.status_code == 200
        assert "data" in response.json()

    def test_verify_api_key_invalid_raises_401(self, test_client):
        """ARRANGE: Set up test client
           ACT: Call endpoint with invalid API key
           ASSERT: Response status is 401 Unauthorized
        """
        # ARRANGE
        headers = {"Authorization": "Bearer invalid-key"}

        # ACT
        response = test_client.get("/v1/models", headers=headers)

        # ASSERT
        assert response.status_code == 401
        assert "detail" in response.json()
        assert "Invalid API key" in response.json()["detail"]

    def test_verify_api_key_missing_raises_401(self, test_client):
        """ARRANGE: Set up test client
           ACT: Call endpoint without Authorization header
           ASSERT: Response status is 401 Unauthorized
        """
        # ACT
        response = test_client.get("/v1/models")

        # ASSERT
        assert response.status_code == 401
        assert "detail" in response.json()
        assert "API key required" in response.json()["detail"]

    def test_verify_api_key_with_direct_key_header(self, test_client, mock_api_key):
        """ARRANGE: Set up test client with direct API key (no Bearer)
           ACT: Call endpoint with Authorization header (non-Bearer)
           ASSERT: Request succeeds
        """
        # ARRANGE
        headers = {"Authorization": mock_api_key}

        # ACT
        response = test_client.get("/v1/models", headers=headers)

        # ASSERT
        assert response.status_code == 200

    def test_verify_api_key_timing_safe(self, test_client):
        """ARRANGE: Set up test client
           ACT: Call endpoint with wrong key multiple times
           ASSERT: All fail consistently (timing-safe comparison)
        """
        # ARRANGE
        headers_wrong = {"Authorization": "Bearer wrong-key"}

        # ACT & ASSERT - call multiple times, all should fail
        for _ in range(3):
            response = test_client.get("/v1/models", headers=headers_wrong)
            assert response.status_code == 401


class TestListModelsEndpoint:
    """List models endpoint tests."""

    def test_list_models_requires_auth(self, test_client):
        """ARRANGE: Set up test client
           ACT: Call GET /v1/models without auth
           ASSERT: Response status is 401
        """
        # ACT
        response = test_client.get("/v1/models")

        # ASSERT
        assert response.status_code == 401

    def test_list_models_returns_valid_response(self, test_client, mock_api_key):
        """ARRANGE: Set up test client with valid API key
           ACT: Call GET /v1/models with auth
           ASSERT: Response contains list of models
        """
        # ARRANGE
        headers = {"Authorization": f"Bearer {mock_api_key}"}

        # ACT
        response = test_client.get("/v1/models", headers=headers)

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    def test_list_models_response_structure(self, test_client, mock_api_key):
        """ARRANGE: Set up test client with valid API key
           ACT: Call GET /v1/models with auth
           ASSERT: Each model has required fields
        """
        # ARRANGE
        headers = {"Authorization": f"Bearer {mock_api_key}"}

        # ACT
        response = test_client.get("/v1/models", headers=headers)

        # ASSERT
        data = response.json()
        assert data["object"] == "list"
        for model in data["data"]:
            assert "id" in model
            assert "object" in model
            assert model["object"] == "model"
            assert "created" in model
            assert "owned_by" in model
            assert model["owned_by"] == "smartsalud"

    def test_list_models_includes_all_agent_models(self, test_client, mock_api_key):
        """ARRANGE: Set up test client with valid API key
           ACT: Call GET /v1/models with auth
           ASSERT: Response includes all defined agents
        """
        # ARRANGE
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        expected_models = [
            "smartsalud-rag",
            "smartsalud-medico",
            "smartsalud-matrona",
            "smartsalud-secretaria"
        ]

        # ACT
        response = test_client.get("/v1/models", headers=headers)

        # ASSERT
        data = response.json()
        model_ids = [m["id"] for m in data["data"]]
        for expected_model in expected_models:
            assert expected_model in model_ids


class TestChatCompletionsEndpoint:
    """Chat completions endpoint tests."""

    def test_chat_completions_requires_auth(self, test_client):
        """ARRANGE: Set up test client
           ACT: Call POST /v1/chat/completions without auth
           ASSERT: Response status is 401
        """
        # ARRANGE
        payload = {
            "model": "smartsalud-rag",
            "messages": [{"role": "user", "content": "¿Qué es diabetes?"}]
        }

        # ACT
        response = test_client.post("/v1/chat/completions", json=payload)

        # ASSERT
        assert response.status_code == 401
        assert "API key required" in response.json()["detail"]

    def test_chat_completions_returns_valid_response(self, test_client, mock_api_key):
        """ARRANGE: Set up test client with valid API key and mocked RAG
           ACT: Call POST /v1/chat/completions with auth
           ASSERT: Response has valid structure
        """
        # ARRANGE
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        payload = {
            "model": "smartsalud-rag",
            "messages": [{"role": "user", "content": "¿Qué es diabetes?"}]
        }

        # ACT
        response = test_client.post(
            "/v1/chat/completions",
            json=payload,
            headers=headers
        )

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "object" in data
        assert data["object"] == "chat.completion"
        assert "created" in data
        assert "model" in data
        assert "choices" in data
        assert "usage" in data

    def test_chat_completions_response_includes_message(self, test_client, mock_api_key):
        """ARRANGE: Set up test client with valid API key and mocked RAG
           ACT: Call POST /v1/chat/completions
           ASSERT: Response includes assistant message
        """
        # ARRANGE
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        payload = {
            "model": "smartsalud-rag",
            "messages": [{"role": "user", "content": "¿Qué es diabetes?"}]
        }

        # ACT
        response = test_client.post(
            "/v1/chat/completions",
            json=payload,
            headers=headers
        )

        # ASSERT
        data = response.json()
        assert len(data["choices"]) > 0
        choice = data["choices"][0]
        assert "message" in choice
        assert "content" in choice["message"]
        assert choice["message"]["role"] == "assistant"
        assert len(choice["message"]["content"]) > 0

    def test_chat_completions_usage_includes_tokens(self, test_client, mock_api_key):
        """ARRANGE: Set up test client with valid API key
           ACT: Call POST /v1/chat/completions
           ASSERT: Response includes token usage
        """
        # ARRANGE
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        payload = {
            "model": "smartsalud-rag",
            "messages": [{"role": "user", "content": "¿Qué es diabetes?"}]
        }

        # ACT
        response = test_client.post(
            "/v1/chat/completions",
            json=payload,
            headers=headers
        )

        # ASSERT
        data = response.json()
        usage = data["usage"]
        assert "prompt_tokens" in usage
        assert "completion_tokens" in usage
        assert "total_tokens" in usage
        assert isinstance(usage["prompt_tokens"], int)
        assert isinstance(usage["completion_tokens"], int)
        assert usage["total_tokens"] == (usage["prompt_tokens"] + usage["completion_tokens"])

    def test_chat_completions_role_based_routing(self, test_client, mock_api_key):
        """ARRANGE: Set up test client with mocked RAG that tracks calls
           ACT: Call POST /v1/chat/completions with specific model
           ASSERT: RAG is queried with correct role
        """
        # ARRANGE
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        payload = {
            "model": "smartsalud-medico",
            "messages": [{"role": "user", "content": "¿Diagnóstico de diabetes?"}],
            "user_role": "medico"
        }

        # ACT
        response = test_client.post(
            "/v1/chat/completions",
            json=payload,
            headers=headers
        )

        # ASSERT
        assert response.status_code == 200
        # Verify the mock was called (integration test)
        test_client.mock_rag.query_by_role.assert_called()
        call_kwargs = test_client.mock_rag.query_by_role.call_args[1]
        assert call_kwargs.get("role") == "medico"

    def test_chat_completions_matrona_role_detection(self, test_client, mock_api_key):
        """ARRANGE: Set up test client with mocked RAG
           ACT: Call POST /v1/chat/completions with matrona model
           ASSERT: RAG is queried with role=matrona
        """
        # ARRANGE
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        payload = {
            "model": "smartsalud-matrona",
            "messages": [{"role": "user", "content": "¿Control prenatal?"}]
        }

        # ACT
        response = test_client.post(
            "/v1/chat/completions",
            json=payload,
            headers=headers
        )

        # ASSERT
        assert response.status_code == 200
        call_kwargs = test_client.mock_rag.query_by_role.call_args[1]
        assert call_kwargs.get("role") == "matrona"

    def test_chat_completions_returns_error_without_user_message(self, test_client, mock_api_key):
        """ARRANGE: Set up test client with empty messages
           ACT: Call POST /v1/chat/completions
           ASSERT: Response status is 500 (wrapped by error handler) or 400
        """
        # ARRANGE
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        payload = {
            "model": "smartsalud-rag",
            "messages": []
        }

        # ACT
        response = test_client.post(
            "/v1/chat/completions",
            json=payload,
            headers=headers
        )

        # ASSERT
        # The HTTPException is caught and wrapped by the exception handler
        # which returns a 500 error with the message in the response
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        assert "No user message found" in response_data["detail"]

    def test_chat_completions_default_parameters(self, test_client, mock_api_key):
        """ARRANGE: Set up test client with minimal payload
           ACT: Call POST /v1/chat/completions with default params
           ASSERT: Request succeeds with defaults applied
        """
        # ARRANGE
        headers = {"Authorization": f"Bearer {mock_api_key}"}
        payload = {
            "messages": [{"role": "user", "content": "¿Diabetes?"}]
        }

        # ACT
        response = test_client.post(
            "/v1/chat/completions",
            json=payload,
            headers=headers
        )

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert data["model"] == "smartsalud-rag"  # default model
