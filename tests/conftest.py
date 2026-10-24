from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from shop.api import app
from shop.database import get_session
from shop.models import Base, Category, Product

# 1. Ізольована база даних в оперативній пам'яті для тестів
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="function", autouse=True)
def setup_database() -> Generator[None, None, None]:
    """Створює та очищує таблиці бази даних перед кожним тестом."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Надає окрему тестову сесію бази даних."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Надає підмінений TestClient FastAPI з тестовою базою даних."""

    def override_get_session():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_category(db_session: Session) -> Category:
    """Фікстура для створення тестової категорії."""
    category = Category(name="Electronics")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def sample_products(
    db_session: Session, sample_category: Category
) -> list[Product]:
    """Фікстура для створення списку тестових товарів."""
    products = [
        Product(
            name="Laptop Lenovo",
            price=25000.0,
            quantity=10,
            category_id=sample_category.id,
        ),
        Product(
            name="Wireless Mouse",
            price=800.0,
            quantity=50,
            category_id=sample_category.id,
        ),
        Product(
            name="Gaming Keyboard",
            price=2500.0,
            quantity=20,
            category_id=sample_category.id,
        ),
    ]
    db_session.add_all(products)
    db_session.commit()
    for p in products:
        db_session.refresh(p)
    return products