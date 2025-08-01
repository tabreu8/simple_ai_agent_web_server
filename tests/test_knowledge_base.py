"""
Test suite for the knowledge base functionality (ChromaDB and document parsing).
"""

from unittest.mock import MagicMock, patch

from knowledge_base.chromadb import get_chromadb_manager
from knowledge_base.doc_parsing import get_document_parser


class TestChromaDBManager:
    """Test cases for ChromaDB manager functionality."""

    def test_chromadb_manager_singleton(self):
        """Test that ChromaDB manager is a singleton."""
        manager1 = get_chromadb_manager()
        manager2 = get_chromadb_manager()

        assert manager1 is manager2

    def test_insert_and_query_documents(self):
        """Test document insertion and querying."""
        manager = get_chromadb_manager()

        # Insert test documents
        documents = [
            "This is a test document about artificial intelligence.",
            "FastAPI is a modern web framework for Python.",
            "ChromaDB is a vector database for embeddings.",
        ]
        metadatas = [
            {"category": "AI", "test": True},
            {"category": "Programming", "test": True},
            {"category": "Database", "test": True},
        ]

        doc_ids = manager.insert_documents(documents, metadatas)

        assert len(doc_ids) == 3
        assert all(isinstance(doc_id, str) for doc_id in doc_ids)

        # Query the documents
        results = manager.query_documents("artificial intelligence", n_results=2)

        assert "ids" in results
        assert "documents" in results
        assert "metadatas" in results
        assert "distances" in results

        assert len(results["ids"]) <= 2
        assert len(results["documents"]) == len(results["ids"])
        assert len(results["metadatas"]) == len(results["ids"])
        assert len(results["distances"]) == len(results["ids"])

    def test_get_document(self):
        """Test retrieving a specific document by ID."""
        manager = get_chromadb_manager()

        # Insert a test document
        documents = ["Test document for retrieval"]
        metadatas = [{"test": "get_document"}]

        doc_ids = manager.insert_documents(documents, metadatas)
        doc_id = doc_ids[0]

        # Retrieve the document
        retrieved_doc = manager.get_document(doc_id)

        assert retrieved_doc is not None
        assert retrieved_doc["id"] == doc_id
        assert retrieved_doc["document"] == "Test document for retrieval"
        assert retrieved_doc["metadata"]["test"] == "get_document"

    def test_get_nonexistent_document(self):
        """Test retrieving a non-existent document."""
        manager = get_chromadb_manager()

        result = manager.get_document("non-existent-id")
        assert result is None

    def test_update_document(self):
        """Test updating a document."""
        manager = get_chromadb_manager()

        # Insert a test document
        documents = ["Original document content"]
        metadatas = [{"version": 1}]

        doc_ids = manager.insert_documents(documents, metadatas)
        doc_id = doc_ids[0]

        # Update the document
        new_content = "Updated document content"
        new_metadata = {"version": 2, "updated": True}

        success = manager.update_document(doc_id, new_content, new_metadata)
        assert success

        # Verify the update
        updated_doc = manager.get_document(doc_id)
        assert updated_doc is not None
        assert updated_doc["document"] == new_content
        assert updated_doc["metadata"]["version"] == 2
        assert updated_doc["metadata"]["updated"] is True

    def test_update_nonexistent_document(self):
        """Test updating a non-existent document."""
        manager = get_chromadb_manager()

        success = manager.update_document("non-existent-id", "New content")
        assert not success

    def test_delete_document(self):
        """Test deleting a document."""
        manager = get_chromadb_manager()

        # Insert a test document
        documents = ["Document to be deleted"]
        metadatas = [{"to_delete": True}]

        doc_ids = manager.insert_documents(documents, metadatas)
        doc_id = doc_ids[0]

        # Verify document exists
        assert manager.get_document(doc_id) is not None

        # Delete the document
        success = manager.delete_document(doc_id)
        assert success

        # Verify document is deleted
        assert manager.get_document(doc_id) is None

    def test_delete_nonexistent_document(self):
        """Test deleting a non-existent document."""
        manager = get_chromadb_manager()

        success = manager.delete_document("non-existent-id")
        assert not success

    def test_query_with_metadata_filter(self):
        """Test querying with metadata filtering."""
        manager = get_chromadb_manager()

        # Insert documents with different categories
        documents = [
            "Programming document about Python",
            "AI document about machine learning",
            "Programming document about JavaScript",
        ]
        metadatas = [
            {"category": "programming", "language": "python"},
            {"category": "ai", "topic": "ml"},
            {"category": "programming", "language": "javascript"},
        ]

        manager.insert_documents(documents, metadatas)

        # Query with metadata filter
        results = manager.query_documents(
            "programming", n_results=10, where={"category": "programming"}
        )

        # All results should have category "programming"
        for metadata in results["metadatas"]:
            assert metadata["category"] == "programming"

    def test_get_collection_stats(self):
        """Test getting collection statistics."""
        manager = get_chromadb_manager()

        # Insert some test documents
        documents = ["Doc 1", "Doc 2", "Doc 3"]
        metadatas = [{}, {}, {}]

        manager.insert_documents(documents, metadatas)

        stats = manager.get_collection_stats()

        assert isinstance(stats, dict)
        assert "document_count" in stats
        assert stats["document_count"] >= 3  # At least the 3 we just inserted


