# Evidencia 01 — Consulta autorizada

## Entorno y fecha

- Entorno: LOCAL.
- Fecha de ejecución: 15 de noviembre de 2026.
- Canal: Swagger UI de FastAPI.
- URL: `http://127.0.0.1:8000/docs`.

## Solicitud

```json
{
  "message": "Explica qué es una propuesta de valor y cómo se evalúa"
}
```

La solicitud se ejecutó con autorización Bearer configurada en Swagger. El
token no se registra en este documento.

## Resultado esperado

La API debía validar el token, enviar la consulta al agente existente mediante
el flujo A2A local y devolver una respuesta real con `success`, `response` y
`request_id`.

## Resultado obtenido

- FastAPI estaba activo en `127.0.0.1:8000`.
- El servidor A2A de LangGraph estaba activo en el puerto `2024`.
- El registro de Uvicorn mostró:

  ```text
  POST /chat HTTP/1.1 200 OK
  ```

- Swagger mostró la solicitud y la respuesta de la API.
- La respuesta fue producida por el flujo configurado, no por una respuesta
  fija del endpoint.

## Observaciones

- Las solicitudes `GET /v1/models` con HTTP 404 no corresponden a un endpoint
  de este proyecto y no afectan el flujo `/chat`.
- La captura visual debe guardarse junto a este archivo con el nombre
  `01-consulta-autorizada.png`, ocultando el token.
- No se registran claves API, tokens ni datos personales.
