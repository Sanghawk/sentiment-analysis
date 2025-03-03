# tests/test_articles.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_articles():
    response = client.get("/articles/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
