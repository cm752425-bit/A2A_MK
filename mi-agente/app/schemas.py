from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="Consulta que recibirá el agente")


class ChatResponse(BaseModel):
    success: bool
    response: str
    request_id: str
