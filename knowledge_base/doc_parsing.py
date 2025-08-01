import io
import logging
from typing import List, Dict, Any, BinaryIO
from markitdown import MarkItDown
import tempfile
import os

logger = logging.getLogger(__name__)


class DocumentParser:
    """Handles document parsing using MarkItDown library."""
    
    def __init__(self):
        """Initialize the MarkItDown parser."""
        self.md_converter = MarkItDown()
    
    def parse_file_content(self, file_content: bytes, filename: str) -> List[str]:
        """
        Parse file content and return chunks of text.
        
        Args:
            file_content: Binary content of the file
            filename: Name of the file (used for extension detection)
            
        Returns:
            List of text chunks extracted from the document
        """
        try:
            # Create a temporary file to work with MarkItDown
            with tempfile.NamedTemporaryFile(suffix=self._get_file_extension(filename), delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file.flush()
                
                try:
                    # Convert the file to markdown
                    result = self.md_converter.convert(temp_file.name)
                    markdown_text = result.text_content
                    
                    # Split into chunks
                    chunks = self._split_into_chunks(markdown_text, filename)
                    
                    logger.info(f"Successfully parsed {filename} into {len(chunks)} chunks")
                    return chunks
                    
                finally:
                    # Clean up temporary file
                    os.unlink(temp_file.name)
                    
        except Exception as e:
            logger.error(f"Error parsing file {filename}: {str(e)}")
            raise
    
    def parse_pdf(self, file_content: bytes, filename: str = "document.pdf") -> List[str]:
        """
        Parse PDF content and return chunks.
        
        Args:
            file_content: Binary PDF content
            filename: Optional filename for context
            
        Returns:
            List of text chunks extracted from the PDF
        """
        return self.parse_file_content(file_content, filename)
    
    def parse_docx(self, file_content: bytes, filename: str = "document.docx") -> List[str]:
        """
        Parse DOCX content and return chunks.
        
        Args:
            file_content: Binary DOCX content
            filename: Optional filename for context
            
        Returns:
            List of text chunks extracted from the DOCX
        """
        return self.parse_file_content(file_content, filename)
    
    def _get_file_extension(self, filename: str) -> str:
        """
        Get the file extension from filename.
        
        Args:
            filename: Name of the file
            
        Returns:
            File extension with dot (e.g., '.pdf', '.docx')
        """
        _, ext = os.path.splitext(filename)
        return ext.lower()
    
    def _split_into_chunks(self, text: str, filename: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to split
            filename: Source filename for context
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            logger.warning(f"Empty text extracted from {filename}")
            return []
        
        # Clean the text
        text = text.strip()
        
        # If text is shorter than chunk_size, return as single chunk
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = start + chunk_size
            
            # If this is not the last chunk, try to end at a good breaking point
            if end < len(text):
                # Look for paragraph breaks first
                last_double_newline = text.rfind('\n\n', start, end)
                if last_double_newline > start:
                    end = last_double_newline + 2
                else:
                    # Look for single newlines
                    last_newline = text.rfind('\n', start, end)
                    if last_newline > start:
                        end = last_newline + 1
                    else:
                        # Look for sentence endings
                        last_period = text.rfind('. ', start, end)
                        if last_period > start:
                            end = last_period + 2
                        else:
                            # Look for word boundaries
                            last_space = text.rfind(' ', start, end)
                            if last_space > start:
                                end = last_space + 1
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            if end >= len(text):
                break
            start = max(start + 1, end - overlap)
        
        logger.info(f"Split text from {filename} into {len(chunks)} chunks (avg size: {sum(len(c) for c in chunks) // len(chunks)} chars)")
        return chunks
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.
        
        Returns:
            List of supported file extensions
        """
        return ['.pdf', '.docx', '.pptx', '.xlsx', '.txt', '.md', '.html', '.csv', '.json', '.xml']
    
    def is_supported_file(self, filename: str) -> bool:
        """
        Check if file is supported for parsing.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            True if file is supported, False otherwise
        """
        ext = self._get_file_extension(filename)
        return ext in self.get_supported_extensions()


# Global instance
_document_parser = None


def get_document_parser() -> DocumentParser:
    """Get or create the global DocumentParser instance."""
    global _document_parser
    if _document_parser is None:
        _document_parser = DocumentParser()
    return _document_parser
