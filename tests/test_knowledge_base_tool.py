"""
Test suite for the knowledge base search tool.
"""
import pytest
import asyncio
from knowledge_base.chromadb import search_knowledge_base, get_chromadb_manager


class TestKnowledgeBaseSearchTool:
    """Test cases for the knowledge base search tool function."""
    
    def test_search_tool_with_no_documents(self):
        """Test search tool when no documents exist."""
        # Clear any existing documents
        manager = get_chromadb_manager()
        
        # Run the search tool
        result = asyncio.run(search_knowledge_base("Python programming"))
        
        assert isinstance(result, str)
        assert "No documents found" in result
        assert "Python programming" in result
    
    def test_search_tool_with_documents(self):
        """Test search tool with existing documents."""
        # Insert test documents
        manager = get_chromadb_manager()
        
        documents = [
            "Python is a high-level programming language known for its simplicity.",
            "FastAPI is a modern web framework for building APIs with Python.",
            "Machine learning algorithms can be implemented efficiently in Python."
        ]
        
        metadatas = [
            {"filename": "python_intro.txt", "topic": "programming"},
            {"filename": "fastapi_guide.txt", "topic": "web_development"},
            {"filename": "ml_guide.txt", "topic": "machine_learning"}
        ]
        
        doc_ids = manager.insert_documents(documents, metadatas)
        assert len(doc_ids) == 3
        
        # Test searching for Python-related content
        result = asyncio.run(search_knowledge_base("Python programming"))
        
        assert isinstance(result, str)
        assert "Search Results for" in result
        assert "Python" in result
        assert "Found" in result
        assert "relevant document" in result
        
        # Should contain document content
        assert "high-level programming language" in result or "web framework" in result
        
        # Should contain metadata
        assert "Source:" in result
        
        # Clean up
        for doc_id in doc_ids:
            manager.delete_document(doc_id)
    
    def test_search_tool_max_results_parameter(self):
        """Test search tool with max_results parameter."""
        manager = get_chromadb_manager()
        
        # Insert multiple documents
        documents = [
            f"Document {i} about Python programming and development." 
            for i in range(10)
        ]
        
        metadatas = [
            {"filename": f"doc_{i}.txt", "topic": "programming"} 
            for i in range(10)
        ]
        
        doc_ids = manager.insert_documents(documents, metadatas)
        assert len(doc_ids) == 10
        
        # Test with max_results=3
        result = asyncio.run(search_knowledge_base("Python", max_results=3))
        
        assert isinstance(result, str)
        assert "Found 3 relevant document" in result
        
        # Count the number of "--- Result" markers
        result_markers = result.count("--- Result")
        assert result_markers == 3
        
        # Clean up
        for doc_id in doc_ids:
            manager.delete_document(doc_id)
    
    def test_search_tool_max_results_bounds(self):
        """Test search tool max_results parameter bounds."""
        manager = get_chromadb_manager()
        
        # Insert a test document
        documents = ["Test document about Python programming."]
        metadatas = [{"filename": "test.txt", "topic": "programming"}]
        
        doc_ids = manager.insert_documents(documents, metadatas)
        
        # Test with max_results too low (should be clamped to 1)
        result = asyncio.run(search_knowledge_base("Python", max_results=0))
        assert "Found 1 relevant document" in result
        
        # Test with max_results too high (should be clamped to 20)
        result = asyncio.run(search_knowledge_base("Python", max_results=100))
        assert "Found 1 relevant document" in result  # Only 1 document exists
        
        # Clean up
        for doc_id in doc_ids:
            manager.delete_document(doc_id)
    
    def test_search_tool_content_truncation(self):
        """Test search tool truncates long content."""
        manager = get_chromadb_manager()
        
        # Insert document with very long content
        long_content = "Python programming. " * 100  # Long repeated content
        documents = [long_content]
        metadatas = [{"filename": "long_doc.txt", "topic": "programming"}]
        
        doc_ids = manager.insert_documents(documents, metadatas)
        
        # Search for the document
        result = asyncio.run(search_knowledge_base("Python"))
        
        assert isinstance(result, str)
        assert "Python programming" in result
        
        # Should truncate long content (check for "...")
        if len(long_content) > 1000:
            assert "..." in result
        
        # Clean up
        for doc_id in doc_ids:
            manager.delete_document(doc_id)
    
    def test_search_tool_metadata_display(self):
        """Test search tool displays metadata correctly."""
        manager = get_chromadb_manager()
        
        # Insert document with rich metadata
        documents = ["Python is a versatile programming language."]
        metadatas = [{
            "filename": "python_guide.pdf",
            "created_at": "2024-01-01T12:00:00",
            "page_number": 5,
            "author": "John Doe",
            "topic": "programming"
        }]
        
        doc_ids = manager.insert_documents(documents, metadatas)
        
        # Search for the document
        result = asyncio.run(search_knowledge_base("Python"))
        
        assert isinstance(result, str)
        
        # Check that relevant metadata is displayed
        assert "Source: python_guide.pdf" in result
        assert "Created: 2024-01-01T12:00:00" in result
        assert "Page: 5" in result
        
        # Clean up
        for doc_id in doc_ids:
            manager.delete_document(doc_id)
    
    def test_search_tool_relevance_score(self):
        """Test search tool shows relevance scores."""
        manager = get_chromadb_manager()
        
        # Insert documents with varying relevance
        documents = [
            "Python is the best programming language for beginners.",
            "Java is also a popular programming language.",
            "Web development can be done with many languages."
        ]
        
        metadatas = [
            {"filename": "python.txt", "topic": "python"},
            {"filename": "java.txt", "topic": "java"},
            {"filename": "web.txt", "topic": "web"}
        ]
        
        doc_ids = manager.insert_documents(documents, metadatas)
        
        # Search specifically for Python
        result = asyncio.run(search_knowledge_base("Python programming"))
        
        assert isinstance(result, str)
        
        # Should show relevance scores
        assert "Relevance Score:" in result
        
        # Clean up
        for doc_id in doc_ids:
            manager.delete_document(doc_id)


class TestKnowledgeBaseToolIntegration:
    """Integration tests for knowledge base search tool with agent processing."""
    
    def test_tool_with_agent_processing(self):
        """Test the search tool works in agent context (basic functionality test)."""
        # This is a basic test to ensure the tool can be called
        # More comprehensive agent integration is tested in test_agent_api.py
        
        result = asyncio.run(search_knowledge_base("test query"))
        
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Should handle empty knowledge base gracefully
        assert "No documents found" in result or "Error" in result
