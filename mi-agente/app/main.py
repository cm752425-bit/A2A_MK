import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas import ChatRequest, ChatResponse
from app.services.agent_service import consultar_agente

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

app = FastAPI(
    title="API del agente de soluciones comerciales y marketing",
    description="API protegida para consultar el agente LangGraph existente.",
    version="1.0.0",
)
WEB_CLIENT = Path(__file__).resolve().parent / "static" / "index.html"
bearer = HTTPBearer(auto_error=False)
PUBLIC_URL = os.getenv(
    "PUBLIC_AGENT_URL", "https://agente-mk-2026-b4e407e65a92.herokuapp.com"
).rstrip("/")


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


@app.get("/salud", tags=["Estado"])
async def salud() -> dict[str, str]:
    """Endpoint de salud solicitado por el coordinador."""
    return {"status": "ok", "service": "agente-mk"}


@app.get("/.well-known/agent-card.json", tags=["A2A"])
async def agent_card() -> dict:
    """Publica la ficha A2A sin exponer credenciales."""
    return {
        "name": "Agente MK — Soluciones comerciales y marketing",
        "description": "Agente especializado en ingeniería comercial y marketing.",
        "url": f"{PUBLIC_URL}/message/send",
        "version": "1.0.0",
        "capabilities": {"streaming": False, "pushNotifications": False},
        "defaultInputModes": ["text"],
        "defaultOutputModes": ["text"],
        "authentication": {
            "schemes": ["bearer"],
            "credentials": "Authorization: Bearer <AGENT_ACCESS_TOKEN>",
        },
        "skills": [
            {
                "id": "marketing-comercial",
                "name": "Ingeniería comercial y marketing",
                "description": "Responde consultas sobre necesidades, propuesta de valor, mercado objetivo y gestión comercial.",
                "tags": ["marketing", "ingenieria-comercial", "mercado-objetivo"],
            }
        ],
    }


def _a2a_error(request_id, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _a2a_text(message: dict) -> tuple[str, str]:
    context_id = str(message.get("contextId") or uuid.uuid4())
    parts = message.get("parts") or []
    texts = [part.get("text", "") for part in parts if isinstance(part, dict) and part.get("kind", "text") == "text"]
    return " ".join(texts).strip(), context_id


@app.post("/message/send", tags=["A2A"])
async def message_send(
    payload: dict = Body(...), _: None = Depends(validar_token)
) -> dict:
    """Recibe una solicitud JSON-RPC A2A message/send."""
    request_id = payload.get("id")
    if payload.get("jsonrpc") != "2.0" or payload.get("method") != "message/send":
        return _a2a_error(request_id, -32600, "Solicitud JSON-RPC message/send no válida.")

    params = payload.get("params") or {}
    message = params.get("message") or {}
    text, context_id = _a2a_text(message)
    if not text:
        return _a2a_error(request_id, -32602, "El mensaje debe contener una parte de texto.")

    message_id = str(uuid.uuid4())
    try:
        response = await consultar_agente(text, context_id)
    except Exception:
        return _a2a_error(request_id, -32000, "El agente no pudo procesar la solicitud.")

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "id": message_id,
            "contextId": context_id,
            "status": {
                "state": "completed",
                "message": {
                    "role": "agent",
                    "messageId": message_id,
                    "contextId": context_id,
                    "parts": [{"kind": "text", "text": response}],
                },
            },
        },
    }


@app.get("/", include_in_schema=False)
async def web_client() -> FileResponse:
    return FileResponse(WEB_CLIENT, media_type="text/html")


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
