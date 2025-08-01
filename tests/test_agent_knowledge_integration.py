"""
Test suite for agent knowledge base integration.
Tests specifically focus on how the agent uses the knowledge base search tool.
"""
import pytest
import json
from fastapi.testclient import TestClient


class TestAgentKnowledgeBaseIntegration:
    """Test cases specifically for agent's knowledge base tool integration."""
    
    def test_agent_references_specific_knowledge(self, client: TestClient, openai_api_key):
        """Test that agent references knowledge base when specific information is available."""
        # Insert specific technical information that's unlikely to be in general training
        documents_data = [
            {
                "content": "The XYZ-3000 industrial controller requires initialization with these exact parameters: voltage=12.7V, frequency=47.5Hz, calibration_code=A7B9X2. Safety protocol mandates checking thermal sensors before activation.",
                "metadata": {
                    "filename": "xyz3000_technical_manual.pdf",
                    "device": "XYZ-3000",
                    "type": "technical_specification"
                }
            }
        ]
        
        # Insert the document using the correct format
        documents_json = json.dumps(documents_data)
        insert_response = client.post("/docs/insert", data={"documents": documents_json})
        assert insert_response.status_code == 200
        
        # Ask about the specific device configuration
        query_data = {
            "query": "What are the initialization parameters for the XYZ-3000 controller?",
            "model": "gpt-4.1-mini"
        }
        
        response = client.post("/agent/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        response_text = data["response"].lower()
        
        # Agent should have found and referenced the specific technical details
        assert "12.7v" in response_text or "12.7 v" in response_text
        assert "47.5hz" in response_text or "47.5 hz" in response_text
        assert "a7b9x2" in response_text
        assert "thermal sensor" in response_text or "thermal" in response_text
        
    def test_agent_searches_internal_company_data(self, client: TestClient, openai_api_key):
        """Test that agent searches knowledge base for company-specific information."""
        # Insert company-specific policy information
        documents_data = [
                {
                    "content": "ACME Corp quarterly budget allocation for Department Z-42: Q1=$127,500, Q2=$145,200, Q3=$189,750, Q4=$156,300. Emergency fund reserve: $45,000. Department head: Dr. Marina Chen.",
                    "metadata": {
                        "filename": "dept_z42_budget_2024.xlsx",
                        "department": "Z-42",
                        "year": "2024",
                        "confidential": True
                    }
                }
            ]
        
        # Insert the document
        documents_json = json.dumps(documents_data)
        insert_response = client.post("/docs/insert", data={"documents": documents_json})
        assert insert_response.status_code == 200
        
        # Ask about specific internal budget information
        query_data = {
            "query": "What is the Q3 budget allocation for Department Z-42?",
            "model": "gpt-4.1-mini"
        }
        
        response = client.post("/agent/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        response_text = data["response"].lower()
        
        # Should contain the specific Q3 budget figure
        assert "189,750" in response_text or "$189,750" in response_text or "189750" in response_text
        
    def test_agent_handles_no_relevant_knowledge(self, client: TestClient, openai_api_key):
        """Test agent behavior when knowledge base has no relevant information."""
        # Insert documents about completely unrelated topics
        documents_data = [
                {
                    "content": "Baking chocolate chip cookies requires flour, sugar, eggs, and chocolate chips. Preheat oven to 375°F and bake for 12 minutes.",
                    "metadata": {
                        "filename": "cookie_recipe.txt",
                        "category": "cooking"
                    }
                }
            ]
        
        # Insert the unrelated document
        documents_json = json.dumps(documents_data)
        insert_response = client.post("/docs/insert", data={"documents": documents_json})
        assert insert_response.status_code == 200
        
        # Ask about something completely different that won't be in the knowledge base
        query_data = {
            "query": "What are the maintenance procedures for the Quantum Flux Capacitor Model QFC-2024?",
            "model": "gpt-4.1-mini"
        }
        
        response = client.post("/agent/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        response_text = data["response"].lower()
        
        # Agent should indicate it doesn't have specific information about this made-up device
        no_info_indicators = [
            "don't have specific information",
            "no specific information",
            "unable to find",
            "don't have access",
            "no information available",
            "cannot find",
            "no documents found",
            "no relevant information",
            "not available in"
        ]
        
        found_indicator = any(indicator in response_text for indicator in no_info_indicators)
        # Also shouldn't mention the cookie recipe as it's completely unrelated
        assert found_indicator or "cookie" not in response_text
        
    def test_agent_prioritizes_knowledge_over_general_info(self, client: TestClient, openai_api_key):
        """Test that agent prioritizes specific knowledge base information over general knowledge."""
        # Insert specific company information that contradicts general knowledge
        documents_data = [
                {
                    "content": "At TechCorp, our Python style guide mandates 2-space indentation (not the standard 4 spaces). All functions must use snake_case_with_tech prefix. Example: tech_calculate_profit(). This is company policy #TC-001.",
                    "metadata": {
                        "filename": "techcorp_python_style_guide.pdf",
                        "policy": "TC-001",
                        "override": True
                    }
                }
            ]
        
        # Insert the document
        documents_json = json.dumps(documents_data)
        insert_response = client.post("/docs/insert", data={"documents": documents_json})
        assert insert_response.status_code == 200
        
        # Ask about Python style guide
        query_data = {
            "query": "What is the Python indentation standard at TechCorp?",
            "model": "gpt-4.1-mini"
        }
        
        response = client.post("/agent/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        response_text = data["response"].lower()
        
        # Should mention the company-specific 2-space rule, not the general 4-space standard
        assert "2 space" in response_text or "2-space" in response_text
        assert "techcorp" in response_text or "tech corp" in response_text
        
    def test_agent_maintains_knowledge_context_across_session(self, client: TestClient, openai_api_key):
        """Test that agent can reference knowledge base across multiple queries in same session."""
        # Insert project information
        documents_data = [
                {
                    "content": "Project Nebula specifications: Launch date March 15, 2025. Team lead: Dr. Alexandra Reyes. Budget: $2.8M. Key components: Quantum processor (vendor: QuantumTech), Neural interface (vendor: BrainLink Corp), Power core (vendor: FusionDyne). Status: In development phase 2 of 4.",
                    "metadata": {
                        "filename": "project_nebula_specs.docx",
                        "project": "Nebula",
                        "classification": "internal"
                    }
                }
            ]
        
        # Insert the document
        documents_json = json.dumps(documents_data)
        insert_response = client.post("/docs/insert", data={"documents": documents_json})
        assert insert_response.status_code == 200
        
        # First question about the project
        session_id = "kb_integration_test_001"
        query_data = {
            "query": "Tell me about Project Nebula",
            "session_id": session_id,
            "model": "gpt-4.1-mini"
        }
        
        response1 = client.post("/agent/query", json=query_data)
        assert response1.status_code == 200
        data1 = response1.json()
        
        response1_text = data1["response"].lower()
        # Should mention key project details
        assert "march 15" in response1_text or "march 15, 2025" in response1_text
        assert "alexandra reyes" in response1_text
        
        # Follow-up question about specific vendors
        query_data2 = {
            "query": "Who is the vendor for the quantum processor in this project?",
            "session_id": session_id,
            "model": "gpt-4.1-mini"
        }
        
        response2 = client.post("/agent/query", json=query_data2)
        assert response2.status_code == 200
        data2 = response2.json()
        
        response2_text = data2["response"].lower()
        # Should find the specific vendor information
        assert "quantumtech" in response2_text or "quantum tech" in response2_text
        
        # Third question about project phase
        query_data3 = {
            "query": "What development phase is the project currently in?",
            "session_id": session_id,
            "model": "gpt-4.1-mini"
        }
        
        response3 = client.post("/agent/query", json=query_data3)
        assert response3.status_code == 200
        data3 = response3.json()
        
        response3_text = data3["response"].lower()
        # Should reference the phase information
        assert "phase 2" in response3_text
        
    def test_agent_combines_multiple_knowledge_sources(self, client: TestClient, openai_api_key):
        """Test that agent can combine information from multiple documents in knowledge base."""
        # Insert related documents about the same topic
        documents_data = [
                {
                    "content": "Server cluster Alpha-7 specifications: 48 CPU cores, 256GB RAM, 10TB SSD storage. Primary function: Machine learning model training.",
                    "metadata": {
                        "filename": "alpha7_hardware_specs.txt",
                        "server": "Alpha-7",
                        "type": "hardware"
                    }
                },
                {
                    "content": "Server cluster Alpha-7 maintenance schedule: Weekly restart every Sunday 3AM. Monthly security patching first Tuesday. Quarterly hardware inspection. Contact: sysadmin@company.com",
                    "metadata": {
                        "filename": "alpha7_maintenance.txt",
                        "server": "Alpha-7",
                        "type": "maintenance"
                    }
                },
                {
                    "content": "Server cluster Alpha-7 usage policy: Reserved for ML training jobs only. Maximum job duration: 72 hours. Priority access for Research team. Booking required via internal portal.",
                    "metadata": {
                        "filename": "alpha7_usage_policy.txt",
                        "server": "Alpha-7",
                        "type": "policy"
                    }
                }
            ]
        
        # Insert all documents
        documents_json = json.dumps(documents_data)
        insert_response = client.post("/docs/insert", data={"documents": documents_json})
        assert insert_response.status_code == 200
        
        # Ask a question that requires combining information from multiple sources
        query_data = {
            "query": "Give me a comprehensive overview of server cluster Alpha-7, including its specs, maintenance, and usage policies.",
            "model": "gpt-4.1-mini"
        }
        
        response = client.post("/agent/query", json=query_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        response_text = data["response"].lower()
        
        # Should combine information from all three documents
        # Hardware specs
        assert "48" in response_text and ("cpu" in response_text or "cores" in response_text)
        assert "256" in response_text and "gb" in response_text
        assert "10" in response_text and "tb" in response_text
        
        # Maintenance schedule
        assert "sunday" in response_text and "3" in response_text  # Sunday 3AM
        assert "tuesday" in response_text  # Monthly patching
        
        # Usage policy
        assert "72" in response_text and "hour" in response_text
        assert "research" in response_text
