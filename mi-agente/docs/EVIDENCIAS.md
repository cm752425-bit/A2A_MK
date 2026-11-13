# Evidencias de la entrega local

Este documento debe acompañar las capturas reales de la ejecución. No se deben
incluir claves API, tokens, códigos de vinculación ni datos personales.

## Opción elegida

**Servicio FastAPI protegido**, integrado con el agente LangGraph existente.

El recorrido esperado es:

```text
Solicitud HTTP → FastAPI → cliente A2A → servidor LangGraph → agente existente → respuesta
```

## Preparación local

1. Crear `.venv` e instalar `requirements.txt`.
2. Crear `mi-agente/.env` desde `.env.example`.
3. Configurar una clave propia de Gemini y un `AGENT_ACCESS_TOKEN` de prueba.
4. Iniciar el servidor A2A en una terminal:

   ```powershell
   cd mi-agente
   langgraph dev --port 2024
   ```

5. Iniciar FastAPI en otra terminal desde la raíz:

   ```powershell
   uvicorn app.main:app --app-dir mi-agente --reload --host 127.0.0.1 --port 8000
   ```

## Caso autorizado

- **Entorno y fecha:** LOCAL; completar con la fecha de la captura.
- **Solicitud:** completar con la consulta enviada en Swagger.
- **Resultado esperado:** respuesta real del agente, con datos, unidades,
  condiciones y supuestos conservados.
- **Resultado obtenido:** completar con la respuesta observada.
- **Evidencia:** captura de Swagger y, si corresponde, registro del servidor
  A2A sin mostrar credenciales.

## Caso rechazado

- **Entorno y fecha:** LOCAL; completar con la fecha de la captura.
- **Solicitud:** la misma consulta sin `Authorization` o con un token falso.
- **Resultado esperado:** HTTP 401 y ningún resultado del agente.
- **Resultado obtenido:** completar con el código y mensaje observados.
- **Evidencia:** captura sin mostrar el token real.

## Pruebas automatizadas

Ejecutar desde `mi-agente`:

```powershell
..\.venv\Scripts\python.exe -m pytest -q
```

Las pruebas unitarias de FastAPI validan salud, autorización, mensaje vacío,
respuesta autorizada y error controlado. Las pruebas A2A requieren que
`langgraph dev` esté activo y una credencial de modelo válida.

## Limitaciones declaradas

- La ejecución real requiere acceso a Gemini y conexión de red.
- El modo `a2a` requiere dos procesos locales: LangGraph y FastAPI.
- Las capturas deben ser producidas por el equipo durante una ejecución real;
  este archivo no sustituye esas evidencias.
