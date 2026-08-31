"""Phase 5 assistant endpoint with explicit structured tool requests."""

from fastapi import APIRouter
from pydantic import BaseModel

from src.llm.agent import DecisionAssistant
from src.llm.schemas import AssistantResponse, ToolRequest

router = APIRouter(prefix="/assistant", tags=["assistant"])
assistant = DecisionAssistant()


class QueryPayload(BaseModel):
    tool: str | None = None
    arguments: dict = {}
    text: str | None = None


@router.post("/query", response_model=AssistantResponse)
def query(payload: QueryPayload):
    if payload.text:
        return assistant.from_text(payload.text)
    return assistant.run(
        ToolRequest(tool=payload.tool or "get_operational_state", arguments=payload.arguments)
    )
