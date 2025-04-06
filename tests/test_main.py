# tests/test_main.py
# (Se elimina la aserción redundante)
from fastapi import status  # Importar status
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/healthchecker")
    assert response.status_code == status.HTTP_200_OK  # Usar status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to FastAPI with SQLAlchemy"}
