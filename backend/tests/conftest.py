import pytest
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app, get_db
from backend.models.user import Base, User
from backend.models.goods import Goods
from backend.models.query import Query
from backend.models.company import Company
from backend.models.warehouse import Warehouse
from backend.models.employee_company import EmployeeCompany
from backend.models.company_item import CompanyItem
from backend.models.price_history import PriceHistory
from backend.models.stock_history import StockHistory
from backend.models.category import Category
from backend.models.goods_categories import GoodsCategory
from backend.models.company_item_categories import CompanyItemCategory
from backend.models.unit import Unit

# Тестовая база SQLite (временный файл)
with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{temp_db.name}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Created tables: {tables}")
    print(f"Engine connected: {engine.connect().closed == False}")
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass  # Не закрываем db, так как scope="module"
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def setup_data(db):
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    
    # Добавляем единицы измерения
    if not db.query(Unit).filter(Unit.name == "шт.").first():
        db.add(Unit(name="шт."))
        db.commit()
    
    if not db.query(Unit).filter(Unit.name == "кг").first():
        db.add(Unit(name="кг"))
        db.commit()
    
    # Добавляем админа
    if not db.query(User).filter(User.login == "germush").first():
        db.add(User(login="germush", password="Gremushka27112007", role="admin"))
        db.commit()
    
    # Добавляем модератора
    user_moderator = db.query(User).filter(User.login == "petr").first()
    if not user_moderator:
        user_moderator = User(login="petr", password="yacigan", role="moderator")
        db.add(user_moderator)
        db.commit()
    print(f"User created: login=petr, id={user_moderator.id}")
    
    # Добавляем компанию
    company = db.query(Company).filter(Company.inn == "123456789012").first()
    if not company:
        company = Company(
            inn="123456789012",
            name="Тестовая",
            legal_name="ООО Тестовая",
            legal_address="Москва, ул. Ленина, 1",
            actual_address="Москва, ул. Мира, 2"
        )
        db.add(company)
        db.commit()
    print(f"Company created: inn=123456789012, id={company.id}")
    
    # Добавляем связь EmployeeCompany
    employee = db.query(EmployeeCompany).filter(
        EmployeeCompany.user_id == user_moderator.id,
        EmployeeCompany.company_id == company.id
    ).first()
    if not employee:
        employee = EmployeeCompany(user_id=user_moderator.id, company_id=company.id)
        db.add(employee)
        db.commit()
        print(f"Created EmployeeCompany: user_id={user_moderator.id}, company_id={company.id}")
    
    # Проверяем запись
    employee_check = db.query(EmployeeCompany).filter(
        EmployeeCompany.user_id == user_moderator.id,
        EmployeeCompany.company_id == company.id
    ).first()
    print(f"Verified EmployeeCompany: found={employee_check is not None}")
    
    db.commit()