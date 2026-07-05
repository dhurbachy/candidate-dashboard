# test/test_auth.py
import app.models  # noqa: F401  (registers models on Base.metadata)


def test_register_user_success(client):
    payload = {"email": "tester@example.com", "password": "securepassword123"}
    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 201
    assert response.json() == {
        "message": "Account created successfully with reviewer baseline privileges."
    }


def test_login_success(client):
    register_payload = {"email": "login_test@example.com", "password": "mypassword123"}
    client.post("/api/auth/register", json=register_payload)

    login_payload = {"email": "login_test@example.com", "password": "mypassword123"}
    response = client.post("/api/auth/login", json=login_payload)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "set-cookie" in response.headers


def test_login_invalid_credentials(client):
    register_payload = {"email": "wrong_pass@example.com", "password": "correct_password"}
    client.post("/api/auth/register", json=register_payload)

    bad_login_payload = {"email": "wrong_pass@example.com", "password": "wrong_password_attempt"}
    response = client.post("/api/auth/login", json=bad_login_payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credential pairing. Verification failed."