# 🤖 AI Agent Web Server

A smart document assistant that helps you upload documents and chat with an AI agent that has access to your knowledge base. Upload PDFs, Word documents, or text files, then ask questions and get answers based on your uploaded content!

## ✨ What Can It Do?

- 📄 **Upload Documents**: Support for PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx), text files, and more
- 🤖 **Smart AI Agent**: Chat with an AI that can search through your uploaded documents
- 🔍 **Knowledge Search**: Find relevant information from your document collection
- 💬 **Conversation Memory**: The AI remembers context within conversation sessions
- 🌐 **Web Access**: AI can also search the web for additional information

## 🚀 Quick Start

### 1. Setup Your Environment

First, make sure you have Python 3.8+ installed. Then:

```bash
# Clone or download this project
cd simple_ai_agent_web_server

# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Your OpenAI API Key

Create a `.env` file with your OpenAI API key:

```bash
# Copy the example file
cp .env.example .env
```

Edit the `.env` file and add your OpenAI API key:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

> 💡 **Need an API key?** Get one from [OpenAI's website](https://platform.openai.com/api-keys)

### 3. Start the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000` 🎉

## 📖 How to Use

### Using the Interactive API Documentation

The easiest way to try the application is through the built-in API documentation:

1. Open your browser to `http://localhost:8000/docs`
2. You'll see an interactive interface where you can test all features

### 📄 Upload Documents

**Option 1: Upload a file**
1. Go to `http://localhost:8000/docs`
2. Find the `POST /docs/insert` endpoint
3. Click "Try it out"
4. Use the file upload option to select your document
5. Click "Execute"

**Option 2: Add text directly**
1. Use the same endpoint but provide JSON data:
```json
{
  "documents": [
    {
      "content": "Your document text here",
      "metadata": {
        "filename": "my_notes.txt",
        "category": "personal"
      }
    }
  ]
}
```

### 🤖 Chat with the AI Agent

1. Go to the `POST /agent/query` endpoint
2. Try asking questions about your uploaded documents:

```json
{
  "query": "What information do you have about project management?",
  "session_id": "my_session_001"
}
```

**Example Questions:**
- "Summarize the main points from the uploaded documents"
- "What does the manual say about installation procedures?"
- "Find information about pricing in the uploaded files"

### 🔍 Search Your Documents

Use the `GET /docs/search` endpoint to search without the AI:

```
GET /docs/search?query=installation&n_results=5
```

## 💡 Usage Examples

### Complete Workflow Example

1. **Upload a document** (e.g., a user manual PDF)
2. **Ask the AI**: "How do I install this software according to the manual?"
3. **Follow up**: "What are the system requirements?"
4. **Search directly**: Find all mentions of "troubleshooting"

### Conversation Sessions

Use the same `session_id` to maintain conversation context:

```json
// First message
{
  "query": "What projects are mentioned in the documents?",
  "session_id": "work_session_123"
}

// Follow-up message (same session)
{
  "query": "What's the budget for the first project you mentioned?",
  "session_id": "work_session_123"
}
```

## 🛠️ Supported File Types

- **PDFs** (.pdf)
- **Microsoft Word** (.docx)
- **PowerPoint** (.pptx) 
- **Excel** (.xlsx)
- **Text files** (.txt)
- **Markdown** (.md)
- **HTML** (.html)
- **CSV** (.csv)
- **JSON** (.json)
- **XML** (.xml)

## 🌐 API Endpoints Overview

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/docs/insert` | POST | Upload documents or add text |
| `/docs/search` | GET | Search through documents |
| `/docs/{doc_id}` | GET | Get specific document |
| `/docs/{doc_id}` | PUT | Update document |
| `/docs/{doc_id}` | DELETE | Delete document |
| `/docs/stats` | GET | Get collection statistics |
| `/agent/query` | POST | Chat with AI agent |

## 🎯 Use Cases

- **Personal Knowledge Base**: Upload your notes, manuals, and documents, then ask questions
- **Customer Support**: Upload product documentation and let the AI help answer questions
- **Research Assistant**: Upload research papers and get summaries or find specific information
- **Document Analysis**: Upload reports and ask for insights or specific data points
- **Learning Aid**: Upload textbooks or course materials and ask study questions

## 🔧 Configuration Options

Edit your `.env` file to customize:

```env
# Required
OPENAI_API_KEY=your_api_key

# Optional - Storage locations
CHROMADB_PATH=knowledge_base     # Where documents are stored
AGENT_MEMORY_PATH=memory         # Where conversation history is stored
CHROMADB_COLLECTION=standard_collection  # Database collection name
```

## ❓ Troubleshooting

**The AI doesn't find information from my documents:**
- Make sure your documents uploaded successfully (check the upload response)
- Try rephrasing your question
- The AI searches for semantically similar content, not exact keyword matches

**Upload fails:**
- Check that your file type is supported
- Ensure the file isn't corrupted
- Large files may take longer to process

**API key errors:**
- Verify your OpenAI API key is correct in the `.env` file
- Make sure you have credits available in your OpenAI account

**Server won't start:**
- Check that port 8000 isn't already in use
- Make sure all dependencies are installed: `pip install -r requirements.txt`

## 🤝 Need Help?

- Check the interactive API docs at `http://localhost:8000/docs`
- Look at the example requests in the API documentation
- See `README-DEV.md` for technical details and development information

---

*Enjoy building your smart document assistant! 🚀*

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

---

*Enjoy building your smart document assistant! 🚀*

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
