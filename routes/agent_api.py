from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from processing.agent import run_agent


class AgentQuery(BaseModel):
    query: str = Field(..., min_length=1, description="Query text cannot be empty")
    session_id: Optional[str] = None
    model: Optional[str] = None


class AgentResponse(BaseModel):
    response: str
    session_id: str


router = APIRouter()


@router.post("/query", response_model=AgentResponse)
async def query_agent(payload: AgentQuery):
    try:
        response, session_id = await run_agent(
            payload.query, payload.session_id, payload.model
        )
        return AgentResponse(response=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
