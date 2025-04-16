import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from models.user import Base, User
from models.goods import Goods
from models.query import Query
from models.company import Company
from models.warehouse import Warehouse
from models.employee_company import EmployeeCompany
from models.company_item import CompanyItem
from models.price_history import PriceHistory
from models.stock_history import StockHistory
from models.category import Category
from models.goods_categories import GoodsCategory
from models.company_item_categories import CompanyItemCategory
from models.unit import Unit

# Тестовая база SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def setup_data(db):
    # Добавляем тестовые данные
    user = User(login="germush", password="Gremushka27112007", role="admin")
    db.add(user)
    user_moderator = User(login="petr", password="yacigan", role="moderator")
    db.add(user_moderator)
    unit = Unit(name="шт.")
    db.add(unit)
    company = Company(
        inn="123456789012",
        name="Тестовая",
        legal_name="ООО Тестовая",
        legal_address="Москва, ул. Ленина, 1",
        actual_address="Москва, ул. Мира, 2"
    )
    db.add(company)
    db.commit()