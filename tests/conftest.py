"""
Test configuration and fixtures for the FastAPI application.
"""

import asyncio
import os
import shutil
import sys
import tempfile
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment variables before importing the app
os.environ["CHROMADB_PATH"] = tempfile.mkdtemp(prefix="test_chromadb_")
os.environ["CHROMADB_COLLECTION"] = "test_collection"
os.environ["AGENT_MEMORY_PATH"] = tempfile.mkdtemp(prefix="test_agent_memory_")


@pytest.fixture(scope="session")
def fastapi_app():
    """Import and return the FastAPI app after environment setup."""
    from main import app

    return app


@pytest.fixture(scope="session")
def openai_api_key():
    """Check if OpenAI API key is available from .env file."""
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not found in .env file - skipping agent tests")
    return api_key


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_dirs():
    """Create and manage test directories."""
    chromadb_dir = os.environ["CHROMADB_PATH"]
    agent_memory_dir = os.environ["AGENT_MEMORY_PATH"]

    yield {"chromadb_dir": chromadb_dir, "agent_memory_dir": agent_memory_dir}

    # Cleanup after all tests
    if os.path.exists(chromadb_dir):
        shutil.rmtree(chromadb_dir)
    if os.path.exists(agent_memory_dir):
        shutil.rmtree(agent_memory_dir)


@pytest.fixture(scope="function")
def client(test_dirs, fastapi_app) -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application."""
    with TestClient(fastapi_app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def sample_documents():
    """Sample documents for testing."""
    return [
        {
            "content": "This is a test document about artificial intelligence and machine learning.",
            "metadata": {"category": "AI", "author": "Test Author"},
        },
        {
            "content": "FastAPI is a modern web framework for building APIs with Python.",
            "metadata": {"category": "Programming", "framework": "FastAPI"},
        },
        {
            "content": "ChromaDB is a vector database for storing and querying embeddings.",
            "metadata": {"category": "Database", "type": "Vector"},
        },
    ]


@pytest.fixture(scope="function")
def sample_text_file():
    """Create a temporary text file for testing file uploads."""
    content = """This is a sample text document for testing file upload functionality.
It contains multiple lines of text that should be parsed and chunked properly.
The document discusses various topics including technology, science, and research.
This content will be used to test the document parsing and insertion capabilities."""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        temp_file_path = f.name

    yield temp_file_path

    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture(scope="function")
def sample_markdown_file():
    """Create a temporary markdown file for testing file uploads."""
    content = """# Test Document

This is a **markdown** document for testing.

## Section 1
- Item 1
- Item 2
- Item 3

## Section 2
This section contains more detailed information about the testing process.

### Subsection
Here we have some code:
```python
def hello_world():
    print("Hello, World!")
```

## Conclusion
This document is used for testing file upload and parsing functionality.
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_file_path = f.name

    yield temp_file_path

    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture(scope="function")
def inserted_document_ids(client, sample_documents):
    """Insert sample documents and return their IDs for testing."""
    import json

    documents_json = json.dumps(sample_documents)
    response = client.post("/docs/insert", data={"documents": documents_json})
    assert response.status_code == 200
    data = response.json()
    return data["document_ids"]


@pytest.fixture(scope="function")
def clean_chromadb():
    """Ensure ChromaDB collection is clean before each test."""
    # This fixture runs before each test to ensure clean state
    # The actual cleanup happens in the test_dirs fixture
    pass
