# 🛠️ Developer Guide - AI Agent Web Server

This guide provides technical documentation for developers who want to understand, modify, or extend the AI Agent Web Server.

## 🏗️ Architecture Overview

The application is built with a modular architecture using FastAPI as the web framework:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │────│   Route Layer   │────│  Business Logic │
│   (main.py)     │    │ agent_api.py    │    │   agent.py      │
│                 │    │ docs_api.py     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                         │
                       ┌─────────────────┐              │
                       │ Knowledge Base  │◄─────────────┘
                       │   chromadb.py   │
                       │ doc_parsing.py  │
                       └─────────────────┘
```

### Core Components

1. **FastAPI Application** (`main.py`)
   - Entry point and application setup
   - Route registration
   - Startup event handlers

2. **Route Layer** (`routes/`)
   - API endpoint definitions
   - Request/response validation
   - Error handling

3. **Business Logic** (`processing/`)
   - OpenAI Agents SDK integration
   - Session management
   - Tool orchestration

4. **Knowledge Base** (`knowledge_base/`)
   - Vector database operations
   - Document processing pipeline
   - Search functionality

## 📁 Project Structure

```
simple_ai_agent_web_server/
├── main.py                          # FastAPI app and startup
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
├── README.md                        # User documentation
├── README-DEV.md                    # This file
│
├── processing/                      # Agent processing logic
│   ├── __init__.py
│   └── agent.py                     # OpenAI Agents SDK integration
│
├── routes/                          # API route definitions
│   ├── __init__.py
│   ├── agent_api.py                 # Agent chat endpoints
│   └── docs_api.py                  # Document CRUD endpoints
│
├── knowledge_base/                  # Knowledge management
│   ├── __init__.py
│   ├── chromadb.py                  # Vector database operations
│   └── doc_parsing.py               # Document processing pipeline
│
└── tests/                           # Test suite
    ├── conftest.py                  # Pytest configuration
    ├── test_agent_api.py            # Agent API tests
    ├── test_agent_knowledge_integration.py  # Knowledge integration tests
    ├── test_docs_api.py             # Document API tests
    └── test_knowledge_base.py       # Core knowledge base tests
```

## 🔧 Technical Stack

### Core Dependencies

- **FastAPI 0.116.1**: Modern web framework with automatic OpenAPI generation
- **OpenAI Agents SDK 0.2.4**: Agent orchestration and tool management
- **ChromaDB 1.0.15**: Vector database for semantic search
- **MarkItDown 0.1.2**: Universal document parsing library
- **Pydantic 2.11.7**: Data validation and serialization

### Development Dependencies

- **pytest 8.4.1**: Testing framework
- **pytest-asyncio**: Async test support
- **httpx**: HTTP client for testing

## 🚀 Development Setup

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd simple_ai_agent_web_server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

Configure required environment variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional - Development overrides
CHROMADB_PATH=dev_knowledge_base
AGENT_MEMORY_PATH=dev_memory
CHROMADB_COLLECTION=dev_collection
```

### 3. Development Server

```bash
# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run with debug logging
uvicorn main:app --reload --log-level debug
```

## 🧪 Testing

### Test Architecture

The test suite is organized into several categories:

1. **Unit Tests** (`test_knowledge_base.py`)
   - ChromaDB operations
   - Document parsing
   - Core utility functions

2. **API Tests** (`test_docs_api.py`, `test_agent_api.py`)
   - HTTP endpoint testing
   - Request/response validation
   - Error handling

3. **Integration Tests** (`test_agent_knowledge_integration.py`)
   - End-to-end workflows
   - Agent-knowledge base interaction
   - Real OpenAI API integration

4. **LLM Parsing Tests** (`test_llm_parsing.py`)
   - Standard vs LLM-enhanced parsing modes
   - Environment configuration testing
   - Parser initialization and fallback behavior
   - Consistency testing between parsing modes

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_agent_api.py

# With coverage
pytest --cov=. --cov-report=html

# Only unit tests (no OpenAI API required)
pytest tests/test_knowledge_base.py tests/test_docs_api.py

