# A2A_MK

Proyecto del agente de inteligencia artificial con arquitectura A2A.

La implementación se encuentra en [`mi-agente/`](mi-agente/). Consulta
[`mi-agente/README.md`](mi-agente/README.md) para instalación, ejecución de
FastAPI, Swagger, pruebas y configuración del agente existente.

Para comenzar en Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy mi-agente\.env.example mi-agente\.env
uvicorn app.main:app --app-dir mi-agente --reload --host 127.0.0.1 --port 8000
```
