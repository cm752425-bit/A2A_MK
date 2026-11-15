import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas import ChatRequest, ChatResponse
from app.services.agent_service import consultar_agente

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

app = FastAPI(
    title="API del agente de soluciones comerciales y marketing",
    description="API protegida para consultar el agente LangGraph existente.",
    version="1.0.0",
)
bearer = HTTPBearer(auto_error=False)


def validar_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> None:
    expected = os.getenv("AGENT_ACCESS_TOKEN")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El servicio no tiene configurado AGENT_ACCESS_TOKEN.",
        )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere un token Bearer.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if credentials.credentials != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no válido.",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/health", tags=["Estado"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "agent-api"}


@app.post("/chat", response_model=ChatResponse, tags=["Agente"])
async def chat(request: ChatRequest, _: None = Depends(validar_token)) -> ChatResponse:
    message = request.message.strip()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El campo message no puede estar vacío.",
        )

    request_id = str(uuid.uuid4())
    try:
        response = await consultar_agente(message, request_id)
    except TimeoutError as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="El agente agotó el tiempo de espera.",
        ) from error
    except (ConnectionError, OSError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El proveedor o servicio externo no está disponible.",
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El agente no pudo procesar la solicitud.",
        ) from error

    return ChatResponse(success=True, response=response, request_id=request_id)