class TestDocumentParser:
    """Test cases for document parsing functionality."""

    def test_document_parser_singleton(self):
        """Test that document parser is a singleton."""
        parser1 = get_document_parser()
        parser2 = get_document_parser()

        assert parser1 is parser2

    def test_supported_file_extensions(self):
        """Test getting supported file extensions."""
        parser = get_document_parser()

        extensions = parser.get_supported_extensions()

        assert isinstance(extensions, list)
        assert len(extensions) > 0
        assert ".txt" in extensions or "txt" in extensions
        assert ".md" in extensions or "md" in extensions

    def test_is_supported_file(self):
        """Test checking if a file is supported."""
        parser = get_document_parser()

        # Test supported files
        assert parser.is_supported_file("test.txt")
        assert parser.is_supported_file("document.md")
        assert parser.is_supported_file("presentation.pptx")

        # Test unsupported files
        assert not parser.is_supported_file("test.exe")
        assert not parser.is_supported_file("document.bin")
        assert not parser.is_supported_file("file.markdown")
        assert not parser.is_supported_file("file.unknown")

        # Test edge cases
        assert not parser.is_supported_file("")
        assert not parser.is_supported_file("no_extension")

    def test_parse_text_file(self):
        """Test parsing a text file."""
        parser = get_document_parser()

        # Create a test text content
        text_content = """This is a test document.
It has multiple lines.
Each line contains different information.
This should be parsed correctly."""

        chunks = parser.parse_file_content(text_content.encode(), "test.txt")

        assert isinstance(chunks, list)
        assert len(chunks) > 0

        # Check that content is properly chunked
        full_content = " ".join(chunks)
        assert "test document" in full_content
        assert "multiple lines" in full_content

    def test_parse_markdown_file(self):
        """Test parsing a markdown file."""
        parser = get_document_parser()

        markdown_content = """# Test Document

This is a **markdown** document.

## Section 1
- Item 1
- Item 2

## Section 2
More content here.

### Subsection
Final content.
"""

        chunks = parser.parse_file_content(markdown_content.encode(), "test.md")

        assert isinstance(chunks, list)
        assert len(chunks) > 0

        # Check that markdown content is parsed
        full_content = " ".join(chunks)
        assert "Test Document" in full_content
        assert "**markdown**" in full_content  # Check for actual markdown syntax
        assert "Section 1" in full_content

    def test_parse_empty_file(self):
        """Test parsing an empty file."""
        parser = get_document_parser()

        chunks = parser.parse_file_content(b"", "empty.txt")

        # Should return empty list or minimal content
        assert isinstance(chunks, list)
        # Allow for either empty list or list with empty/minimal content
        assert len(chunks) == 0 or all(not chunk.strip() for chunk in chunks)

    def test_parse_large_file(self):
        """Test parsing a large file that should be chunked."""
        parser = get_document_parser()

        # Create a large text content
        large_content = "This is a sentence. " * 1000  # 1000 sentences

        chunks = parser.parse_file_content(large_content.encode(), "large.txt")

        assert isinstance(chunks, list)
        assert len(chunks) > 1  # Should be split into multiple chunks

        # Verify all chunks together contain the original content
        combined_content = " ".join(chunks)
        assert "This is a sentence" in combined_content

    @patch("knowledge_base.doc_parsing.MarkItDown")
    def test_parse_file_with_markitdown_error(self, mock_markitdown):
        """Test handling of MarkItDown parsing errors."""
        parser = get_document_parser()

        # Mock MarkItDown to raise an exception
        mock_instance = MagicMock()
        mock_instance.convert.side_effect = Exception("Parsing failed")
        mock_markitdown.return_value = mock_instance

        # This should fall back to treating the file as plain text
        content = b"Test content that fails to parse"
        chunks = parser.parse_file_content(content, "test.txt")

        # Should still return some content (fallback behavior)
        assert isinstance(chunks, list)

    def test_chunk_text_basic(self):
        """Test basic text chunking functionality."""
        parser = get_document_parser()

        # Test with a text that should be chunked
        long_text = "This is sentence one. " * 100
        chunks = parser._split_into_chunks(long_text, "test.txt")

        assert isinstance(chunks, list)
        assert len(chunks) >= 1

        # Each chunk should be a string
        for chunk in chunks:
            assert isinstance(chunk, str)
            assert len(chunk.strip()) > 0

    def test_chunk_text_short(self):
        """Test chunking of short text."""
        parser = get_document_parser()

        short_text = "This is a short text."
        chunks = parser._split_into_chunks(short_text, "test.txt")

        # Short text should typically be in one chunk
        assert isinstance(chunks, list)
        assert len(chunks) == 1
        assert chunks[0].strip() == short_text.strip()


