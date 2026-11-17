import os
import uuid

from fastapi.testclient import TestClient

os.environ["AGENT_ACCESS_TOKEN"] = "test-token"

from app.main import app  # noqa: E402
import app.main as main  # noqa: E402


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_salud():
    response = client.get("/salud")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_agent_card():
    response = client.get("/.well-known/agent-card.json")
    body = response.json()
    assert response.status_code == 200
    assert body["url"].endswith("/message/send")
    assert body["skills"]


def test_message_send_without_token():
    payload = {"jsonrpc": "2.0", "id": "1", "method": "message/send", "params": {}}
    response = client.post("/message/send", json=payload)
    assert response.status_code == 401


def test_message_send(monkeypatch):
    async def fake_agent(message: str, request_id: str | None = None) -> str:
        assert message == "consulta A2A"
        assert request_id
        return "respuesta A2A"

    monkeypatch.setattr(main, "consultar_agente", fake_agent)
    context_id = str(uuid.uuid4())
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "messageId": str(uuid.uuid4()),
                "contextId": context_id,
                "parts": [{"kind": "text", "text": "consulta A2A"}],
            }
        },
    }
    response = client.post(
        "/message/send", json=payload, headers={"Authorization": "Bearer test-token"}
    )
    body = response.json()
    assert response.status_code == 200
    assert body["result"]["status"]["state"] == "completed"
    assert body["result"]["status"]["message"]["parts"][0]["text"] == "respuesta A2A"
    assert body["result"]["contextId"] == context_id


def test_web_client():
    response = client.get("/")
    assert response.status_code == 200
    assert "Agente de soluciones" in response.text


def test_chat_without_token():
    response = client.post("/chat", json={"message": "hola"})
    assert response.status_code == 401


def test_chat_with_invalid_token():
    response = client.post(
        "/chat",
        json={"message": "hola"},
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert response.status_code == 401


def test_chat_empty_message():
    response = client.post(
        "/chat",
        json={"message": "   "},
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 422


def test_chat_authorized(monkeypatch):
    async def fake_agent(message: str, request_id: str | None = None) -> str:
        assert message == "consulta real de prueba"
        return "respuesta del agente"

    monkeypatch.setattr(main, "consultar_agente", fake_agent)
    response = client.post(
        "/chat",
        json={"message": "consulta real de prueba"},
        headers={"Authorization": "Bearer test-token"},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["response"] == "respuesta del agente"
    assert body["request_id"]


def test_chat_agent_error(monkeypatch):
    async def failing_agent(message: str, request_id: str | None = None) -> str:
        raise RuntimeError("fallo interno")

    monkeypatch.setattr(main, "consultar_agente", failing_agent)
    response = client.post(
        "/chat",
        json={"message": "consulta"},
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 502
    assert response.json()["detail"] == "El agente no pudo procesar la solicitud."
