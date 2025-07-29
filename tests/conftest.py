import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.dependencies import get_db, Base
from app.main import app

# ✅ PostgreSQL test database URL
SQLALCHEMY_TEST_URL = "postgresql://burnoutadmin:Casandra1960@localhost/test_db"

# ✅ Setup engine and sessionmaker
engine = create_engine(SQLALCHEMY_TEST_URL)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# ✅ DB Fixture: resets schema for each test function
@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Client Fixture: overrides dependency with test DB
@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

# ✅ Auth Headers Fixture: registers and logs in a user
@pytest.fixture(scope="function")
def auth_headers(client):
    # Register test user
    register_response = client.post("/users/register", json={
        "email": "testuser@example.com",
        "password": "testpass",
        "full_name": "Test User"
    })
    assert register_response.status_code == 200

    # Login test user
    login_response = client.post("/users/login", data={
        "username": "testuser@example.com",
        "password": "testpass"
    })
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
