from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/")
    assert response.status_code == 200


def test_list_items():
    response = client.get("/items")
    assert response.status_code == 200
    assert "items" in response.json()


def test_get_item():
    response = client.get("/items/1")
    assert response.status_code == 200


def test_get_item_not_found():
    response = client.get("/items/999")
    assert response.status_code == 404


def test_simulate_error():
    response = client.get("/error")
    assert response.status_code == 500
