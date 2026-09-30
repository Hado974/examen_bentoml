import jwt
import pytest
from src.auth import (
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    create_jwt_token,
    verify_jwt_token,
)


def test_jwt_valid_token_success():
    """Verifie que l'authentification reussit avec un jeton JWT valide."""
    username = "user123"
    token = create_jwt_token(username, expires_minutes=30)
    payload = verify_jwt_token(token)

    assert payload is not None
    assert payload["sub"] == username
    assert "exp" in payload


def test_jwt_expired_token_failure():
    """Verifie que l'authentification echoue si le jeton JWT a expire."""
    username = "user123"
    # Token cree avec expiration passee (-10 minutes)
    expired_token = create_jwt_token(username, expires_minutes=-10)

    with pytest.raises(jwt.ExpiredSignatureError):
        verify_jwt_token(expired_token)


def test_jwt_invalid_token_failure():
    """Verifie que l'authentification echoue si le jeton JWT est invalide ou corrompu."""
    invalid_token = "invalid.token.string"

    with pytest.raises(jwt.InvalidTokenError):
        verify_jwt_token(invalid_token)


def test_jwt_invalid_secret_failure():
    """Verifie que l'authentification echoue si le token a ete signe avec une autre cle."""
    fake_token = jwt.encode({"sub": "hacker"}, "wrong_secret_key", algorithm=JWT_ALGORITHM)

    with pytest.raises(jwt.InvalidSignatureError):
        verify_jwt_token(fake_token)