# Integration tests (requires OpenAI API key)
pytest tests/test_agent_knowledge_integration.py
```

### Test Configuration

Tests use temporary directories and isolated databases:

```python
# conftest.py - Test fixtures
@pytest.fixture
def temp_chromadb_path():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def openai_api_key():
    # Automatically skips tests if no API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")
    return api_key
```

## 📊 API Design

### Document Management API (`/docs`)

```python
# docs_api.py
@router.post("/insert")
async def insert_documents(
    documents: Optional[str] = Form(None),
    files: List[UploadFile] = File([])
) -> Dict[str, Any]:
    # Handles both JSON and file uploads
    # Returns document IDs and processing summary
```

### Agent API (`/agent`)

```python
# agent_api.py
@router.post("/query")
async def query_agent(request: AgentRequest) -> AgentResponse:
    # Processes agent queries with session management
    # Returns agent response and session ID
```

### Request/Response Models

```python
# Pydantic models for validation
class AgentRequest(BaseModel):
    query: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    model: Optional[str] = None

class AgentResponse(BaseModel):
    response: str
    session_id: str
```

## 🧠 AI Agent Implementation

### Agent Configuration

```python
# processing/agent.py
agent = Agent(
    name="Helpful Assistant",
    instructions="You are a helpful assistant with access to web search and a knowledge base...",
    model=model or DEFAULT_MODEL,
    tools=[WebSearchTool(), search_knowledge_base],
)
```

### Custom Knowledge Base Tool

```python
# knowledge_base/chromadb.py
@function_tool
async def search_knowledge_base(query: str, max_results: int = 5) -> str:
    """
    Search the knowledge base for relevant documents.
    Returns formatted results with content and metadata.
    """
    # Implementation handles search, formatting, and error cases
```

### Session Management

```python
# SQLite-based session persistence
session = SQLiteSession(session_id, DB_PATH)
result = await Runner.run(agent, query, session=session)
```

## 🗄️ Knowledge Base Architecture

### ChromaDB Integration

```python
class ChromaDBManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(...)
    
    def insert_documents(self, documents, metadatas):
        # Vector embedding and storage
    
    def query_documents(self, query_text, n_results, where):
        # Semantic search with metadata filtering
```

### Document Processing Pipeline

```python
class DocumentParser:
    def __init__(self, use_llm: bool = False, llm_model: str = "gpt-4o", openai_api_key: Optional[str] = None):
        # Initialize MarkItDown with optional LLM enhancement
        if use_llm and openai_api_key:
            client = OpenAI(api_key=openai_api_key)
            self.md_converter = MarkItDown(llm_client=client, llm_model=llm_model)
        else:
            self.md_converter = MarkItDown()
    
    def parse_file_content(self, content: bytes, filename: str):
        # 1. Detect file type
        # 2. Extract text using MarkItDown (with optional LLM enhancement)
        # 3. Split into chunks with intelligent boundaries
        # 4. Return processed chunks
    
    def _split_into_chunks(self, text: str, filename: str):
        # Intelligent text chunking with overlap
        # Preserves context boundaries (paragraphs, sentences, words)
```

#### LLM-Enhanced Parsing

The document parser supports two modes:

**Standard Mode** (default):
- Fast processing using MarkItDown's built-in converters
- No additional API costs
- Reliable for most document types

**LLM-Enhanced Mode** (optional):
- Uses OpenAI's LLM for intelligent document understanding
- Better image descriptions and complex layout processing
- Controlled via environment variables:

```env
MARKITDOWN_USE_LLM=true         # Enable LLM enhancement
MARKITDOWN_LLM_MODEL=gpt-4o     # Choose model
```

**Implementation Details:**
```python
# Environment-based configuration
def get_document_parser() -> DocumentParser:
    use_llm = os.getenv("MARKITDOWN_USE_LLM", "false").lower() == "true"
    llm_model = os.getenv("MARKITDOWN_LLM_MODEL", "gpt-4o")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    return DocumentParser(
        use_llm=use_llm,
        llm_model=llm_model,
        openai_api_key=openai_api_key
    )
```

## 🔌 Adding New Features

### Adding a New Tool

1. Create the tool function:
```python
@function_tool
async def my_custom_tool(parameter: str) -> str:
    """Tool description for the agent."""
    # Implementation
    return result
