import os
import uuid
from typing import Optional
from dotenv import load_dotenv

from agents import Agent, Runner, SQLiteSession, WebSearchTool

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DEFAULT_MODEL = "gpt-4.1"
MEMORY_DIR = os.getenv("AGENT_MEMORY_PATH", "memory")
DB_PATH = os.path.join(MEMORY_DIR, "conversation_history.db")





# Main agent runner function
async def run_agent(query: str, session_id: Optional[str] = None, model: Optional[str] = None):
    """
    Run the agent with the given query, session ID, and optional model override.
    If session_id is not provided, a new one is generated.
    Returns the agent's response and the session ID used.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set in .env file.")

    # Generate a new session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())

    # Define the agent instance (with optional model override)
    agent = Agent(
        name="Helpful Assistant",
        instructions="You are a helpful assistant.",
        model=model or DEFAULT_MODEL,
        tools=[WebSearchTool()],
    )

    # Set up persistent session memory
    session = SQLiteSession(session_id, DB_PATH)

    # Run the agent and get the result
    result = await Runner.run(agent, query, session=session)

    return result.final_output, session_id
