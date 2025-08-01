# Simple AI Agent Web Server

A Python FastAPI server using OpenAI Agents SDK with persistent ChromaDB vector storage and document processing capabilities.

## Features

- **OpenAI Agents SDK**: AI agent functionality with session memory
- **ChromaDB Vector Store**: Persistent vector database for document storage and retrieval
- **Document Processing**: Support for PDF, DOCX, and other file formats using MarkItDown
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Environment Configuration**: .env-based configuration

## Project Structure

```
├── main.py                     # FastAPI server entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── processing/
│   └── agent.py               # AI agent logic
├── routes/
│   ├── agent_api.py           # Agent API routes
│   └── docs_api.py            # Document management API routes
└── knowledge_base/
    ├── __init__.py            # Package initialization
    ├── chromadb.py            # ChromaDB operations
    └── doc_parsing.py         # Document parsing using MarkItDown
```

## Setup

### 1. Environment Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# OpenAI API Key (required for agent functionality)
OPENAI_API_KEY=your-openai-key-here

# ChromaDB Configuration
CHROMADB_PATH=knowledge_base              # Database storage path
CHROMADB_COLLECTION=standard_collection   # Collection name
```

### 3. Run the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`.

## API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Agent API

#### Query Agent
```http
POST /agent/query
Content-Type: application/json

{
  "query": "Hello!",
  "session_id": "optional-session-id",
  "model": "optional-model"
}
```

Response:
```json
{
  "response": "Hi! How can I help you?",
  "session_id": "generated-or-provided-id"
}
```

The `session_id` parameter allows the agent to remember previous messages and maintain conversation context. If you use the same `session_id` for multiple requests, the agent will recall earlier exchanges and respond accordingly.

### Document Management API

#### Upload and Process File
```http
POST /docs/docs/upload
Content-Type: multipart/form-data

Upload a PDF, DOCX, or other supported file for processing and storage.
```

#### Insert Document Chunks
```http
POST /docs/docs/insert
Content-Type: application/json

{
  "chunks": ["Text chunk 1", "Text chunk 2"],
  "metadata": [{"source": "manual"}, {"source": "manual"}]
}
```

#### Search Documents
```http
GET /docs/docs/search?query=your search query&n_results=10&metadata_filter={"source":"manual"}
```

#### Update Document
```http
PUT /docs/docs/{doc_id}
Content-Type: application/json

{
  "document": "Updated content",
  "metadata": {"updated": true}
}
```

#### Delete Document
```http
DELETE /docs/docs/{doc_id}
```

#### Get Document
```http
GET /docs/docs/{doc_id}
```

#### Collection Statistics
```http
GET /docs/stats
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | Your OpenAI API key |
| `CHROMADB_PATH` | `knowledge_base` | Directory for ChromaDB storage |
| `CHROMADB_COLLECTION` | `standard_collection` | ChromaDB collection name |
| `AGENT_MEMORY_PATH` | `memory` | Directory for agent conversation history storage |

### Supported File Types

The document processing supports the following file types:
- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- PowerPoint (`.pptx`)
- Excel (`.xlsx`)
- Text files (`.txt`)
- Markdown (`.md`)
- HTML (`.html`)
- CSV (`.csv`)
- JSON (`.json`)
- XML (`.xml`)

## ChromaDB Features

- **Persistent Storage**: Data is automatically saved and persisted across server restarts
- **Vector Similarity Search**: Semantic search using embeddings
- **Metadata Filtering**: Filter documents by metadata attributes
- **Automatic Embeddings**: Documents are automatically embedded using ChromaDB's default embedding function

## Document Processing Features

- **Automatic Chunking**: Large documents are split into manageable chunks with overlap
- **Metadata Enrichment**: Automatic addition of source filename, file size, and processing timestamps
- **Content Extraction**: Text extraction from various file formats using MarkItDown
- **Error Handling**: Robust error handling for unsupported files and processing issues

## Development

## Development

### Running Tests

The project includes a comprehensive test suite covering all API endpoints and core functionality.

#### Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Install all dependencies (including test dependencies)
pip install -r requirements.txt

# Validate test setup
python3 validate_tests.py

# Run all tests with server startup
python3 run_tests.py

# Or use make commands (if make is available)
make test
```

#### Available Test Commands

```bash
# Run all tests
make test

# Run unit tests only (no server required)
make test-unit

# Run API tests only
make test-api

# Run with coverage report
make test-coverage

# Run specific test file
make test-specific FILE=test_docs_api.py

# Quick test for development (no server startup)
make test-fast

# Clean test artifacts
make clean-test
```

#### Test Categories

- **API Tests**: Complete endpoint testing including document CRUD, search, and agent queries
- **Unit Tests**: Knowledge base functionality (ChromaDB and document parsing)
- **Integration Tests**: End-to-end workflows like document upload → search → retrieval
- **Error Handling**: Comprehensive error condition testing

See `tests/README.md` for detailed testing documentation.

### Running the Development Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Code Structure

- **main.py**: FastAPI application setup and startup logic
- **knowledge_base/chromadb.py**: ChromaDB client management and operations
- **knowledge_base/doc_parsing.py**: Document parsing and chunking logic
- **routes/docs_api.py**: Document management API endpoints
- **routes/agent_api.py**: AI agent API endpoints

## Dependencies

Key dependencies include:
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `chromadb`: Vector database
- `markitdown[all]`: Document processing
- `openai-agents`: OpenAI Agents SDK
- `python-multipart`: File upload support

## License

This project is licensed under the MIT License.
