# Evidencia 02 — Acceso rechazado sin token

## Entorno y fecha

- Entorno: LOCAL.
- Fecha de ejecución: 15 de noviembre de 2026.
- Endpoint: `POST http://127.0.0.1:8000/chat`.

## Solicitud

Se envió una consulta válida sin encabezado `Authorization`:

```json
{
  "message": "prueba sin token"
}
```

## Resultado esperado

La API debía rechazar la solicitud antes de ejecutar el agente y responder
HTTP 401.

## Resultado obtenido

La prueba local devolvió:

```text
HTTP 401
{"detail":"Se requiere un token Bearer."}
```

No se ejecutó el agente ni se devolvió una respuesta exitosa.

## Evidencia visual pendiente

En Swagger, pulsar **Authorize → Logout**, ejecutar `POST /chat` y guardar la
captura como `02-acceso-sin-token.png`. La captura no debe mostrar tokens.
