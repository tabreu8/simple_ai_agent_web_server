"""
Test suite for the agent API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


class TestAgentAPI:
    """Test cases for agent API functionality."""
    
    @patch('routes.agent_api.run_agent')
    def test_agent_query_success(self, mock_run_agent, client: TestClient):
        """Test successful agent query."""
        # Mock the agent response
        mock_run_agent.return_value = ("Test response from agent", "session_123")
        
        query_data = {
            "query": "What is machine learning?",
            "session_id": "test_session",
            "model": "gpt-4"
        }
        
        response = client.post("/agent/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["response"] == "Test response from agent"
        assert data["session_id"] == "session_123"
        
        # Verify that run_agent was called with correct parameters
        mock_run_agent.assert_called_once_with(
            "What is machine learning?", 
            "test_session", 
            "gpt-4"
        )
    
    @patch('routes.agent_api.run_agent')
    def test_agent_query_minimal_request(self, mock_run_agent, client: TestClient):
        """Test agent query with minimal required data."""
        mock_run_agent.return_value = ("Minimal response", "new_session_456")
        
        query_data = {"query": "Simple test query"}
        
        response = client.post("/agent/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["response"] == "Minimal response"
        assert data["session_id"] == "new_session_456"
        
        # Verify that run_agent was called with None for optional parameters
        mock_run_agent.assert_called_once_with("Simple test query", None, None)
    
    @patch('routes.agent_api.run_agent')
    def test_agent_query_with_session_id_only(self, mock_run_agent, client: TestClient):
        """Test agent query with session ID but no model."""
        mock_run_agent.return_value = ("Session response", "existing_session")
        
        query_data = {
            "query": "Continue our conversation",
            "session_id": "existing_session"
        }
        
        response = client.post("/agent/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["response"] == "Session response"
        assert data["session_id"] == "existing_session"
        
        mock_run_agent.assert_called_once_with(
            "Continue our conversation", 
            "existing_session", 
            None
        )
    
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
    
    @patch('routes.agent_api.run_agent')
    def test_agent_query_exception_handling(self, mock_run_agent, client: TestClient):
        """Test agent query error handling."""
        # Mock an exception in run_agent
        mock_run_agent.side_effect = Exception("Agent processing failed")
        
        query_data = {"query": "Test query that will fail"}
        
        response = client.post("/agent/query", json=query_data)
        
        assert response.status_code == 500
        assert "Agent processing failed" in response.json()["detail"]
    
    @patch('routes.agent_api.run_agent')
    def test_agent_query_long_query(self, mock_run_agent, client: TestClient):
        """Test agent query with a long query string."""
        mock_run_agent.return_value = ("Long response", "long_session")
        
        long_query = "This is a very long query " * 100  # Create a long query
        query_data = {"query": long_query}
        
        response = client.post("/agent/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["response"] == "Long response"
        assert data["session_id"] == "long_session"
        
        mock_run_agent.assert_called_once_with(long_query, None, None)
    
    @patch('routes.agent_api.run_agent')
    def test_agent_query_special_characters(self, mock_run_agent, client: TestClient):
        """Test agent query with special characters."""
        mock_run_agent.return_value = ("Special char response", "special_session")
        
        special_query = "Query with special chars: !@#$%^&*()_+ 中文 émojis 🤖"
        query_data = {"query": special_query}
        
        response = client.post("/agent/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["response"] == "Special char response"
        mock_run_agent.assert_called_once_with(special_query, None, None)


class TestAgentIntegration:
    """Integration tests for agent functionality."""
    
    @patch('routes.agent_api.run_agent')
    def test_agent_conversation_flow(self, mock_run_agent, client: TestClient):
        """Test a conversation flow with multiple agent queries."""
        # Simulate a conversation with multiple turns
        conversations = [
            ("Hello, how are you?", "Hello! I'm doing well, thanks for asking.", "conv_001"),
            ("Can you help me with Python?", "Of course! I'd be happy to help with Python.", "conv_001"),
            ("What is a list in Python?", "A list in Python is a ordered collection of items.", "conv_001")
        ]
        
        session_id = None
        
        for query, expected_response, expected_session in conversations:
            mock_run_agent.return_value = (expected_response, expected_session)
            
            query_data = {"query": query}
            if session_id:
                query_data["session_id"] = session_id
            
            response = client.post("/agent/query", json=query_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["response"] == expected_response
            assert data["session_id"] == expected_session
            
            # Use the returned session_id for the next query
            session_id = data["session_id"]
    
    @patch('routes.agent_api.run_agent')
    def test_agent_model_switching(self, mock_run_agent, client: TestClient):
        """Test switching between different models."""
        models_to_test = ["gpt-4", "gpt-3.5-turbo", "claude-3"]
        
        for i, model in enumerate(models_to_test):
            mock_run_agent.return_value = (f"Response from {model}", f"session_{i}")
            
            query_data = {
                "query": f"Test query for {model}",
                "model": model
            }
            
            response = client.post("/agent/query", json=query_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["response"] == f"Response from {model}"
            assert data["session_id"] == f"session_{i}"
            
            # Verify the model parameter was passed correctly
            mock_run_agent.assert_called_with(f"Test query for {model}", None, model)
    
    @patch('routes.agent_api.run_agent')
    def test_agent_concurrent_sessions(self, mock_run_agent, client: TestClient):
        """Test handling multiple concurrent sessions."""
        sessions = ["session_a", "session_b", "session_c"]
        
        for session in sessions:
            mock_run_agent.return_value = (f"Response for {session}", session)
            
            query_data = {
                "query": f"Query for {session}",
                "session_id": session
            }
            
            response = client.post("/agent/query", json=query_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["response"] == f"Response for {session}"
            assert data["session_id"] == session
            
            mock_run_agent.assert_called_with(f"Query for {session}", session, None)
