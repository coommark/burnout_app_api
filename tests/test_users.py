def test_register_user(client):
    response = client.post("/users/register", json={
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data

def test_register_user_duplicate(client):
    # First registration
    client.post("/users/register", json={
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    })
    # Duplicate registration
    response = client.post("/users/register", json={
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_user(client):
    # Register user first
    client.post("/users/register", json={
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    })
    # Then login
    response = client.post("/users/login", data={
        "username": "testuser@example.com",
        "password": "TestPassword123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials(client):
    response = client.post("/users/login", data={
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_password_recover(client, mocker):
    # Register first
    client.post("/users/register", json={
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    })

    # Patch email sending
    mocker.patch("app.routers.users.FastMail.send_message", return_value=None)

    response = client.post("/users/password-recover", json={
        "email": "testuser@example.com"
    })
    assert response.status_code == 200
    assert response.json()["msg"] == "Password reset email sent"
