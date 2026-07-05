import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import app.models
# Import your database components and models
from app.database import Base, get_db
from app.main import app
from sqlalchemy.pool import StaticPool

# 1. Create an isolated in-memory or file-based SQLite engine for testing
TEST_DATABASE_URL = "sqlite://"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    # 2. Build all tables (like 'users') in the test database before the test runs
    Base.metadata.create_all(bind=engine)
    yield
    # 3. Drop all tables after the test finishes to keep tests isolated
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(session):
    # 4. Override production dependency injection with the test database session
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
