# Entrega — A2A_MK

## Repositorio

<https://github.com/cm752425-bit/A2A_MK>

Rama de entrega: `main`.

## Implementaciones elegidas

1. Servicio FastAPI protegido mediante token Bearer.
2. Canal web propio de chat, distinto de WhatsApp Web.

Ambas implementaciones reutilizan el agente LangGraph existente y su
comunicación A2A local.

## Cómo ejecutar localmente

Desde la raíz del proyecto:

```powershell
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy mi-agente\.env.example mi-agente\.env
```

Completar `mi-agente/.env` con las credenciales propias. Nunca entregar ese
archivo.

Terminal 1:

```powershell
cd mi-agente
..\.venv\Scripts\Activate.ps1
langgraph dev --port 2024
```

Terminal 2:

```powershell
uvicorn app.main:app --app-dir mi-agente --reload --host 127.0.0.1 --port 8000
```

Interfaces:

- Canal web: <http://127.0.0.1:8000/>
- Swagger: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

## Pruebas

Desde `mi-agente`:

```powershell
..\.venv\Scripts\python.exe -m pytest -q
```

Última verificación: `9 passed`.

## Evidencias

Se encuentran en `mi-agente/docs/evidencias/`:

- Consulta autorizada, HTTP 200.
- Solicitud sin token, HTTP 401.
- Token incorrecto, HTTP 401.
- Canal web funcionando, HTTP 200.

Las capturas ocultan tokens y claves.

## Variables sensibles

Las claves de Gemini y el token de acceso se configuran únicamente en
`mi-agente/.env`. El repositorio entrega solo `.env.example` con valores
ficticios. Heroku no es necesario para la entrega base y no se incluyeron
credenciales de despliegue.

## Limitaciones conocidas

- La consulta real requiere conexión a Gemini y una clave válida del proveedor.
- El modo A2A requiere que estén activos los dos procesos locales.
- El contenido de los apuntes del agente es local y el caso de marketing es
  ficticio e ilustrativo.

## Despliegue Heroku opcional

La app Heroku se llama `agente-mk-2026` y usa el modo `direct` en producción,
porque no depende de un proceso `langgraph dev` local. Las variables sensibles
deben configurarse en Heroku como Config Vars; no se guardan en el repositorio.

URL pública:

<https://agente-mk-2026-b4e407e65a92.herokuapp.com/>

Swagger público:

<https://agente-mk-2026-b4e407e65a92.herokuapp.com/docs>

El despliegue fue verificado con HTTP 200 en `/`, `/health` y `/docs`. Para
ejecutar `/chat` aún deben configurarse en Heroku una clave nueva del proveedor
Gemini y un `AGENT_ACCESS_TOKEN` nuevo; esos valores no se incluyen aquí.
