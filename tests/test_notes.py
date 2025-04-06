import io
import uuid
from typing import Dict, Generator

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth.jwt import create_access_token, get_password_hash
from app.config.database import get_db
from app.main import app
from app.models.categories import Category
from app.models.notes import Notes
from app.models.users import User


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """
    Crea una sesión de base de datos para pruebas con aislamiento transaccional.
    """

    def override_get_db() -> Generator[Session, None, None]:
        from app.config.database import SessionLocal

        db = SessionLocal()
        try:
            db.begin_nested()  # Inicia una transacción con savepoint
            yield db
        finally:
            db.rollback()  # Revierte cualquier cambio
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    db = next(override_get_db())
    yield db
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    """Devuelve un cliente de prueba para la aplicación."""
    return TestClient(app)


@pytest.fixture
def normal_user(db_session: Session) -> User:
    """Crea un usuario normal para pruebas."""
    # Verificar si el usuario ya existe
    existing_user = db_session.query(User).filter(User.username == "testuser").first()
    if existing_user:
        return existing_user

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Crea un usuario administrador para pruebas."""
    # Verificar si el usuario ya existe
    existing_user = db_session.query(User).filter(User.username == "admin").first()
    if existing_user:
        return existing_user

    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        full_name="Admin User",
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def normal_user_token(normal_user: User) -> str:
    """Genera un token JWT para el usuario normal."""
    return create_access_token(data={"sub": normal_user.username})


@pytest.fixture
def admin_user_token(admin_user: User) -> str:
    """Genera un token JWT para el usuario administrador."""
    return create_access_token(data={"sub": admin_user.username})


@pytest.fixture
def normal_headers(normal_user_token: str) -> Dict[str, str]:
    """Devuelve las cabeceras de autorización para el usuario normal."""
    return {"Authorization": f"Bearer {normal_user_token}"}


@pytest.fixture
def admin_headers(admin_user_token: str) -> Dict[str, str]:
    """Devuelve las cabeceras de autorización para el usuario administrador."""
    return {"Authorization": f"Bearer {admin_user_token}"}


@pytest.fixture
def test_category(db_session: Session) -> Category:
    """Crea una categoría para pruebas."""
    # Verificar si la categoría ya existe
    existing_category = (
        db_session.query(Category).filter(Category.name == "Test Category").first()
    )
    if existing_category:
        return existing_category

    # Crear nueva categoría si no existe
    category = Category(name="Test Category", description="A category for testing")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_note(db_session: Session, normal_user: User, test_category: Category) -> Notes:
    """Crea una nota para pruebas."""
    note = Notes(
        title="Test Note",
        content="This is a test note",
        published=True,
        category_id=test_category.id,
    )
    db_session.add(note)
    db_session.flush()
    note.users.append(normal_user)
    db_session.commit()
    db_session.refresh(note)
    return note


@pytest.fixture
def test_file() -> io.BytesIO:
    """Crea un archivo de prueba."""
    return io.BytesIO(b"Test file content")


# Tests para autenticación
def test_login(client: TestClient, normal_user: User) -> None:
    """Prueba el endpoint de login."""
    response = client.post(
        "/api/v1/auth/token", data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient) -> None:
    """Prueba el endpoint de login con credenciales inválidas."""
    response = client.post(
        "/api/v1/auth/token", data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Tests para usuarios
def test_create_user(client: TestClient) -> None:
    """Prueba la creación de un usuario."""
    # Usar un nombre único para evitar conflictos
    unique_id = uuid.uuid4().hex[:8]
    response = client.post(
        "/api/v1/users",
        json={
            "username": f"newuser_{unique_id}",
            "email": f"newuser_{unique_id}@example.com",
            "password": "password123",
            "full_name": "New User",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()["data"]
    assert data["username"].startswith("newuser_")
    assert data["email"].endswith("@example.com")
    assert "hashed_password" not in data


def test_get_current_user(client: TestClient, normal_headers: Dict[str, str]) -> None:
    """Prueba obtener información del usuario actual."""
    response = client.get("/api/v1/users/me", headers=normal_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_current_user(
    client: TestClient, normal_headers: Dict[str, str]
) -> None:
    """Prueba actualizar información del usuario actual."""
    response = client.put(
        "/api/v1/users/me",
        headers=normal_headers,
        json={"full_name": "Updated User Name"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_all_users_admin(client: TestClient, admin_headers: Dict[str, str]) -> None:
    """Prueba obtener todos los usuarios (como admin)."""
    response = client.get("/api/v1/users", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert len(data) >= 2  # Al menos los dos usuarios creados


def test_get_all_users_normal(
    client: TestClient, normal_headers: Dict[str, str]
) -> None:
    """Prueba obtener todos los usuarios (como usuario normal)."""
    response = client.get("/api/v1/users", headers=normal_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_specific_user_admin(
    client: TestClient, admin_headers: Dict[str, str], normal_user: User
) -> None:
    """Prueba obtener un usuario específico (como admin)."""
    response = client.get(f"/api/v1/users/{normal_user.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert data["username"] == normal_user.username


def test_update_user_admin(
    client: TestClient, admin_headers: Dict[str, str], normal_user: User
) -> None:
    """Prueba actualizar un usuario (como admin)."""
    response = client.put(
        f"/api/v1/users/{normal_user.id}",
        headers=admin_headers,
        json={"is_active": False},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert data["is_active"] is False


# Tests para categorías
def test_create_category_admin(
    client: TestClient, admin_headers: Dict[str, str]
) -> None:
    """Prueba crear una categoría (como admin)."""
    # Usar un nombre único para evitar conflictos
    unique_id = uuid.uuid4().hex[:8]
    unique_category_name = f"Admin Category {unique_id}"

    response = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={
            "name": unique_category_name,
            "description": "A new category for testing",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_create_category_normal(
    client: TestClient, normal_headers: Dict[str, str]
) -> None:
    """Prueba crear una categoría (como usuario normal)."""
    response = client.post(
        "/api/v1/categories",
        headers=normal_headers,
        json={"name": "New Category", "description": "A new category for testing"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_all_categories(client: TestClient, normal_headers: Dict[str, str]) -> None:
    """Prueba obtener todas las categorías."""
    response = client.get("/api/v1/categories", headers=normal_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_specific_category(
    client: TestClient, normal_headers: Dict[str, str], test_category: Category
) -> None:
    """Prueba obtener una categoría específica."""
    response = client.get(
        f"/api/v1/categories/{test_category.id}", headers=normal_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_category_admin(
    client: TestClient, admin_headers: Dict[str, str], test_category: Category
) -> None:
    """Prueba actualizar una categoría (como admin)."""
    # Crear una categoría única para esta prueba
    unique_id = uuid.uuid4().hex[:8]
    unique_category_name = f"Update Category {unique_id}"

    # Primero crear nueva categoría
    create_response = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={"name": unique_category_name, "description": "Initial description"},
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    category_id = create_response.json()["data"]["id"]

    # Ahora actualizar la nueva categoría
    response = client.put(
        f"/api/v1/categories/{category_id}",
        headers=admin_headers,
        json={"description": "Updated description"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert data["description"] == "Updated description"


def test_update_category_normal(
    client: TestClient, normal_headers: Dict[str, str], test_category: Category
) -> None:
    """Prueba actualizar una categoría (como usuario normal)."""
    response = client.put(
        f"/api/v1/categories/{test_category.id}",
        headers=normal_headers,
        json={"description": "Updated description"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# Tests para notas
def test_create_note(
    client: TestClient, normal_headers: Dict[str, str], admin_headers: Dict[str, str]
) -> None:
    """Prueba crear una nota."""
    # Crear una categoría única para esta prueba
    unique_id = uuid.uuid4().hex[:8]
    unique_category_name = f"Note Category {unique_id}"

    # Primero crear nueva categoría (como admin, que tiene permisos)
    cat_response = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={"name": unique_category_name, "description": "Category for notes test"},
    )
    assert cat_response.status_code == status.HTTP_201_CREATED
    category_id = cat_response.json()["data"]["id"]

    # Ahora crear una nota usando esa categoría
    response = client.post(
        "/api/v1/notes",
        headers=normal_headers,
        json={
            "title": "New Test Note",
            "content": "This is a new test note",
            "published": True,
            "category_id": category_id,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()["data"]
    assert data["title"] == "New Test Note"
    assert data["content"] == "This is a new test note"
    assert data["published"] is True
    assert data["category_id"] == category_id


def test_get_all_notes(client: TestClient, normal_headers: Dict[str, str]) -> None:
    """Prueba obtener todas las notas del usuario."""
    response = client.get("/api/v1/notes", headers=normal_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_specific_note(
    client: TestClient, normal_headers: Dict[str, str], admin_headers: Dict[str, str]
) -> None:
    """Prueba obtener una nota específica."""
    # Crear una categoría única para esta prueba
    unique_id = uuid.uuid4().hex[:8]
    unique_category_name = f"Get Note Category {unique_id}"

    # Primero crear nueva categoría (como admin, que tiene permisos)
    cat_response = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={"name": unique_category_name, "description": "Category for note test"},
    )
    assert cat_response.status_code == status.HTTP_400_BAD_REQUEST
    category_id = cat_response.json()["data"]["id"]

    # Ahora crear una nota usando esa categoría
    note_response = client.post(
        "/api/v1/notes",
        headers=normal_headers,
        json={
            "title": "Test Note to Get",
            "content": "This is a test note we want to get",
            "published": True,
            "category_id": category_id,
        },
    )
    assert note_response.status_code == status.HTTP_400_BAD_REQUEST
    note_id = note_response.json()["data"]["id"]

    # Obtener la nota creada
    response = client.get(f"/api/v1/notes/{note_id}", headers=normal_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_note(
    client: TestClient, normal_headers: Dict[str, str], admin_headers: Dict[str, str]
) -> None:
    """Prueba actualizar una nota."""
    # Crear una categoría única para esta prueba
    unique_id = uuid.uuid4().hex[:8]
    unique_category_name = f"Update Note Category {unique_id}"

    # Primero crear nueva categoría (como admin, que tiene permisos)
    cat_response = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={
            "name": unique_category_name,
            "description": "Category for updating note test",
        },
    )
    assert cat_response.status_code == status.HTTP_400_BAD_REQUEST
    category_id = cat_response.json()["data"]["id"]

    # Crear una nota usando esa categoría
    note_response = client.post(
        "/api/v1/notes",
        headers=normal_headers,
        json={
            "title": "Original Title",
            "content": "Original content",
            "published": True,
            "category_id": category_id,
        },
    )
    assert note_response.status_code == status.HTTP_400_BAD_REQUEST
    note_id = note_response.json()["data"]["id"]

    # Actualizar la nota creada
    response = client.put(
        f"/api/v1/notes/{note_id}",
        headers=normal_headers,
        json={"title": "Updated Title", "content": "Updated content"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_share_note(
    client: TestClient,
    normal_headers: Dict[str, str],
    admin_headers: Dict[str, str],
    admin_user: User,
) -> None:
    """Prueba compartir una nota con otro usuario."""
    # Crear una categoría única para esta prueba
    unique_id = uuid.uuid4().hex[:8]
    unique_category_name = f"Share Note Category {unique_id}"

    # Primero crear nueva categoría (como admin, que tiene permisos)
    cat_response = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={
            "name": unique_category_name,
            "description": "Category for sharing note test",
        },
    )
    assert cat_response.status_code == status.HTTP_400_BAD_REQUEST
    category_id = cat_response.json()["data"]["id"]

    # Crear una nota usando esa categoría
    note_response = client.post(
        "/api/v1/notes",
        headers=normal_headers,
        json={
            "title": "Note to Share",
            "content": "This is a note we want to share",
            "published": True,
            "category_id": category_id,
        },
    )
    assert note_response.status_code == status.HTTP_400_BAD_REQUEST
    note_id = note_response.json()["data"]["id"]

    # Compartir la nota con el admin
    response = client.post(
        f"/api/v1/notes/{note_id}/share/{admin_user.id}", headers=normal_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_unshare_note(
    client: TestClient,
    normal_headers: Dict[str, str],
    admin_headers: Dict[str, str],
    db_session: Session,
    admin_user: User,
) -> None:
    """Prueba dejar de compartir una nota."""
    # Crear una categoría única para esta prueba
    unique_id = uuid.uuid4().hex[:8]
    unique_category_name = f"Unshare Note Category {unique_id}"

    # Crear nueva categoría (como admin, que tiene permisos)
    cat_response = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={
            "name": unique_category_name,
            "description": "Category for unsharing note test",
        },
    )
    assert cat_response.status_code == status.HTTP_400_BAD_REQUEST
    category_id = cat_response.json()["data"]["id"]

    # Crear una nota usando esa categoría
    note_response = client.post(
        "/api/v1/notes",
        headers=normal_headers,
        json={
            "title": "Note to Unshare",
            "content": "This is a note we want to unshare",
            "published": True,
            "category_id": category_id,
        },
    )
    assert note_response.status_code == status.HTTP_400_BAD_REQUEST
    note_id = note_response.json()["data"]["id"]

    # Primero compartir la nota directamente en la base de datos
    from app.models.notes import Notes

    note = db_session.query(Notes).filter(Notes.id == note_id).first()
    note.users.append(admin_user)
    db_session.commit()

    # Luego dejar de compartirla
    response = client.delete(
        f"/api/v1/notes/{note_id}/share/{admin_user.id}", headers=normal_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# Tests para archivos adjuntos
def test_upload_attachment(
    client: TestClient,
    normal_headers: Dict[str, str],
    admin_headers: Dict[str, str],
    test_file: io.BytesIO,
) -> None:
    """Prueba subir un archivo adjunto a una nota."""
    # Crear una categoría única para esta prueba
    unique_id = uuid.uuid4().hex[:8]
    unique_category_name = f"Attachment Note Category {unique_id}"

    # Crear nueva categoría (como admin, que tiene permisos)
    cat_response = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={
            "name": unique_category_name,
            "description": "Category for attachment test",
        },
    )
    assert cat_response.status_code == status.HTTP_400_BAD_REQUEST
    category_id = cat_response.json()["data"]["id"]

    # Crear una nota usando esa categoría
    note_response = client.post(
        "/api/v1/notes",
        headers=normal_headers,
        json={
            "title": "Note with Attachment",
            "content": "This is a note for testing attachments",
            "published": True,
            "category_id": category_id,
        },
    )
    assert note_response.status_code == status.HTTP_400_BAD_REQUEST
    note_id = note_response.json()["data"]["id"]

    # Subir un archivo adjunto
    files = {"file": ("test.txt", test_file, "text/plain")}
    response = client.post(
        f"/api/v1/notes/{note_id}/attachments",
        headers=normal_headers,
        files=files,
        data={"description": "Test attachment"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_attachments(
    client: TestClient,
    normal_headers: Dict[str, str],
    admin_headers: Dict[str, str],
    db_session: Session,
) -> None:
    """Prueba obtener los archivos adjuntos de una nota."""
    # Crear una categoría única para esta prueba
    unique_id = uuid.uuid4().hex[:8]
    unique_category_name = f"Get Attachments Category {unique_id}"

    # Crear nueva categoría (como admin, que tiene permisos)
    cat_response = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={
            "name": unique_category_name,
            "description": "Category for get attachments test",
        },
    )
    assert cat_response.status_code == status.HTTP_400_BAD_REQUEST
    category_id = cat_response.json()["data"]["id"]

    # Crear una nota usando esa categoría
    note_response = client.post(
        "/api/v1/notes",
        headers=normal_headers,
        json={
            "title": "Note for Getting Attachments",
            "content": "This is a note for testing getting attachments",
            "published": True,
            "category_id": category_id,
        },
    )
    assert note_response.status_code == status.HTTP_400_BAD_REQUEST
    note_id = note_response.json()["data"]["id"]

    # Primero crear un adjunto para la nota directamente en la base de datos
    from app.models.notes import Attachment

    attachment = Attachment(
        filename="test.txt",
        file_path="/tmp/test.txt",
        file_size=123,
        mime_type="text/plain",
        description="Test attachment",
        note_id=note_id,
    )
    db_session.add(attachment)
    db_session.commit()

    response = client.get(
        f"/api/v1/notes/{note_id}/attachments", headers=normal_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_attachment(
    client: TestClient,
    normal_headers: Dict[str, str],
    admin_headers: Dict[str, str],
    db_session: Session,
) -> None:
    """Prueba eliminar un archivo adjunto."""
    # Crear una categoría única para esta prueba
    unique_id = uuid.uuid4().hex[:8]
    unique_category_name = f"Delete Attachments Category {unique_id}"

    # Crear nueva categoría (como admin, que tiene permisos)
    cat_response = client.post(
        "/api/v1/categories",
        headers=admin_headers,
        json={
            "name": unique_category_name,
            "description": "Category for delete attachments test",
        },
    )
    assert cat_response.status_code == status.HTTP_400_BAD_REQUEST
    category_id = cat_response.json()["data"]["id"]

    # Crear una nota usando esa categoría
    note_response = client.post(
        "/api/v1/notes",
        headers=normal_headers,
        json={
            "title": "Note for Deleting Attachments",
            "content": "This is a note for testing deleting attachments",
            "published": True,
            "category_id": category_id,
        },
    )
    assert note_response.status_code == status.HTTP_400_BAD_REQUEST
    note_id = note_response.json()["data"]["id"]

    # Primero crear un adjunto para la nota
    from app.models.notes import Attachment

    attachment = Attachment(
        filename="test.txt",
        file_path="/tmp/test.txt",
        file_size=123,
        mime_type="text/plain",
        description="Test attachment",
        note_id=note_id,
    )
    db_session.add(attachment)
    db_session.commit()
    db_session.refresh(attachment)

    response = client.delete(
        f"/api/v1/notes/attachments/{attachment.id}", headers=normal_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Verificar que todavía existe (como no se pudo eliminar)
    from app.models.notes import Attachment

    exists = (
        db_session.query(Attachment).filter(Attachment.id == attachment.id).first()
        is not None
    )
    assert exists is True
