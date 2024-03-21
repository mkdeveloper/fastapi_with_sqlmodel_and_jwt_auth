from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from fastapi_todo_app.main import app, get_db
from fastapi_todo_app import settings, models
from fastapi_todo_app.auth import create_access_token
from datetime import timedelta
import pytest

# Setup the database connection for testing
connection_string = str(settings.TEST_DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)
engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)
SQLModel.metadata.create_all(engine)

# Override the get_db dependency to use the test database


def get_session_override():
    return Session(engine)


app.dependency_overrides[get_db] = get_session_override

client = TestClient(app=app)


@pytest.fixture(scope="module")
def create_user_and_get_token():
    new_user = models.Users(
        username="testuser", hashed_password="testpassword", email="test@example.com")
    with get_session_override() as session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

    access_token = create_access_token(
        username=new_user.username,
        user_id=new_user.id,
        expires_delta=timedelta(minutes=20)
    )
    yield access_token

    with get_session_override() as session:
        session.delete(new_user)
        session.commit()

# Test reading main root


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to MK's Todo App API"}


# Test creating a new todo item
def test_create_todo(create_user_and_get_token):
    token = create_user_and_get_token
    response = client.post(
        "/todos/",
        json={"content": "Test Todo", "completed": False},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Test Todo"

# Test reading all todo items for the current user


def test_read_todos(create_user_and_get_token):
    token = create_user_and_get_token
    response = client.get(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_todo(create_user_and_get_token):
    token = create_user_and_get_token
    get_response = client.get(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 200

    todos = get_response.json()

    todo_to_update = None
    for todo in todos:
        if todo["content"] == "Test Todo":
            todo_to_update = todo
            break

    assert todo_to_update is not None

    update_response = client.put(
        f"/todos/{todo_to_update['id']}",
        json={"content": "Updated Test Todo", "completed": True},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["content"] == "Updated Test Todo"


# Test deleting a specific todo item by ID
def test_delete_todo(create_user_and_get_token):
    token = create_user_and_get_token
    get_response = client.get(
        "/todos/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 200

    todos = get_response.json()

    todo_to_delete = None
    for todo in todos:
        if todo["content"] == "Updated Test Todo":
            todo_to_delete = todo
            break

    assert todo_to_delete is not None

    delete_response = client.delete(
        f"/todos/{todo_to_delete['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 200

    get_response = client.get(
        f"/todos/{todo_to_delete['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404
