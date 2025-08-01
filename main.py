import os

from fastapi import FastAPI

from routes.agent_api import router as agent_router
from routes.docs_api import router as docs_router

app = FastAPI(
    title="Simple AI Agent Web Server",
    description="FastAPI server with OpenAI Agents SDK and ChromaDB vector store",
    version="1.0.0",
)


# Create directories on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    # Ensure knowledge base directory exists
    kb_path = os.getenv("CHROMADB_PATH", "knowledge_base")
    os.makedirs(kb_path, exist_ok=True)
    print(f"Knowledge base directory ensured at: {kb_path}")

    # Ensure agent memory directory exists
    memory_path = os.getenv("AGENT_MEMORY_PATH", "memory")
    os.makedirs(memory_path, exist_ok=True)
    print(f"Agent memory directory ensured at: {memory_path}")


app.include_router(agent_router, prefix="/agent")
app.include_router(docs_router, prefix="/docs")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Simple AI Agent Web Server",
        "version": "1.0.0",
        "endpoints": {
            "agent": "/agent",
            "docs": "/docs",
            "docs_stats": "/docs/stats",
            "openapi": "/docs",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
