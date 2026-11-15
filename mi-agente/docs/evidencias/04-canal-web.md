# Evidencia 04 — Canal web propio

## Entorno y fecha

- Entorno: LOCAL.
- Fecha de ejecución visual: 15 de noviembre de 2026.
- Canal: frontend web propio.
- URL: `http://127.0.0.1:8000/`.

## Opción implementada

Se agregó una página web propia, distinta de WhatsApp Web, que reutiliza la
API FastAPI protegida. El flujo es:

```text
Página web → POST /chat → cliente A2A → agente existente → respuesta web
```

## Preparación

1. Mantener activo `langgraph dev --port 2024`.
2. Mantener activo FastAPI en el puerto `8000`.
3. Abrir `http://127.0.0.1:8000/`.
4. Introducir el token local en el campo de contraseña sin mostrarlo.

## Solicitud de prueba

Consulta realizada:

```text
Explica qué es un mercado objetivo
```

## Resultado esperado

La página debía enviar la consulta a `/chat`, recibir la respuesta real del
agente y mostrar el estado de la operación junto con el `request_id`.

## Resultado obtenido

La página web mostró `Consulta completada (200)`, un `request_id` y una
respuesta real del agente sobre el mercado objetivo.

## Captura requerida

Guardar como:

```text
04-canal-web.png
```

La imagen debe mostrar la consulta y la respuesta, pero no el token ni las
claves del modelo. Se recomienda recortar el campo de token y cualquier panel
de red del navegador.