```

2. Register with agent:
```python
# processing/agent.py
tools=[WebSearchTool(), search_knowledge_base, my_custom_tool]
```

### Adding New API Endpoints

1. Define route in appropriate router:
```python
# routes/docs_api.py
@router.post("/my-endpoint")
async def my_endpoint(request: MyRequest) -> MyResponse:
    # Implementation
```

2. Add request/response models:
```python
class MyRequest(BaseModel):
    field: str = Field(..., description="Field description")

class MyResponse(BaseModel):
    result: str
```

3. Add tests:
```python
def test_my_endpoint(client: TestClient):
    response = client.post("/docs/my-endpoint", json={"field": "value"})
    assert response.status_code == 200
```

### Extending Document Support

1. Update supported extensions:
```python
# knowledge_base/doc_parsing.py
def get_supported_extensions(self) -> List[str]:
    base_extensions = [".pdf", ".docx", ".txt", ".md"]
    # Add new extensions
    return base_extensions + [".new_type"]
```

2. Add processing logic if needed:
```python
def parse_file_content(self, content: bytes, filename: str):
    # Add custom processing for new file types
```

## 🔍 Debugging and Monitoring

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use throughout the application
logger.info("Processing document")
logger.error(f"Error processing: {str(e)}")
```

### Error Handling

```python
# Consistent error responses
@router.post("/endpoint")
async def endpoint():
    try:
        # Implementation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Performance Monitoring

```python
# Add timing decorators
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        logger.info(f"{func.__name__} took {time.time() - start:.2f}s")
        return result
    return wrapper
```

## 🚀 Deployment

### Production Configuration

```env
# .env.production
OPENAI_API_KEY=prod_key
CHROMADB_PATH=/app/data/knowledge_base
AGENT_MEMORY_PATH=/app/data/memory
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Performance Considerations

- **ChromaDB**: Stores data persistently on disk
- **Agent Memory**: SQLite database for session storage
- **File Uploads**: Consider size limits and processing time
- **Concurrent Requests**: FastAPI handles async requests efficiently

## 🔧 Configuration Management

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | None |
| `CHROMADB_PATH` | ChromaDB storage path | `knowledge_base` |
| `AGENT_MEMORY_PATH` | Agent session storage | `memory` |
| `CHROMADB_COLLECTION` | Collection name | `standard_collection` |
| `MARKITDOWN_USE_LLM` | Enable LLM-enhanced document parsing | `false` |
| `MARKITDOWN_LLM_MODEL` | LLM model for enhanced parsing | `gpt-4o` |

### Configuration Validation

```python
# Add validation in main.py
import os

def validate_config():
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is required")
    
    # Validate paths, create directories
    kb_path = os.getenv("CHROMADB_PATH", "knowledge_base")
    os.makedirs(kb_path, exist_ok=True)
```

## 📈 Performance Optimization

### ChromaDB Optimization

```python
# Batch operations for better performance
def insert_documents_batch(self, documents, metadatas, batch_size=100):
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_meta = metadatas[i:i+batch_size]
        self.collection.add(documents=batch_docs, metadatas=batch_meta)
```

### Caching Strategies

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_search_results(query: str, n_results: int):
    # Cache frequent searches
    return self.query_documents(query, n_results)
```

## 🛡️ Security Considerations

### API Key Management
- Never commit API keys to version control
- Use environment variables or secret management systems
- Rotate keys regularly

### Input Validation
- All inputs are validated with Pydantic models
- File upload limits and type checking
- SQL injection prevention (using ChromaDB API)

### Error Handling
- Don't expose internal details in error messages
- Log security events appropriately
- Implement rate limiting for production

## 🤝 Contributing

### Code Style
- Follow PEP 8 conventions
- Use type hints consistently
- Add docstrings for public functions

### Testing Requirements
- Add tests for new features
- Maintain test coverage above 80%
- Test both success and error cases

### Pull Request Process
1. Create feature branch
2. Add tests
3. Update documentation
4. Submit PR with clear description

---

*Happy coding! 🚀*
