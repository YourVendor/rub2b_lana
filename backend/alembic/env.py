from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from backend.database import Base
from backend.models.unit import Unit
from backend.models.user import User
from backend.models.company import Company
from backend.models.employee_company import EmployeeCompany
from backend.models.company_item import CompanyItem
from backend.models.prices import Prices
from backend.models.price_history import PriceHistory
from backend.models.stock_history import StockHistory
from backend.models.category import Category
from backend.models.company_item_categories import CompanyItemCategory
from backend.models.goods import Goods
from backend.models.goods_categories import GoodsCategory
from backend.models.query import Query
from backend.models.warehouse import Warehouse

# Отладка: выведем таблицы
print("Tables in metadata:", [t.name for t in Base.metadata.sorted_tables])

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

connectable = engine_from_config(
    config.get_section(config.config_ini_section),
    prefix="sqlalchemy.",
    poolclass=pool.NullPool
)

with connectable.connect() as connection:
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        include_object=lambda object, name, type_, reflected, compare_to: (
            type_ != "column" or (
                object.table.name != "price_history" or name != "price"
            )
        )
    )
    with context.begin_transaction():
        context.run_migrations()