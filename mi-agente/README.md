# Agente de soluciones comerciales y marketing

Este proyecto conserva el agente LangGraph existente y agrega una API FastAPI
protegida para consultarlo localmente. El agente usa la herramienta de apuntes
que ya estaba implementada y puede exponerse también mediante A2A con
`langgraph dev`.

La opción elegida para la entrega es **Servicio FastAPI protegido**. En modo
`a2a`, el recorrido es FastAPI → cliente A2A → servidor LangGraph → agente
existente. Las evidencias y su plantilla están en `docs/EVIDENCIAS.md`.

## Requisitos

- Windows 10/11 o Linux/macOS.
- Python 3.11 o superior.
- Una clave válida de Google Gemini (`GOOGLE_API_KEY`) para ejecutar consultas reales.

## Instalación en Windows PowerShell

Ejecuta los comandos desde la carpeta `mi-agente`:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` y reemplaza los valores ficticios. Nunca compartas ese archivo.

El proyecto queda configurado para utilizar `gemini-3.5-flash-lite`. Debes
proporcionar una clave válida en `MODEL_API_KEY` o `GOOGLE_API_KEY`.

## Variables de entorno

| Variable | Uso |
|---|---|
| `GOOGLE_API_KEY` | Clave del proveedor Gemini para el agente existente. |
| `MODEL_API_KEY` | Alias documentado para futuras integraciones de modelo. |
| `AGENT_ACCESS_TOKEN` | Token requerido por `POST /chat`. |
| `AGENT_EXECUTION_MODE` | `a2a` para usar el agente por A2A; `direct` para una prueba local directa. |
| `MODEL_NAME` | Modelo Gemini configurado: `gemini-3.5-flash-lite`. |
| `HOST` | Host local; por defecto `127.0.0.1`. |
| `PORT` | Puerto HTTP; por defecto `8000`. |
| `A2A_VIAJES_URL` | URL del servidor LangGraph usado por el consumidor A2A. |
| `A2A_VIAJES_GRAPH` | Grafo remoto, normalmente `agente_soluciones_comerciales_marketing`. |

## Iniciar la API FastAPI

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

La documentación interactiva está disponible en:

- Swagger: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- Estado: <http://127.0.0.1:8000/health>

En Swagger pulsa **Authorize**, escribe `Bearer` seguido del valor de
`AGENT_ACCESS_TOKEN`, y prueba `POST /chat` con:

```json
{
  "message": "Explica los criterios para evaluar una propuesta de valor"
}
```

La respuesta exitosa contiene `success`, la respuesta real del agente y un
`request_id`. Sin token o con un token incorrecto se obtiene HTTP 401.

También puedes probar desde PowerShell:

```powershell
curl.exe -X POST http://127.0.0.1:8000/chat `
  -H "Authorization: Bearer colocar_token_de_prueba" `
  -H "Content-Type: application/json" `
  -d '{"message":"Explica la propuesta de valor"}'
```

## Ejecutar el servidor A2A original

La API anterior no reemplaza el servidor A2A existente. Para levantarlo:

```powershell
langgraph dev
```

Ese servidor usa `langgraph.json` y expone el grafo mediante la tarjeta A2A y
`/a2a/{assistant_id}`. El agente remoto requiere que `A2A_VIAJES_URL` y
`A2A_VIAJES_GRAPH` estén configurados.

## Pruebas

```powershell
pytest -q
```

Las pruebas de FastAPI validan salud, autorización, mensaje vacío, respuesta
autorizada y errores controlados. Las pruebas A2A se omiten automáticamente si
`langgraph dev` no está ejecutándose. La consulta real requiere una clave del
proveedor y servicios disponibles.

## Detener el servidor

En la terminal donde está ejecutándose, pulsa `Ctrl+C`.

## Servicios externos y limitaciones

- Las respuestas del modelo dependen de Google Gemini y de su disponibilidad.
- La herramienta `consultar_mis_apuntes` usa los apuntes locales existentes; no
  consulta internet.
- El flujo A2A depende del servidor local de LangGraph y de sus URLs configuradas.
- No se despliega en Heroku todavía.
- El caso de marketing incluido en los apuntes es ficticio e ilustrativo.

## Seguridad

No subas ni compartas `.env`, claves API, tokens, contraseñas, sesiones,
capturas que contengan secretos ni el contenido de credenciales. `.gitignore`
excluye estos archivos y directorios.

## Preparación para Heroku

El proyecto incluye `requirements.txt` y `Procfile`. El proceso web escucha en
`0.0.0.0` y usa la variable `PORT` cuando se ejecute en producción. Las
credenciales deberán configurarse como variables del entorno de Heroku; no se
incluyen en el repositorio.
