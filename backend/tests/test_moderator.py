import pytest
import io
import pandas as pd
from ..models.company_item import CompanyItem
from ..models.price_history import PriceHistory
from ..models.stock_history import StockHistory

def test_upload_price(client, setup_data, db):
    response = client.post("/login", json={"login": "petr", "password": "yacigan"})
    token = response.json()["access_token"]
    
    # Создаём тестовый Excel
    data = {
        "Код": ["001", "002"],
        "Наименование": ["Товар 1", "Товар 2"],
        "Штрихкод": ["1234567890123", "1234567890124"],
        "Ед.изм.": ["шт.", "кг"],
        "Цена": [100.0, 200.0],
        "Остаток": [50, 30]
    }
    df = pd.DataFrame(data)
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    
    response = client.post(
        "/moderator/upload-price",
        files={"file": ("test.xlsx", excel_buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"config": '{"company_id": 1, "identifier_column": "Код", "ean13_column": "Штрихкод", "name_column": "Наименование", "unit_column": "Ед.изм.", "price_column": "Цена", "stock_column": "Остаток", "skip_first_row": false, "update_missing": "zero", "update_name": false}'},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "preview" in response.json()
    assert len(response.json()["preview"]) == 2
    assert db.query(CompanyItem).count() == 2
    assert db.query(PriceHistory).count() == 2
    assert db.query(StockHistory).count() == 2

def test_get_company_items(client, setup_data, db):
    response = client.post("/login", json={"login": "petr", "password": "yacigan"})
    token = response.json()["access_token"]
    item = CompanyItem(
        company_id=1,
        identifier="001",
        ean13="1234567890123",
        name="Товар 1",
        unit_id=1,
        base_price=100.0,
        stock=50
    )
    db.add(item)
    db.commit()
    response = client.get("/moderator/company-items/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["identifier"] == "001"

def test_update_company_item(client, setup_data, db):
    response = client.post("/login", json={"login": "petr", "password": "yacigan"})
    token = response.json()["access_token"]
    item = CompanyItem(
        company_id=1,
        identifier="001",
        ean13="1234567890123",
        name="Товар 1",
        unit_id=1,
        base_price=100.0,
        stock=50
    )
    db.add(item)
    db.commit()
    response = client.put(
        f"/moderator/company-item/{item.id}",
        json={
            "identifier": "001",
            "ean13": "1234567890123",
            "name": "Товар 1 Обновлённый",
            "unit_id": 1,
            "base_price": 150.0,
            "stock": 60,
            "price_type": "base"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Товар 1 Обновлённый"
    assert db.query(PriceHistory).filter(PriceHistory.company_item_id == item.id, PriceHistory.price == 150.0).count() == 1

def test_get_average_price(client, setup_data, db):
    response = client.post("/login", json={"login": "petr", "password": "yacigan"})
    token = response.json()["access_token"]
    item = CompanyItem(
        company_id=1,
        identifier="001",
        ean13="1234567890123",
        name="Товар 1",
        unit_id=1,
        base_price=100.0,
        stock=50
    )
    db.add(item)
    db.flush()
    db.add(PriceHistory(company_item_id=item.id, price=100.0))
    db.add(PriceHistory(company_item_id=item.id, price=200.0))
    db.commit()
    response = client.get(f"/moderator/average-price/{item.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["average_price"] == 150.0