class TestKnowledgeBaseIntegration:
    """Integration tests for knowledge base components."""

    def test_chromadb_document_parser_integration(self):
        """Test integration between ChromaDB and document parser."""
        manager = get_chromadb_manager()
        parser = get_document_parser()

        # Create a test document
        document_content = """# Integration Test

This is a test document for integration testing.

## Features
- Document parsing
- Vector storage
- Similarity search

The system should handle this document properly.
"""

        # Parse the document
        chunks = parser.parse_file_content(document_content.encode(), "integration.md")
        assert len(chunks) > 0

        # Insert into ChromaDB
        metadatas = [
            {"source": "integration_test", "chunk": i} for i in range(len(chunks))
        ]
        doc_ids = manager.insert_documents(chunks, metadatas)

        assert len(doc_ids) == len(chunks)

        # Search for the content
        results = manager.query_documents("integration testing", n_results=5)

        assert len(results["ids"]) > 0

        # Verify we can find our inserted content
        found_content = False
        for doc in results["documents"]:
            if "integration testing" in doc.lower():
                found_content = True
                break

        assert found_content

    def test_file_processing_workflow(self):
        """Test complete file processing workflow."""
        manager = get_chromadb_manager()
        parser = get_document_parser()

        # Simulate file upload workflow
        file_content = """FastAPI Testing Guide

This guide covers testing FastAPI applications.

## Unit Tests
Write unit tests for individual functions.

## Integration Tests
Test the complete API endpoints.

## Best Practices
- Use pytest for testing
- Mock external dependencies
- Test error conditions
"""

        filename = "testing_guide.md"

        # Step 1: Check if file is supported
        assert parser.is_supported_file(filename)

        # Step 2: Parse file content
        chunks = parser.parse_file_content(file_content.encode(), filename)
        assert len(chunks) > 0

        # Step 3: Prepare metadata
        base_metadata = {
            "source_filename": filename,
            "source_type": "uploaded_file",
            "file_size": len(file_content),
            "content_type": "text/markdown",
        }

        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({"chunk_index": i, "total_chunks": len(chunks)})
            metadatas.append(chunk_metadata)

        # Step 4: Insert into ChromaDB
        doc_ids = manager.insert_documents(chunks, metadatas)
        assert len(doc_ids) == len(chunks)

        # Step 5: Verify searchability
        search_results = manager.query_documents("FastAPI testing", n_results=3)
        assert len(search_results["ids"]) > 0

        # Step 6: Verify metadata filtering
        filtered_results = manager.query_documents(
            "testing", n_results=10, where={"source_filename": filename}
        )

        # All results should be from our file
        for metadata in filtered_results["metadatas"]:
            assert metadata["source_filename"] == filename
