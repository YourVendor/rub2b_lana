# backend/tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

def test_login():
    response = client.post("/login", json={"login": "germush", "password": "Gremushka27112007"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_admin_structure():
    response = client.post("/login", json={"login": "germush", "password": "Gremushka27112007"})
    token = response.json()["access_token"]
    response = client.get("/admin/structure", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "tables" in response.json()