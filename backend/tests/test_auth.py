import pytest
import io
import pandas as pd

def test_login_success(client, setup_data, db):
    response = client.post("/login", json={"login": "germush", "password": "Gremushka27112007"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid(client):
    response = client.post("/login", json={"login": "germush", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверный логин или пароль"

def test_dashboard_access(client, setup_data):
    response = client.post("/login", json={"login": "germush", "password": "Gremushka27112007"})
    token = response.json()["access_token"]
    response = client.get("/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Привет, брат! Ты в дашборде"