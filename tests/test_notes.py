import uuid
from typing import Any, Dict, Generator

import pytest
from app.config.database import get_db
from app.helpers.enum import NoteCategory
from app.main import app
from app.schemas.notes import NoteBaseSchema
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """
    Crea una sesión de base de datos para pruebas y la cierra al finalizar.
    Cada prueba se ejecuta en una transacción que se revierte al finalizar.
    """

    # Sobrescribe la dependencia de base de datos
    def override_get_db() -> Generator[Session, None, None]:
        from app.config.database import SessionLocal

        db = SessionLocal()
        try:
            db.begin_nested()  # Inicia una transacción con savepoint
            yield db
        finally:
            db.rollback()  # Revierte cualquier cambio
            db.close()

    # Reemplaza la dependencia original con nuestra versión de prueba
    app.dependency_overrides[get_db] = override_get_db

    # Obtiene una sesión usando nuestra función sobrescrita
    db = next(override_get_db())
    yield db

    # Limpia las sobrescrituras después de la prueba
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    """Devuelve un cliente de prueba para la aplicación."""
    return TestClient(app)


@pytest.fixture
def test_note() -> NoteBaseSchema:
    """Crea una instancia de nota para pruebas."""
    return NoteBaseSchema(
        id=str(uuid.uuid4()),
        title="Nota de prueba",
        content="Contenido de prueba",
        category=NoteCategory.STICK,
        published=False,
    )


@pytest.fixture
def created_note(
    client: TestClient, test_note: NoteBaseSchema, db_session: Session
) -> Dict[str, Any]:
    """Crea una nota a través de la API y la devuelve."""
    payload = jsonable_encoder(test_note)
    response = client.post("/api/v1/notes", json=payload)
    assert (
        response.status_code == 200
    ), f"Error al crear nota para test: {response.text}"
    data: Dict[str, Any] = response.json()["data"]
    return data


def test_create_note(client: TestClient, test_note: NoteBaseSchema) -> None:
    """Prueba la creación de una nota."""
    payload = jsonable_encoder(test_note)
    response = client.post("/api/v1/notes", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["title"] == test_note.title
    assert data["data"]["content"] == test_note.content
    assert data["data"]["category"] == test_note.category
    assert data["data"]["published"] == test_note.published


def test_create_note_with_invalid_category(
    client: TestClient, test_note: NoteBaseSchema
) -> None:
    """Prueba la validación al crear una nota con una categoría inválida."""
    payload = jsonable_encoder(test_note)
    payload["category"] = "categoria_invalida"
    response = client.post("/api/v1/notes", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_update_note(
    client: TestClient, created_note: Dict[str, Any], test_note: NoteBaseSchema
) -> None:
    """Prueba la actualización de una nota."""
    # Modificar el contenido de la nota
    update_data = jsonable_encoder(test_note)
    update_data["content"] = "Contenido actualizado"

    # Enviar solicitud de actualización
    note_id = created_note["id"]
    response = client.put(f"/api/v1/notes/{note_id}", json=update_data)

    # Verificar la respuesta
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["content"] == "Contenido actualizado"


def test_show_note(client: TestClient, created_note: Dict[str, Any]) -> None:
    """Prueba la obtención de una nota específica."""
    note_id = created_note["id"]
    response = client.get(f"/api/v1/notes/show/{note_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["id"] == note_id
    assert data["data"]["title"] == created_note["title"]


def test_get_all_notes(client: TestClient, created_note: Dict[str, Any]) -> None:
    """Prueba la obtención de todas las notas."""
    response = client.get("/api/v1/notes/")
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["total_items"] > 0


def test_search_notes(client: TestClient, created_note: Dict[str, Any]) -> None:
    """Prueba la búsqueda de notas por texto."""
    # Buscar por título existente
    search_term = created_note["title"][:10]  # Usar parte del título
    response = client.get(f"/api/v1/notes/search/{search_term}")
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["total_items"] > 0

    # Buscar por texto que no existe
    response = client.get("/api/v1/notes/search/texto_inexistente_12345")
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["total_items"] == 0


def test_delete_note(client: TestClient, created_note: Dict[str, Any]) -> None:
    """Prueba la eliminación de una nota."""
    note_id = created_note["id"]

    # Eliminar la nota
    response = client.delete(f"/api/v1/notes/{note_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Resource was deleted"

    # Verificar que la nota ya no existe
    response = client.get(f"/api/v1/notes/show/{note_id}")
    assert response.status_code == 404
    assert response.status_code == 404
