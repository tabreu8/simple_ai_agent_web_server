"""
Tests for LLM-enhanced document parsing functionality.
"""

import pytest
import os
import tempfile
from knowledge_base.doc_parsing import DocumentParser


class TestLLMDocumentParsing:
    """Test LLM-enhanced document parsing features."""

    def test_standard_parser_initialization(self):
        """Test that standard parser initializes correctly."""
        parser = DocumentParser(use_llm=False)
        assert parser.use_llm is False
        assert parser.md_converter is not None

    def test_llm_parser_initialization_without_api_key(self):
        """Test LLM parser falls back to standard mode without API key."""
        parser = DocumentParser(use_llm=True, openai_api_key=None)
        assert parser.use_llm is True
        assert parser.md_converter is not None

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_llm_parser_initialization_with_api_key(self):
        """Test LLM parser initializes correctly with API key."""
        api_key = os.getenv("OPENAI_API_KEY")
        parser = DocumentParser(
            use_llm=True, 
            llm_model="gpt-4.1-mini",  # Use smaller model for testing
            openai_api_key=api_key
        )
        assert parser.use_llm is True
        assert parser.llm_model == "gpt-4.1-mini"
        assert parser.md_converter is not None

    def test_environment_based_parser_creation(self):
        """Test parser creation from environment variables."""
        # Test with environment variable fallbacks
        from knowledge_base.doc_parsing import get_document_parser
        
        # This should work regardless of env vars since it falls back to standard mode
        parser = get_document_parser()
        assert parser is not None

    def test_simple_text_parsing(self):
        """Test basic text parsing functionality."""
        parser = DocumentParser(use_llm=False)
        
        # Create simple text content
        text_content = b"# Test Document\n\nThis is a test document with some content.\n\n## Section 1\n\nMore content here."
        
        chunks = parser.parse_file_content(text_content, "test.md")
        
        assert len(chunks) > 0
        assert isinstance(chunks[0], str)
        assert "Test Document" in chunks[0]

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_llm_enhanced_parsing(self):
        """Test LLM-enhanced parsing with real API (if available)."""
        api_key = os.getenv("OPENAI_API_KEY")
        
        parser = DocumentParser(
            use_llm=True,
            llm_model="gpt-4.1-mini",  # Use smaller model for testing
            openai_api_key=api_key
        )
        
        # Test with simple text (should work regardless of LLM)
        text_content = b"# Test Document\n\nThis is a test document."
        chunks = parser.parse_file_content(text_content, "test.md")
        
        assert len(chunks) > 0
        assert isinstance(chunks[0], str)

    def test_parser_configuration_precedence(self):
        """Test that explicit parameters override environment variables."""
        # Set environment variable
        original_env = os.environ.get("MARKITDOWN_USE_LLM")
        os.environ["MARKITDOWN_USE_LLM"] = "true"
        
        try:
            # Explicit False should override env var True
            parser = DocumentParser(use_llm=False)
            assert parser.use_llm is False
            
            # Explicit True should work
            parser = DocumentParser(use_llm=True)
            assert parser.use_llm is True
            
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["MARKITDOWN_USE_LLM"] = original_env
            else:
                os.environ.pop("MARKITDOWN_USE_LLM", None)

    def test_supported_file_types_consistency(self):
        """Test that supported file types remain consistent between parser modes."""
        standard_parser = DocumentParser(use_llm=False)
        llm_parser = DocumentParser(use_llm=True, openai_api_key="dummy")
        
        # Both should support the same file types
        standard_extensions = standard_parser.get_supported_extensions()
        llm_extensions = llm_parser.get_supported_extensions()
        
        assert standard_extensions == llm_extensions
        assert '.pdf' in standard_extensions
        assert '.docx' in standard_extensions
        assert '.txt' in standard_extensions

    def test_chunk_splitting_consistency(self):
        """Test that chunk splitting works consistently in both modes."""
        # Create a longer text to test chunking
        long_text = "# Document Title\n\n" + "This is a paragraph. " * 100
        text_content = long_text.encode('utf-8')
        
        standard_parser = DocumentParser(use_llm=False)
        standard_chunks = standard_parser.parse_file_content(text_content, "test.md")
        
        llm_parser = DocumentParser(use_llm=True, openai_api_key="dummy")
        llm_chunks = llm_parser.parse_file_content(text_content, "test.md")
        
        # Both should produce multiple chunks for long content
        assert len(standard_chunks) > 1
        assert len(llm_chunks) > 1
        
        # Chunks should be reasonably sized
        for chunk in standard_chunks:
            assert len(chunk) <= 1200  # chunk_size + some tolerance
        
        for chunk in llm_chunks:
            assert len(chunk) <= 1200

    def test_error_handling_consistency(self):
        """Test that error handling works in both parser modes."""
        standard_parser = DocumentParser(use_llm=False)
        llm_parser = DocumentParser(use_llm=True, openai_api_key="dummy")
        
        # Test with empty content
        empty_chunks_standard = standard_parser.parse_file_content(b"", "empty.txt")
        empty_chunks_llm = llm_parser.parse_file_content(b"", "empty.txt")
        
        # Both should handle empty content gracefully
        assert isinstance(empty_chunks_standard, list)
        assert isinstance(empty_chunks_llm, list)
