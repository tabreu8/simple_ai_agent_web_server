"""
Test suite for the agent API endpoints.
"""

from fastapi.testclient import TestClient


class TestAgentAPI:
    """Test cases for agent API functionality using real implementation."""

    def test_agent_query_success(self, client: TestClient, openai_api_key):
        """Test successful agent query with real implementation."""
        query_data = {
            "query": "What is 2+2?",
            "session_id": "test_session",
            "model": "gpt-4.1-mini",  # Use the default test model
        }

        response = client.post("/agent/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        # Check that we got a response and session_id
        assert "response" in data
        assert "session_id" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
        assert data["session_id"] == "test_session"

    def test_agent_query_minimal_request(self, client: TestClient, openai_api_key):
        """Test agent query with minimal required data."""
        query_data = {"query": "Hello"}

        response = client.post("/agent/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        # Check that we got a response and session_id
        assert "response" in data
        assert "session_id" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
        # Session ID should be auto-generated (UUID format)
        assert len(data["session_id"]) == 36  # UUID length

    def test_agent_query_with_session_id_only(self, client: TestClient, openai_api_key):
        """Test agent query with session ID but no model."""
        query_data = {"query": "What is Python?", "session_id": "existing_session"}

        response = client.post("/agent/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        assert "response" in data
        assert "session_id" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
        assert data["session_id"] == "existing_session"

    def test_agent_query_missing_query(self, client: TestClient):
        """Test agent query without required query field."""
        response = client.post("/agent/query", json={})

        assert response.status_code == 422  # FastAPI validation error

        # Check that the error mentions the missing 'query' field
        error_detail = response.json()["detail"]
        assert any(error["loc"] == ["body", "query"] for error in error_detail)

    def test_agent_query_empty_query(self, client: TestClient):
        """Test agent query with empty query string."""
        response = client.post("/agent/query", json={"query": ""})

        assert response.status_code == 422  # FastAPI validation error for empty string

    def test_agent_query_special_characters(self, client: TestClient, openai_api_key):
        """Test agent query with special characters."""
        special_query = "What is 1+1? Answer with just the number."
        query_data = {"query": special_query}  # Use default model

        response = client.post("/agent/query", json=query_data)

        assert response.status_code == 200
        data = response.json()

        assert "response" in data
        assert "session_id" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0


class TestAgentIntegration:
    """Integration tests for agent functionality using real implementation."""

    def test_agent_conversation_flow(self, client: TestClient, openai_api_key):
        """Test a conversation flow with multiple agent queries."""
        # Start a conversation
        query_data = {
            "query": "My name is Alice. Remember this.",
            "model": "gpt-4.1-mini",
        }

        response = client.post("/agent/query", json=query_data)
        assert response.status_code == 200
        data = response.json()
        session_id = data["session_id"]

        # Continue the conversation in the same session
        query_data = {
            "query": "What is my name?",
            "session_id": session_id,
            "model": "gpt-4.1-mini",
        }

        response = client.post("/agent/query", json=query_data)
        assert response.status_code == 200
        data = response.json()

        # The agent should remember the name from the previous message
        assert data["session_id"] == session_id
        assert "Alice" in data["response"]

    def test_agent_model_switching(self, client: TestClient, openai_api_key):
        """Test switching between different models."""
        # Test with explicit model specification
        query_data = {"query": "Say 'Hello from gpt-4.1-mini'", "model": "gpt-4.1-mini"}

        response = client.post("/agent/query", json=query_data)
        assert response.status_code == 200
        data = response.json()

        assert "response" in data
        assert "session_id" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

        # Test with default model (no model specified)
        query_data = {"query": "Say 'Hello from default model'"}

        response = client.post("/agent/query", json=query_data)
        assert response.status_code == 200
        data = response.json()

        assert "response" in data
        assert "session_id" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

    def test_agent_concurrent_sessions(self, client: TestClient, openai_api_key):
        """Test handling multiple concurrent sessions."""
        sessions = []

        # Create multiple sessions with different contexts
        for i in range(3):
            query_data = {
                "query": f"My favorite number is {i}. Remember this.",
                "model": "gpt-4.1-mini",
            }

            response = client.post("/agent/query", json=query_data)
            assert response.status_code == 200
            data = response.json()
            sessions.append(data["session_id"])

        # Test that each session maintains its own context
        for i, session_id in enumerate(sessions):
            query_data = {
                "query": "What is my favorite number?",
                "session_id": session_id,
                "model": "gpt-4.1-mini",
            }

            response = client.post("/agent/query", json=query_data)
            assert response.status_code == 200
            data = response.json()

            # Each session should remember its own number
            assert str(i) in data["response"]
