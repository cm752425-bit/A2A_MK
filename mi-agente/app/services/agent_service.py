import os
import uuid

from langchain_core.messages import HumanMessage


def _message_text(message) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            part.get("text", "") for part in content if isinstance(part, dict)
        ).strip()
    return str(content)


async def consultar_agente(message: str, request_id: str | None = None) -> str:
    """Ejecuta el agente real directamente o mediante el protocolo A2A."""
    if os.getenv("AGENT_EXECUTION_MODE", "direct").lower() == "a2a":
        from src.consumidor.a2a_cliente import consultar_viajes

        return await consultar_viajes(message, request_id or str(uuid.uuid4()))

    # Se importa bajo demanda para que /health y la documentación funcionen
    # aunque todavía no se haya configurado la clave del proveedor.
    from src.agente_viajes.graph import graph

    result = await graph.ainvoke({"messages": [HumanMessage(content=message)]})
    messages = result.get("messages", [])
    if not messages:
        raise RuntimeError("El agente no devolvió mensajes.")
    response = _message_text(messages[-1]).strip()
    if not response:
        raise RuntimeError("El agente devolvió una respuesta vacía.")
    return response
