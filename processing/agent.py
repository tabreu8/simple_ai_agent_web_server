import os
import uuid
from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession

import os
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DEFAULT_MODEL = "gpt-4.1"
MEMORY_DIR = "memory"
DB_PATH = os.path.join(MEMORY_DIR, "conversation_history.db")

# Ensure the memory directory exists
os.makedirs(MEMORY_DIR, exist_ok=True)

# Basic agent setup
def get_agent(model: str = None):
    return Agent(
        name="Helpful Assistant",
        instructions="You are a helpful assistant.",
        model=model or DEFAULT_MODEL,
    )

async def run_agent(query: str, session_id: str = None, model: str = None):
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set in .env file.")
    if not session_id:
        session_id = str(uuid.uuid4())
    agent = get_agent(model)
    session = SQLiteSession(session_id, DB_PATH)
    result = await Runner.run(agent, query, session=session)
    return result.final_output, session_id
