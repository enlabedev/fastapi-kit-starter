import uuid
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from app.schemas.notes import NoteBaseSchema
from app.main import app

client = TestClient(app)


class TestNotes:
    notes = NoteBaseSchema(
        id=str(uuid.uuid4()),
        title="Nuevo contenido",
        content="Despliegues para ramas",
        category="stick",
        published=False,
    )

    def test_create_note(self):
        json = jsonable_encoder(self.notes)
        response = client.post("/api/v1/notes", json=json)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == self.notes.title

    def test_create_note_duplicate(self):
        json = jsonable_encoder(self.notes)
        response = client.post("/api/v1/notes", json=json)
        assert response.status_code == 422

    def test_create_note_with_big_category(self):
        json = jsonable_encoder(self.notes)
        json["id"] = str(uuid.uuid4())
        json["category"] = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            + "Cras consectetur finibus libero vitae viverra"
        )
        response = client.post("/api/v1/notes", json=json)
        assert response.status_code == 422

    def test_update_note(self):
        json = jsonable_encoder(self.notes)
        json["content"] = "Despliegues para 2 ramas"
        response = client.put(f"/api/v1/notes/{json['id']}", json=json)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["content"] == json["content"]

    def test_show_note(self):
        json = jsonable_encoder(self.notes)
        response = client.get(f"/api/v1/notes/show/{json['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == json["title"]

    def test_get_all_note(self):
        response = client.get("/api/v1/notes/")
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["total_items"] > 0

    def test_search_text_nuevo_int_notes(self):
        response = client.get("/api/v1/notes/search/Nuevo contenido")
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["total_items"] > 0

    def test_search_text_sin_int_notes(self):
        response = client.get("/api/v1/notes/search/sin")
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["total_items"] == 0

    def test_delete_note(self):
        json = jsonable_encoder(self.notes)
        response = client.delete(f"/api/v1/notes/{json['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Resource was deleted"
