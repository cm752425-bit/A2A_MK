"""Cliente A2A del agente conversacional: descubre al agente de viajes y le envía message/send."""
import json
import os
import uuid

import httpx
from dotenv import load_dotenv

from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import get_artifact_text, get_message_text, new_text_message
from a2a.types import Role, SendMessageRequest, TaskState

load_dotenv()


def _sin_kind(datos):
    """Quita los discriminadores kind (A2A 0.3) que langgraph-api >=0.16 emite y los protos de a2a-sdk 1.2.2 rechazan."""
    if isinstance(datos, dict):
        return {clave: _sin_kind(valor) for clave, valor in datos.items() if clave != "kind"}
    if isinstance(datos, list):
        return [_sin_kind(valor) for valor in datos]
    return datos


class _HttpA2A(httpx.AsyncClient):
    """httpx.AsyncClient que elimina kind de las respuestas JSON antes de que el SDK las parsee."""

    async def send(self, request, **kwargs):
        respuesta = await super().send(request, **kwargs)
        if "application/json" not in respuesta.headers.get("content-type", ""):
            return respuesta
        try:
            datos = respuesta.json()
        except Exception:
            return respuesta
        encabezados = {
            clave: valor
            for clave, valor in respuesta.headers.items()
            if clave.lower() not in ("content-length", "content-encoding")
        }
        return httpx.Response(
            status_code=respuesta.status_code,
            headers=encabezados,
            content=json.dumps(_sin_kind(datos)).encode("utf-8"),
            request=respuesta.request,
        )


def _url_base() -> str:
    """URL del servidor de LangGraph, solo desde el entorno."""
    url = os.getenv("A2A_VIAJES_URL")
    if not url:
        raise RuntimeError("Falta A2A_VIAJES_URL en el entorno (.env).")
    return url


def _graph_viajes() -> str:
    """Grafo remoto a consumir, solo desde el entorno."""
    graph_id = os.getenv("A2A_VIAJES_GRAPH")
    if not graph_id:
        raise RuntimeError("Falta A2A_VIAJES_GRAPH en el entorno (.env).")
    return graph_id


def obtener_assistant_id() -> str:
    """Devuelve el assistant_id UUID que el servidor asignó al grafo de viajes."""
    respuesta = httpx.post(
        f"{_url_base()}/assistants/search",
        json={"graph_id": _graph_viajes()},
        timeout=10,
    ).json()
    asistentes = respuesta if isinstance(respuesta, list) else respuesta.get("assistants", [])
    if not asistentes:
        raise RuntimeError(f"El servidor no devolvió asistentes para el grafo {_graph_viajes()}.")
    return asistentes[0]["assistant_id"]


async def crear_cliente_a2a(assistant_id: str):
    """Descarga la Agent Card por GET y devuelve el cliente A2A (JSON-RPC, sin streaming)."""
    http_a2a = _HttpA2A(timeout=120, trust_env=False)
    try:
        resolver = A2ACardResolver(http_a2a, _url_base())
        tarjeta = await resolver.get_agent_card(
            http_kwargs={"params": {"assistant_id": assistant_id}}
        )
        return await create_client(
            tarjeta,
            client_config=ClientConfig(
                httpx_client=http_a2a,
                streaming=False,
                supported_protocol_bindings=["JSONRPC"],
            ),
        )
    except Exception:
        await http_a2a.aclose()
        raise


async def consultar_viajes(texto: str, context_id: str) -> str:
    """Envía un message/send al agente de viajes con el contextId de la conversación y devuelve su texto."""
    try:
        cliente = await crear_cliente_a2a(obtener_assistant_id())
        try:
            mensaje = new_text_message(texto, context_id=context_id, role=Role.ROLE_USER)
            mensaje.message_id = str(uuid.uuid4())
            solicitud = SendMessageRequest(message=mensaje)
            textos: list[str] = []
            async for evento in cliente.send_message(solicitud):
                if evento.HasField("message"):
                    textos.append(get_message_text(evento.message))
                elif evento.HasField("task"):
                    tarea = evento.task
                    if tarea.status.state != TaskState.TASK_STATE_COMPLETED:
                        raise RuntimeError(
                            f"Tarea A2A {tarea.id} no completada: {TaskState.Name(tarea.status.state)}"
                        )
                    textos.extend(get_artifact_text(artifact) for artifact in tarea.artifacts)
                    if not textos and tarea.status.HasField("message"):
                        textos.append(get_message_text(tarea.status.message))
            respuesta = "\n".join(filter(None, textos))
            if not respuesta:
                raise RuntimeError("El agente de viajes no devolvió texto.")
            return respuesta
        finally:
            await cliente.close()
    except Exception as error:
        return f"Error consultando al agente de viajes: {error}"
