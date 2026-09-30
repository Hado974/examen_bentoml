def get_valid_payload():
    """Jeu de donnees d'entree valide pour tester /predict."""
    return {
        "gre_score": 320,
        "toefl_score": 110,
        "university_rating": 4,
        "sop": 4.0,
        "lor": 4.0,
        "cgpa": 8.8,
        "research": 1,
    }


def test_predict_missing_token_failure(api_client):
    """Verifie que l'API /predict renvoie une erreur 401 si le jeton JWT est manquant."""
    payload = get_valid_payload()
    response = api_client.post("/predict", json=payload)

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Missing authentication token"


def test_predict_invalid_token_failure(api_client):
    """Verifie que l'API /predict renvoie une erreur 401 si le jeton JWT est invalide."""
    payload = get_valid_payload()
    headers = {"Authorization": "Bearer token_completement_invalide"}
    response = api_client.post("/predict", json=payload, headers=headers)

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid token"


def test_predict_expired_token_failure(api_client, expired_token):
    """Verifie que l'API /predict renvoie une erreur 401 si le jeton JWT a expire."""
    payload = get_valid_payload()
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = api_client.post("/predict", json=payload, headers=headers)

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Token has expired"


def test_predict_valid_input_success(api_client, auth_headers):
    """Verifie que l'API /predict renvoie une prediction valide pour des donnees d'entree correctes."""
    payload = get_valid_payload()
    response = api_client.post("/predict", json=payload, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert isinstance(data["prediction"], list)
    assert len(data["prediction"]) == 1
    assert isinstance(data["prediction"][0], float)

    # La probabilite d'admission doit etre comprise entre 0 et 1
    pred_val = data["prediction"][0]
    assert 0.0 <= pred_val <= 1.0


def test_predict_invalid_input_failure(api_client, auth_headers):
    """Verifie que l'API renvoie une erreur pour des donnees d'entree invalides

    (ex: score GRE superieur au maximum autorise de 340).
    """
    invalid_payload = get_valid_payload()
    invalid_payload["gre_score"] = 999  # GRE max est 340

    response = api_client.post("/predict", json=invalid_payload, headers=auth_headers)
    # Pydantic leve une erreur de validation (code 400 ou 422)
    assert response.status_code in [400, 422]
