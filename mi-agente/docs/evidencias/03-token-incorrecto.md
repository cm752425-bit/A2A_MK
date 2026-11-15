# Evidencia 03 — Token incorrecto

## Entorno y fecha

- Entorno: LOCAL.
- Fecha de ejecución: 15 de noviembre de 2026.
- Canal: Swagger UI de FastAPI.
- Endpoint: `POST http://127.0.0.1:8000/chat`.

## Solicitud

Se envió la consulta con un token deliberadamente incorrecto. El valor usado
no se registra en este documento ni en la captura.

```json
{
  "message": "Explica qué es un mercado objetivo"
}
```

## Resultado esperado

La API debía rechazar la solicitud con HTTP 401 sin ejecutar el agente.

## Resultado obtenido

La respuesta observada fue:

```text
HTTP 401 Unauthorized
Token no válido.
```

## Observaciones

- La captura oculta el token enviado.
- No se produjo una respuesta exitosa del agente.
- La captura asociada es `03-token-incorrecto.png`.
