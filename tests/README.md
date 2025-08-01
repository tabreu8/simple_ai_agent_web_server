# Testing Guide

This document provides comprehensive information about testing the FastAPI AI Agent Web Server.

## Overview

The test suite covers:
- Document API endpoints (`/docs/*`)
- Agent API endpoints (`/agent/*`)
- Knowledge base functionality (ChromaDB and document parsing)
- Integration workflows
- Error handling and edge cases

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Test configuration and fixtures
├── test_docs_api.py         # Document API endpoint tests
├── test_agent_api.py        # Agent API endpoint tests
└── test_knowledge_base.py   # Knowledge base unit tests
```

## Running Tests

### Quick Start

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests with server startup
python run_tests.py

# Or use make commands
make test
```

### Test Commands

```bash
# Run all tests
make test

# Run unit tests only (no server required)
make test-unit

# Run API tests only (requires server)
make test-api

# Run integration tests
make test-integration

# Run with coverage
make test-coverage

# Run specific test file
make test-specific FILE=test_docs_api.py

# Quick test for development (no server startup)
make test-fast

# Clean test artifacts
make clean-test
```

### Using pytest directly

```bash
# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_docs_api.py::TestDocumentInsert -v

# Run specific test method
pytest tests/test_docs_api.py::TestDocumentInsert::test_insert_json_documents_success -v

# Run with markers
pytest tests/ -m "not slow" -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## Test Categories

### 1. Document API Tests (`test_docs_api.py`)

#### Insert Document Tests
- JSON document insertion
- File upload (text, markdown)
- Combined JSON + file uploads
- Error handling (empty content, unsupported files)
- Deprecated upload endpoint

#### Search Tests
- Basic text search
- Metadata filtering
- Parameter validation (n_results, filters)
- Invalid input handling

#### CRUD Operations
- Document retrieval by ID
- Document updates (content and metadata)
- Document deletion
- Error handling for non-existent documents

#### Collection Statistics
- Stats retrieval
- Supported file types listing

#### Integration Flows
- Complete document lifecycle (insert → search → get → update → delete)
- File upload and search workflow
- Metadata filtering workflow

### 2. Agent API Tests (`test_agent_api.py`)

#### Basic Functionality
- Agent query processing
- Session management
- Model parameter handling
- Error handling

#### Integration Scenarios
- Conversation flows
- Model switching
- Concurrent sessions

### 3. Knowledge Base Tests (`test_knowledge_base.py`)

#### ChromaDB Manager Tests
- Document insertion and querying
- CRUD operations
- Metadata filtering
- Collection statistics

#### Document Parser Tests
- File type support detection
- Text file parsing
- Markdown file parsing
- Text chunking
- Error handling

#### Integration Tests
- ChromaDB + DocumentParser integration
- Complete file processing workflow

## Test Fixtures

The test suite uses several fixtures defined in `conftest.py`:

- `client`: FastAPI test client
- `sample_documents`: Pre-defined test documents
- `sample_text_file`: Temporary text file for testing
- `sample_markdown_file`: Temporary markdown file for testing
- `inserted_document_ids`: Documents inserted for testing
- `test_dirs`: Temporary directories for test data

## Environment Setup

Tests use isolated environments:

```python
# Temporary directories for test data
CHROMADB_PATH = tempfile.mkdtemp(prefix="test_chromadb_")
CHROMADB_COLLECTION = "test_collection"
AGENT_MEMORY_PATH = tempfile.mkdtemp(prefix="test_agent_memory_")
```

## Important Test Flows

### 1. Document Lifecycle Test
```python
def test_complete_document_lifecycle(self, client):
    # 1. Insert document
    # 2. Search for document
    # 3. Retrieve specific document
    # 4. Update document
    # 5. Delete document
    # 6. Verify deletion
```

### 2. File Upload and Search Flow
```python
def test_file_upload_and_search_flow(self, client, sample_text_file):
    # 1. Upload file
    # 2. Search for file content
    # 3. Verify file appears in results
```

### 3. Metadata Filtering Flow
```python
def test_metadata_filtering_flow(self, client):
    # 1. Insert documents with different metadata
    # 2. Search with category filter
    # 3. Verify filtering works correctly
```

## Mocking Strategy

The test suite uses mocking for:

- Agent processing (`routes.agent_api.run_agent`)
- External dependencies when needed
- MarkItDown parsing errors

Example:
```python
@patch('routes.agent_api.run_agent')
def test_agent_query_success(self, mock_run_agent, client):
    mock_run_agent.return_value = ("Test response", "session_123")
    # ... test logic
```

## Coverage Goals

The test suite aims for high coverage across:

- All API endpoints
- Core business logic
- Error handling paths
- Edge cases
- Integration scenarios

## Continuous Integration

For CI/CD environments:

```bash
make ci-test
```

This command:
1. Installs test dependencies
2. Runs tests with coverage
3. Generates coverage reports

## Development Workflow

During development:

```bash
# Quick tests without server startup
make test-fast

# Watch mode for continuous testing
make test-watch

# Clean and run full suite
make dev-test
```

## Debugging Tests

For debugging failing tests:

```bash
# Run with verbose output and no capture
pytest tests/test_docs_api.py::TestDocumentInsert::test_insert_json_documents_success -v -s

# Run with pdb debugging
pytest tests/test_docs_api.py::TestDocumentInsert::test_insert_json_documents_success -v -s --pdb
```

## Performance Considerations

- Tests use temporary directories that are cleaned up automatically
- Database operations are isolated per test function
- Server startup/shutdown is handled by the test runner
- Large file tests are avoided to maintain test speed

## Adding New Tests

When adding new functionality:

1. Add unit tests for core logic
2. Add API tests for new endpoints
3. Add integration tests for workflows
4. Update this documentation
5. Ensure tests are properly categorized with markers

Example test structure:
```python
class TestNewFeature:
    """Test cases for new feature."""
    
    def test_basic_functionality(self, client):
        """Test basic feature functionality."""
        pass
    
    def test_error_handling(self, client):
        """Test feature error handling."""
        pass
    
    def test_integration_workflow(self, client):
        """Test feature integration with other components."""
        pass
```
