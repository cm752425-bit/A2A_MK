"""Agente conversacional · consume al agente de viajes por A2A y agrega una herramienta local (precio BTC)."""
import asyncio
import os
import uuid

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

from src.consumidor import a2a_cliente
from src.consumidor.prompts import SYSTEM_CONVERSACIONAL

load_dotenv()

modelo = ChatGoogleGenerativeAI(
    model=os.environ.get("MODEL_NAME") or os.environ.get("MODELO", "gemini-3.5-flash-lite"),
    google_api_key=os.environ.get("MODEL_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
)

# Regla 6: cada conversación reutiliza su contextId A2A (UUID); iniciar_conversacion() lo renueva.
_CONTEXT_ID = str(uuid.uuid4())


def iniciar_conversacion() -> str:
    """Empieza una conversación nueva: genera y devuelve un contextId A2A UUID fresco."""
    global _CONTEXT_ID
    _CONTEXT_ID = str(uuid.uuid4())
    return _CONTEXT_ID


@tool
def precio_btc() -> dict:
    """Devuelve el precio simulado de Bitcoin en USD."""
    return {"precio_usd": 67432.5, "fuente": "simulado"}


@tool
async def consultar_viajes_remoto(texto: str) -> str:
    """Consulta al agente de viajes remoto (por A2A) y devuelve sus datos entre etiquetas <viajes>...</viajes>."""
    respuesta = await a2a_cliente.consultar_viajes(texto, _CONTEXT_ID)
    return f"<viajes>\n{respuesta}\n</viajes>"


# El checkpointer guarda la conversación por thread_id: el agente recuerda los turnos anteriores.
graph = create_agent(
    model=modelo,
    tools=[precio_btc, consultar_viajes_remoto],
    system_prompt=SYSTEM_CONVERSACIONAL,
    name="agente_conversacional",
    checkpointer=InMemorySaver(),
)


def texto(msg) -> str:
    """El contenido de Gemini puede venir como lista de partes; esto lo aplana a texto."""
    c = msg.content
    return c if isinstance(c, str) else " ".join(p.get("text", "") for p in c if isinstance(p, dict))


async def _demo() -> None:
    """Consumo multi-turno: mismo thread_id y mismo contextId A2A en los 3 turnos (reglas 6 y 7)."""
    context_id = iniciar_conversacion()
    print(f"contextId A2A: {context_id}")
    hilo = {"configurable": {"thread_id": "consumidor-demo"}}
    preguntas = [
        "Quiero un vuelo de Santiago a Lima el 2026-11-10",
        "¿Y cuánto está el precio de BTC?",
        "¿Cuánto salía el vuelo que me buscaste?",
    ]
    for pregunta in preguntas[:3]:  # tope de 3 turnos
        resultado = await graph.ainvoke({"messages": [HumanMessage(content=pregunta)]}, hilo)
        print(f"\n> {pregunta}\n{texto(resultado['messages'][-1])}")


if __name__ == "__main__":
    asyncio.run(_demo())
