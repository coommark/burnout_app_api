import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, date
from app.models import Assessment, User
from app.dependencies import get_db, Base
from app.main import app
from app.models import Assessment
from app.crud import get_user_by_email

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

# ✅ Client Fixture: overrides DB for testing
@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

# ✅ Registers and logs in a test user
@pytest.fixture(scope="function")
def auth_headers(client):
    register_response = client.post("/users/register", json={
        "email": "testuser@example.com",
        "password": "testpass",
        "full_name": "Test User"
    })
    assert register_response.status_code == 200

    login_response = client.post("/users/login", data={
        "username": "testuser@example.com",
        "password": "testpass"
    })
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# ✅ Registers user + seeds 6 assessments so prediction works
@pytest.fixture
async def seeded_user_with_6_assessments(db, client):
    # Create user
    response = client.post("/users/register", json={
        "email": "seeded@example.com",
        "password": "password123",
        "full_name": "Seeded User"
    })
    assert response.status_code == 200

    login_response = client.post("/users/login", data={
        "username": "seeded@example.com",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get user ID
    user = db.execute(select(User).where(User.email == "seeded@example.com")).scalar_one()

    # Add 6 assessments with proper dates
    today = date.today()
    for i in range(6):
        db.add(Assessment(
            user_id=user.id,
            tired_score=3,
            capable_score=3,
            meaningful_score=3,
            date=today - timedelta(days=i)
        ))
    db.commit()

    return headers