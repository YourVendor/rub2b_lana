import pytest
import io
import pandas as pd
from sqlalchemy import inspect

def test_login_success(client, setup_data, db):
    # Проверяем, что таблица users существует
    inspector = inspect(db.get_bind())
    tables = inspector.get_table_names()
    print(f"Tables in test: {tables}")
    assert 'users' in tables, "Table 'users' not found in database"
    
    response = client.post("/login", json={"login": "germush", "password": "Gremushka27112007"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid(client, setup_data, db):
    inspector = inspect(db.get_bind())
    tables = inspector.get_table_names()
    print(f"Tables in test: {tables}")
    assert 'users' in tables, "Table 'users' not found in database"
    
    response = client.post("/login", json={"login": "germush", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверный логин или пароль"

def test_dashboard_access(client, setup_data, db):
    inspector = inspect(db.get_bind())
    tables = inspector.get_table_names()
    print(f"Tables in test: {tables}")
    assert 'users' in tables, "Table 'users' not found in database"
    
    response = client.post("/login", json={"login": "germush", "password": "Gremushka27112007"})
    token = response.json()["access_token"]
    response = client.get("/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Привет, брат! Ты в дашборде"