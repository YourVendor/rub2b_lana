import pytest
from ..models.query import Query

def test_get_structure(client, setup_data, db):
    response = client.post("/login", json={"login": "germush", "password": "Gremushka27112007"})
    token = response.json()["access_token"]
    response = client.get("/admin/structure", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "tables" in response.json()
    assert "users" in response.json()["tables"]

def test_run_query(client, setup_data, db):
    response = client.post("/login", json={"login": "germush", "password": "Gremushka27112007"})
    token = response.json()["access_token"]
    response = client.post(
        "/admin/query",
        json={"name": "TestQuery", "query_text": "SELECT * FROM users;", "author": "germush", "active": True},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()["result"]) >= 1
    assert response.json()["result"][0]["login"] == "germush"

def test_update_query(client, setup_data, db):
    response = client.post("/login", json={"login": "germush", "password": "Gremushka27112007"})
    token = response.json()["access_token"]
    db_query = Query(name="TestQuery", query_text="SELECT * FROM users;", author="germush", active=True)
    db.add(db_query)
    db.commit()
    response = client.put(
        f"/admin/query/{db_query.id}",
        json={"name": "TestQuery", "query_text": "SELECT login FROM users;", "author": "germush", "active": True},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["result"][0]["login"] == "germush"

def test_get_queries(client, setup_data, db):
    response = client.post("/login", json={"login": "germush", "password": "Gremushka27112007"})
    token = response.json()["access_token"]
    db_query = Query(name="TestQuery", query_text="SELECT * FROM users;", author="germush", active=True)
    db.add(db_query)
    db.commit()
    response = client.get("/admin/queries", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["name"] == "TestQuery"

def test_delete_query(client, setup_data, db):
    response = client.post("/login", json={"login": "germush", "password": "Gremushka27112007"})
    token = response.json()["access_token"]
    db_query = Query(name="TestQuery", query_text="SELECT * FROM users;", author="germush", active=True)
    db.add(db_query)
    db.commit()
    response = client.delete(f"/admin/query/{db_query.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Запрос удалён"