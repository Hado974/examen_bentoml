import os
import pytest
import requests
from starlette.testclient import TestClient

from src.auth import create_jwt_token
from src.service import svc

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")


def is_live_server_running(url: str) -> bool:
    """Verifie si un serveur HTTP est en ecoute sur l'URL cible."""
    try:
        resp = requests.get(f"{url.rstrip('/')}/livez", timeout=1.0)
        return resp.status_code in [200, 404]
    except Exception:
        return False


class ApiClientWrapper:
    """Wrapper uniforme permettant aux tests de s'executer soit contre

    un conteneur Docker live (via requests), soit en memoire (via TestClient).
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.use_live = is_live_server_running(self.base_url)
        self._test_client = None

        if not self.use_live:
            self._test_client = TestClient(svc.to_asgi())
            self._test_client.__enter__()

    def post(self, endpoint: str, json=None, headers=None):
        path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        if self.use_live:
            url = f"{self.base_url}{path}"
            return requests.post(url, json=json, headers=headers)
        return self._test_client.post(path, json=json, headers=headers)

    def close(self):
        if self._test_client is not None:
            self._test_client.__exit__(None, None, None)


@pytest.fixture(scope="session")
def api_client():
    """Fixture fournissant un client API (live ou in-memory)."""
    client = ApiClientWrapper(BASE_URL)
    yield client
    client.close()


@pytest.fixture(scope="module")
def base_url():
    """Fixture retournant l'URL de base."""
    return BASE_URL


@pytest.fixture(scope="module")
def valid_token():
    """Jeton JWT valide pour les tests de prediction."""
    return create_jwt_token("user123", expires_minutes=60)


@pytest.fixture(scope="module")
def expired_token():
    """Jeton JWT expire pour tester le rejet d'authentification."""
    return create_jwt_token("user123", expires_minutes=-10)


@pytest.fixture(scope="module")
def auth_headers(valid_token):
    """En-tetes HTTP avec token JWT valide."""
    return {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json",
    }
