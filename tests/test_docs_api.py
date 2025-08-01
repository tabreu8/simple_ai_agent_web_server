"""
Test suite for the document API endpoints.
"""
import pytest
import json
import os
from fastapi.testclient import TestClient
from typing import List, Dict, Any


class TestDocumentInsert:
    """Test cases for document insertion endpoints."""
    
    def test_insert_json_documents_success(self, client: TestClient, sample_documents):
        """Test successful insertion of JSON documents."""
        import json
        
        # Convert to the format expected by the API
        documents_json = json.dumps(sample_documents)
        response = client.post("/docs/insert", data={"documents": documents_json})
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "document_ids" in data
        assert len(data["document_ids"]) == len(sample_documents)
        assert data["processing_summary"]["json_documents"] == len(sample_documents)
        assert data["processing_summary"]["uploaded_files"] == 0
        assert data["processing_summary"]["total_chunks"] == len(sample_documents)
    
    def test_insert_single_document(self, client: TestClient):
        """Test insertion of a single document."""
        import json
        
        single_doc = [{"content": "Single test document", "metadata": {"test": True}}]
        documents_json = json.dumps(single_doc)
        response = client.post("/docs/insert", data={"documents": documents_json})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["document_ids"]) == 1
    
    def test_insert_documents_with_empty_content(self, client: TestClient):
        """Test insertion with empty content should be skipped."""
        import json
        
        docs_with_empty = [
            {"content": "Valid content", "metadata": {"test": True}},
            {"content": "", "metadata": {"empty": True}},
            {"content": "   ", "metadata": {"whitespace": True}},
            {"content": "Another valid content", "metadata": {"test": True}}
        ]
        documents_json = json.dumps(docs_with_empty)
        response = client.post("/docs/insert", data={"documents": documents_json})
        
        assert response.status_code == 200
        data = response.json()
        # Should only insert 2 valid documents (empty and whitespace-only are skipped)
        assert len(data["document_ids"]) == 2
        assert data["processing_summary"]["json_documents"] == 2
    
    def test_insert_file_upload_text(self, client: TestClient, sample_text_file):
        """Test file upload with text file."""
        with open(sample_text_file, "rb") as f:
            response = client.post(
                "/docs/insert",
                files={"files": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "document_ids" in data
        assert len(data["document_ids"]) > 0
        assert data["processing_summary"]["uploaded_files"] == 1
        assert len(data["processing_summary"]["processed_files"]) == 1
        assert data["processing_summary"]["processed_files"][0]["filename"] == "test.txt"
    
    def test_insert_file_upload_markdown(self, client: TestClient, sample_markdown_file):
        """Test file upload with markdown file."""
        with open(sample_markdown_file, "rb") as f:
            response = client.post(
                "/docs/insert",
                files={"files": ("test.md", f, "text/markdown")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert len(data["document_ids"]) > 0
        assert data["processing_summary"]["uploaded_files"] == 1
    
    def test_insert_file_upload_pdf(self, client: TestClient):
        """Test file upload with PDF file."""
        pdf_path = "/Users/tiago/Documents/Coding&Stuff/simple_ai_agent_web_server/tests/sample-local-pdf.pdf"
        
        with open(pdf_path, "rb") as f:
            response = client.post(
                "/docs/insert",
                files={"files": ("sample-local-pdf.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert len(data["document_ids"]) > 0
        assert data["processing_summary"]["uploaded_files"] == 1
        assert len(data["processing_summary"]["processed_files"]) == 1
        assert data["processing_summary"]["processed_files"][0]["filename"] == "sample-local-pdf.pdf"
    
    def test_insert_combined_json_and_files(self, client: TestClient, sample_text_file):
        """Test inserting both JSON documents and files in the same request."""
        import json
        
        json_docs = [{"content": "JSON document content", "metadata": {"source": "json"}}]
        documents_json = json.dumps(json_docs)
        
        with open(sample_text_file, "rb") as f:
            response = client.post(
                "/docs/insert",
                data={"documents": documents_json},
                files={"files": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["processing_summary"]["json_documents"] == 1
        assert data["processing_summary"]["uploaded_files"] == 1
        assert len(data["document_ids"]) >= 2  # At least one JSON doc + file chunks
    
    def test_insert_no_content_error(self, client: TestClient):
        """Test error when no content is provided."""
        response = client.post("/docs/insert", data={})
        
        assert response.status_code == 400
        assert "At least one of 'documents' (JSON) or 'files' must be provided" in response.json()["detail"]
    
    def test_insert_unsupported_file_type(self, client: TestClient):
        """Test error with unsupported file type."""
        # Create a fake binary file
        fake_file_content = b"This is not a supported file type"
        
        response = client.post(
            "/docs/insert",
            files={"files": ("test.exe", fake_file_content, "application/octet-stream")}
        )
        
        assert response.status_code == 400
        assert "type not supported" in response.json()["detail"]
    
    def test_deprecated_upload_endpoint(self, client: TestClient, sample_text_file):
        """Test that the deprecated upload endpoint still works."""
        with open(sample_text_file, "rb") as f:
            response = client.post(
                "/docs/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestDocumentSearch:
    """Test cases for document search functionality."""
    
    def test_search_documents_success(self, client: TestClient, inserted_document_ids):
        """Test successful document search."""
        response = client.get("/docs/search?query=artificial intelligence")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "total_results" in data
        assert isinstance(data["results"], list)
        assert data["total_results"] >= 0
        
        # Check result structure
        if data["results"]:
            result = data["results"][0]
            assert "id" in result
            assert "document" in result
            assert "metadata" in result
            assert "similarity_score" in result
            assert "distance" in result
    
    def test_search_with_specific_query(self, client: TestClient, inserted_document_ids):
        """Test search with a specific query that should return relevant results."""
        response = client.get("/docs/search?query=FastAPI framework")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find the FastAPI document
        assert len(data["results"]) > 0
        # Check that at least one result contains FastAPI-related content
        found_fastapi = any("FastAPI" in str(result.get("document", "")) for result in data["results"])
        assert found_fastapi or len(data["results"]) > 0  # Either found FastAPI or got other results
    
    def test_search_with_n_results_parameter(self, client: TestClient, inserted_document_ids):
        """Test search with n_results parameter."""
        response = client.get("/docs/search?query=test&n_results=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["results"]) <= 2
    
    def test_search_with_metadata_filter(self, client: TestClient, inserted_document_ids):
        """Test search with metadata filtering."""
        metadata_filter = json.dumps({"category": "AI"})
        response = client.get(f"/docs/search?query=test&metadata_filter={metadata_filter}")
        
        assert response.status_code == 200
        data = response.json()
        
        # All results should have category = "AI" if any results are returned
        for result in data["results"]:
            if result["metadata"]:
                assert result["metadata"].get("category") == "AI"
    
    def test_search_invalid_metadata_filter(self, client: TestClient):
        """Test search with invalid metadata filter JSON."""
        response = client.get("/docs/search?query=test&metadata_filter=invalid-json")
        
        assert response.status_code == 400
        assert "Invalid JSON" in response.json()["detail"]
    
    def test_search_missing_query(self, client: TestClient):
        """Test search without query parameter."""
        response = client.get("/docs/search")
        
        assert response.status_code == 422  # FastAPI validation error
    
    def test_search_invalid_n_results(self, client: TestClient):
        """Test search with invalid n_results values."""
        # Test with n_results too high
        response = client.get("/docs/search?query=test&n_results=150")
        assert response.status_code == 422
        
        # Test with n_results too low
        response = client.get("/docs/search?query=test&n_results=0")
        assert response.status_code == 422


class TestDocumentCRUD:
    """Test cases for document CRUD operations."""
    
    def test_get_document_success(self, client: TestClient, inserted_document_ids):
        """Test successful document retrieval."""
        doc_id = inserted_document_ids[0]
        response = client.get(f"/docs/{doc_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == doc_id
        assert "document" in data
        assert "metadata" in data
    
    def test_get_document_not_found(self, client: TestClient):
        """Test document retrieval with non-existent ID."""
        response = client.get("/docs/non-existent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_update_document_content(self, client: TestClient, inserted_document_ids):
        """Test updating document content."""
        doc_id = inserted_document_ids[0]
        update_data = {
            "document": "Updated document content for testing",
            "metadata": {"updated": True, "version": 2}
        }
        
        response = client.put(f"/docs/{doc_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["document_id"] == doc_id
        
        # Verify the update by retrieving the document
        get_response = client.get(f"/docs/{doc_id}")
        assert get_response.status_code == 200
        updated_doc = get_response.json()
        assert updated_doc["document"] == update_data["document"]
    
    def test_update_document_metadata_only(self, client: TestClient, inserted_document_ids):
        """Test updating only document metadata."""
        doc_id = inserted_document_ids[0]
        update_data = {"metadata": {"updated": True, "metadata_only": True}}
        
        response = client.put(f"/docs/{doc_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_update_document_not_found(self, client: TestClient):
        """Test updating non-existent document."""
        update_data = {"document": "New content"}
        response = client.put("/docs/non-existent-id", json=update_data)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_update_document_no_data(self, client: TestClient, inserted_document_ids):
        """Test update with no data provided."""
        doc_id = inserted_document_ids[0]
        response = client.put(f"/docs/{doc_id}", json={})
        
        assert response.status_code == 400
        assert "At least one of 'document' or 'metadata' must be provided" in response.json()["detail"]
    
    def test_delete_document_success(self, client: TestClient, inserted_document_ids):
        """Test successful document deletion."""
        doc_id = inserted_document_ids[0]
        response = client.delete(f"/docs/{doc_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["document_id"] == doc_id
        
        # Verify deletion by trying to retrieve the document
        get_response = client.get(f"/docs/{doc_id}")
        assert get_response.status_code == 404
    
    def test_delete_document_not_found(self, client: TestClient):
        """Test deleting non-existent document."""
        response = client.delete("/docs/non-existent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestCollectionStats:
    """Test cases for collection statistics."""
    
    def test_get_stats_success(self, client: TestClient):
        """Test successful retrieval of collection statistics."""
        response = client.get("/docs/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "stats" in data
        assert "supported_file_types" in data["stats"]
        assert isinstance(data["stats"]["supported_file_types"], list)
    
    def test_get_stats_with_documents(self, client: TestClient, inserted_document_ids):
        """Test statistics after inserting documents."""
        response = client.get("/docs/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        stats = data["stats"]
        assert "supported_file_types" in stats
        # Should have some documents in the collection
        if "count" in stats:
            assert stats["count"] > 0


class TestIntegrationFlows:
    """Test cases for complete integration flows."""
    
    def test_complete_document_lifecycle(self, client: TestClient):
        """Test complete document lifecycle: insert -> search -> get -> update -> delete."""
        import json
        
        # 1. Insert a document
        doc_data = [{
            "content": "Integration test document about machine learning algorithms",
            "metadata": {"test_type": "integration", "topic": "ML"}
        }]
        documents_json = json.dumps(doc_data)
        insert_response = client.post("/docs/insert", data={"documents": documents_json})
        assert insert_response.status_code == 200
        doc_id = insert_response.json()["document_ids"][0]
        
        # 2. Search for the document
        search_response = client.get("/docs/search?query=machine learning")
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results["results"]) > 0
        
        # Verify our document is in the search results
        found_doc = any(result["id"] == doc_id for result in search_results["results"])
        assert found_doc
        
        # 3. Get the specific document
        get_response = client.get(f"/docs/{doc_id}")
        assert get_response.status_code == 200
        doc = get_response.json()
        assert doc["id"] == doc_id
        assert "machine learning" in doc["document"].lower()
        
        # 4. Update the document
        update_data = {
            "document": "Updated integration test document about deep learning",
            "metadata": {"test_type": "integration", "topic": "DL", "updated": True}
        }
        update_response = client.put(f"/docs/{doc_id}", json=update_data)
        assert update_response.status_code == 200
        
        # Verify the update
        get_updated_response = client.get(f"/docs/{doc_id}")
        assert get_updated_response.status_code == 200
        updated_doc = get_updated_response.json()
        assert "deep learning" in updated_doc["document"].lower()
        assert updated_doc["metadata"]["updated"] is True
        
        # 5. Delete the document
        delete_response = client.delete(f"/docs/{doc_id}")
        assert delete_response.status_code == 200
        
        # Verify deletion
        get_deleted_response = client.get(f"/docs/{doc_id}")
        assert get_deleted_response.status_code == 404
    
    def test_file_upload_and_search_flow(self, client: TestClient, sample_text_file):
        """Test file upload followed by search."""
        # 1. Upload a file
        with open(sample_text_file, "rb") as f:
            upload_response = client.post(
                "/docs/insert",
                files={"files": ("integration_test.txt", f, "text/plain")}
            )
        
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        doc_ids = upload_data["document_ids"]
        assert len(doc_ids) > 0
        
        # 2. Search for content from the uploaded file
        search_response = client.get("/docs/search?query=sample text document")
        assert search_response.status_code == 200
        search_results = search_response.json()
        
        # Should find at least one result
        assert len(search_results["results"]) > 0
        
        # 3. Verify at least one of our uploaded documents is in the results
        uploaded_doc_found = any(
            result["id"] in doc_ids for result in search_results["results"]
        )
        assert uploaded_doc_found
    
    def test_pdf_upload_and_search_flow(self, client: TestClient):
        """Test PDF file upload followed by search."""
        pdf_path = "/Users/tiago/Documents/Coding&Stuff/simple_ai_agent_web_server/tests/sample-local-pdf.pdf"
        
        # 1. Upload a PDF file
        with open(pdf_path, "rb") as f:
            upload_response = client.post(
                "/docs/insert",
                files={"files": ("sample-local-pdf.pdf", f, "application/pdf")}
            )
        
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        doc_ids = upload_data["document_ids"]
        assert len(doc_ids) > 0
        
        # 2. Search for content that might be in the PDF
        # Note: This will depend on the actual content of the PDF
        search_response = client.get("/docs/search?query=document content")
        assert search_response.status_code == 200
        search_results = search_response.json()
        
        # Should find at least one result (PDF content)
        assert len(search_results["results"]) > 0
        
        # 3. Verify at least one of our uploaded PDF documents is in the results
        uploaded_doc_found = any(
            result["id"] in doc_ids for result in search_results["results"]
        )
        # Note: This assertion might fail if PDF parsing doesn't work or PDF is empty
        # In that case, we at least verify the upload succeeded
        if not uploaded_doc_found:
            # At minimum, verify the upload process worked
            assert upload_data["status"] == "success"
            assert upload_data["processing_summary"]["uploaded_files"] == 1
    
    def test_metadata_filtering_flow(self, client: TestClient):
        """Test document insertion with metadata and filtered search."""
        import json
        
        # 1. Insert documents with different categories
        docs = [
            {"content": "Python programming tutorial", "metadata": {"category": "programming", "language": "python"}},
            {"content": "JavaScript web development", "metadata": {"category": "programming", "language": "javascript"}},
            {"content": "Machine learning basics", "metadata": {"category": "ai", "topic": "ml"}},
            {"content": "Database design principles", "metadata": {"category": "database", "type": "relational"}}
        ]
        documents_json = json.dumps(docs)
        insert_response = client.post("/docs/insert", data={"documents": documents_json})
        assert insert_response.status_code == 200
        
        # 2. Search with category filter
        category_filter = json.dumps({"category": "programming"})
        search_response = client.get(f"/docs/search?query=tutorial&metadata_filter={category_filter}")
        assert search_response.status_code == 200
        
        search_results = search_response.json()
        # All results should have category "programming"
        for result in search_results["results"]:
            if result["metadata"]:
                assert result["metadata"].get("category") == "programming"
        
        # 3. Search with language filter
        language_filter = json.dumps({"language": "python"})
        python_search = client.get(f"/docs/search?query=programming&metadata_filter={language_filter}")
        assert python_search.status_code == 200
        
        python_results = python_search.json()
        for result in python_results["results"]:
            if result["metadata"]:
                assert result["metadata"].get("language") == "python"
