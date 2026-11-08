import nbformat as nbf
import os

nb = nbf.v4.new_notebook()
cells = []
cells.append(nbf.v4.new_markdown_cell('# 1. Configuración base'))
cells.append(nbf.v4.new_code_cell('''import sys
from pathlib import Path

# Funciona desde la ra?z del taller, la del proyecto o notebooks/.
carpeta = Path.cwd().resolve()
raiz = next((p for base in (carpeta, *carpeta.parents)
             for p in (base, base / "agente-viajes-a2a")
             if (p / "notebook_runtime.py").is_file()), None)
if raiz is None:
    raise RuntimeError("Abre el notebook dentro de la carpeta del proyecto.")
if str(raiz) not in sys.path:
    sys.path.insert(0, str(raiz))
from notebook_runtime import asegurar_servidor
A2A_URL = asegurar_servidor()
print(f"Servidor disponible: {A2A_URL}")
import os, uuid
A2A_VIAJES_URL = A2A_URL
A2A_VIAJES_GRAPH = os.environ["A2A_VIAJES_GRAPH"]
print(A2A_VIAJES_URL, A2A_VIAJES_GRAPH)'''))
cells.append(nbf.v4.new_code_cell('''import httpx
r = httpx.post(f"{A2A_VIAJES_URL}/assistants/search", json={"graph_id": A2A_VIAJES_GRAPH}, timeout=10)
r.raise_for_status()
data = r.json()
assistants = data if isinstance(data, list) else data.get("assistants", [])
if not assistants:
    raise RuntimeError("No hay asistentes para el grafo configurado.")
assistant_id = assistants[0]["assistant_id"]
print(assistant_id)'''))
cells.append(nbf.v4.new_code_cell('''import httpx
card = httpx.get(f"{A2A_VIAJES_URL}/.well-known/agent-card.json?assistant_id={assistant_id}", timeout=10).json()
print(card["name"], card["url"])'''))
cells.append(nbf.v4.new_code_cell('''import uuid, httpx
context_id = str(uuid.uuid4())
body = {"jsonrpc":"2.0","id":"1","method":"message/send","params":{"message":{"role":"user","messageId":uuid.uuid4().hex,"contextId":context_id,"parts":[{"kind":"text","text":"Quiero un vuelo de Santiago a Lima el 2026-11-10"}]}}}
resp = httpx.post(f"{A2A_VIAJES_URL}/a2a/{assistant_id}", json=body, timeout=90).json()
print(resp["result"]["status"]["state"], context_id)'''))
cells.append(nbf.v4.new_markdown_cell('# 2. Agentes'))
cells.append(nbf.v4.new_code_cell('''from src.consumidor.graph import graph, precio_btc, iniciar_conversacion
from src.consumidor.prompts import SYSTEM_CONVERSACIONAL
print(graph.name); print(bool(SYSTEM_CONVERSACIONAL)); print(precio_btc.invoke({}))'''))
cells.append(nbf.v4.new_markdown_cell('# 3. Consumo'))
cells.append(nbf.v4.new_code_cell('''from langchain_core.messages import HumanMessage
cid = iniciar_conversacion()
config = {"configurable": {"thread_id": "nb-demo-consumidor"}}
def texto(msg):
    c = msg.content
    return c if isinstance(c, str) else " ".join(p.get("text","") for p in c if isinstance(p,dict))
r = await graph.ainvoke({"messages": [HumanMessage(content="Quiero un vuelo de Santiago a Lima el 2026-11-10")]}, config)
print(texto(r["messages"][-1]))'''))
cells.append(nbf.v4.new_code_cell('''r = await graph.ainvoke({"messages": [HumanMessage(content="¿Y cuánto está el precio de BTC?")]}, config)
print(texto(r["messages"][-1]))'''))
cells.append(nbf.v4.new_code_cell('''r = await graph.ainvoke({"messages": [HumanMessage(content="¿Cuánto salía el vuelo que me buscaste?")]}, config)
print(texto(r["messages"][-1]))'''))
nb.cells = cells
out = os.path.join(os.path.dirname(__file__), "agente-conversacional.ipynb")
with open(out, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("ok")
