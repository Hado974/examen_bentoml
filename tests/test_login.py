from src.auth import verify_jwt_token


def test_login_success(api_client):
    """Verifie que l'API /login renvoie un jeton JWT valide pour des identifiants corrects."""
    credentials = {
        "username": "user123",
        "password": "password123",
    }
    response = api_client.post("/login", json=credentials)

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    token = data["token"]

    # Verifie que le token est fonctionnel et decode le username
    payload = verify_jwt_token(token)
    assert payload["sub"] == "user123"


def test_login_incorrect_password(api_client):
    """Verifie que l'API renvoie une erreur 401 pour un mot de passe incorrect."""
    credentials = {
        "username": "user123",
        "password": "wrong_password",
    }
    response = api_client.post("/login", json=credentials)

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Invalid credentials"


def test_login_unknown_user(api_client):
    """Verifie que l'API renvoie une erreur 401 pour un utilisateur inexistant."""
    credentials = {
        "username": "unknown_user",
        "password": "password123",
    }
    response = api_client.post("/login", json=credentials)

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"
