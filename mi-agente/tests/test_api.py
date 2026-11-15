import os

from fastapi.testclient import TestClient

os.environ["AGENT_ACCESS_TOKEN"] = "test-token"

from app.main import app  # noqa: E402
import app.main as main  # noqa: E402


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


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
