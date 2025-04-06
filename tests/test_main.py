from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/healthchecker")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI with SQLAlchemy"}
    assert response.json() == {"message": "Welcome to FastAPI with SQLAlchemy"}
