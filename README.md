# Simple AI Agent Web Server

This project is a FastAPI server using the OpenAI Agents SDK. It provides an endpoint to interact with an LLM agent, supporting persistent SQLite session storage and .env-based OpenAI key configuration.

## Features
- Query endpoint for agent interaction
- Optional sessionID and model selection
- Persistent SQLite storage for sessions
- Modular code structure

## Project Structure
- `main.py`: Launches FastAPI server
- `routes/agent_api.py`: API route for agent queries
- `processing/agent.py`: Agent implementation

## Usage
1. Set your OpenAI API key in a `.env` file as `OPENAI_API_KEY=your-key`.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `uvicorn main:app --reload`

## Session Memory

The `session_id` parameter allows the agent to remember previous messages and maintain conversation context. If you use the same `session_id` for multiple requests, the agent will recall earlier exchanges and respond accordingly. If you omit `session_id`, a new session is created and returned in the response.

This enables multi-turn conversations, where the agent can remember facts (like your name) or previous questions within the same session.

## API Example
```
POST /agent/query
{
  "query": "Hello!",
  "session_id": "optional-session-id",
  "model": "optional-model"
}
```
Response:
```
{
  "response": "Hi! How can I help you?",
  "session_id": "generated-or-provided-id"
}
```
