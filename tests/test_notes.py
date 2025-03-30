import uuid
from typing import Any, Dict

from app.main import app
from app.schemas.notes import NoteBaseSchema
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

client = TestClient(app)


class TestNotes:
    def setup_method(self) -> None:
        """Setup class to initialize the test client"""

    def setup_class(self) -> None:
        """Setup method to create a new note before each test"""
        self.note_id = str(uuid.uuid4())
        self.notes = NoteBaseSchema(
            id=self.note_id,
            title="Nuevo contenido",
            content="Despliegues para ramas",
            category="stick",
            published=False,
        )

    def create_note_via_api(self) -> Dict[str, Any]:
        payload = jsonable_encoder(self.notes)
        response = client.post("/api/v1/notes", json=payload)
        assert (
            response.status_code == 200
        ), f"Error al crear nota para test: {response.text}"
        return response.json()  # Ensure response.json() returns Dict[str, Any]

    def test_create_note(self) -> None:
        data = self.create_note_via_api()
        assert data["data"]["title"] == self.notes.title

    def test_create_note_with_big_category(self) -> None:
        self.test_create_note()
        json = jsonable_encoder(self.notes)
        json["category"] = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            + "Cras consectetur finibus libero vitae viverra"
        )
        response = client.post("/api/v1/notes", json=json)
        assert response.status_code == 422

    def test_update_note(self) -> None:
        """Test updating a note"""
        data = self.create_note_via_api()
        note_id = data["data"]["id"]
        json = jsonable_encoder(self.notes)
        json["content"] = "Despliegues para 2 ramas"
        response = client.put(f"/api/v1/notes/{note_id}", json=json)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["content"] == json["content"]

    def test_show_note(self) -> None:
        json = jsonable_encoder(self.notes)
        response = client.get(f"/api/v1/notes/show/{self.note_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == json["title"]

    def test_get_all_note(self) -> None:
        response = client.get("/api/v1/notes/")
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["total_items"] > 0

    def test_search_text_nuevo_int_notes(self) -> None:
        response = client.get("/api/v1/notes/search/Nuevo contenido")
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["total_items"] > 0

    def test_search_text_sin_int_notes(self) -> None:
        response = client.get("/api/v1/notes/search/sin")
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["total_items"] == 0

    def test_delete_note(self) -> None:
        response = client.delete(f"/api/v1/notes/{self.note_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Resource was deleted"
