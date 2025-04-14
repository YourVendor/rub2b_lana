import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login():
    response = client.post("/login", json={"login": "vi", "password": "12345"})
    assert response.status_code == 200
    assert "access_token" in response.json()