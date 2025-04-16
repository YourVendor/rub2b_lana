import pytest
import io
import pandas as pd
from sqlalchemy import inspect
from backend.models.company_item import CompanyItem
from backend.models.price_history import PriceHistory
from backend.models.stock_history import StockHistory
from backend.models.company import Company
from backend.models.employee_company import EmployeeCompany
from backend.models.user import User
import json

def test_upload_price(client, setup_data, db):
    inspector = inspect(db.get_bind())
    tables = inspector.get_table_names()
    print(f"Tables in test: {tables}")
    assert 'users' in tables, "Table 'users' not found in database"
    assert 'employee_companies' in tables, "Table 'employee_companies' not found in database"
    
    user = db.query(User).filter(User.login == "petr").first()
    assert user is not None, "User 'petr' not found"
    company = db.query(Company).filter(Company.inn == "123456789012").first()
    assert company is not None, "Company not found in database"
    employee = db.query(EmployeeCompany).filter(
        EmployeeCompany.user_id == user.id,
        EmployeeCompany.company_id == company.id
    ).first()
    assert employee is not None, f"EmployeeCompany not found for user {user.id} and company {company.id}"
    
    response = client.post("/login", json={"login": "petr", "password": "yacigan"})
    assert response.status_code == 200, f"Login failed: {response.json()}"
    token = response.json()["access_token"]

    company_id = company.id
    print(f"Using company_id: {company_id}")

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
    print(f"Excel columns: {list(df.columns)}")

    config = {
        "company_id": company_id,
        "identifier_column": "Код",
        "ean13_column": "Штрихкод",
        "name_column": "Наименование",
        "unit_column": "Ед.изм.",
        "price_column": "Цена",
        "stock_column": "Остаток",
        "skip_first_row": False,
        "update_missing": "ignore",
        "update_name": False
    }
    print(f"Sending config: {config}")

    response = client.post(
        "/moderator/upload-price",
        files={"file": ("test.xlsx", excel_buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        data={"config": json.dumps(config)},
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    assert response.status_code == 200, f"Upload failed: {response.json()}"
    assert "preview" in response.json(), "Preview field missing in response"
    assert isinstance(response.json()["preview"], list), "Preview is not a list"
    assert len(response.json()["preview"]) == 2, f"Expected 2 rows in preview, got {len(response.json()['preview'])}"
    assert response.json()["preview"][0]["Код"] == 1, "Incorrect data in preview"  # Изменили на 1

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
    response_json = response.json()
    print(f"Response JSON: {response_json}")  # Добавить дебаг
    assert response_json["name"] == "Товар 1 Обновлённый"
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
    db.commit()  # Заменили flush на commit
    db.add(PriceHistory(company_item_id=item.id, price=100.0))
    db.add(PriceHistory(company_item_id=item.id, price=200.0))
    db.commit()
    response = client.get(f"/moderator/average-price/{item.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["average_price"] == 150.0