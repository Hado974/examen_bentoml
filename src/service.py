import bentoml
import numpy as np
import pandas as pd
from starlette.responses import JSONResponse

from src.auth import (
    JWTAuthMiddleware,
    PayloadNormalizerMiddleware,
    USERS,
    create_jwt_token,
)
from src.models import AdmissionInput, UserCredentials

# Noms exacts des variables explicatives utilisees lors de l'entrainement
FEATURE_NAMES = [
    "GRE Score",
    "TOEFL Score",
    "University Rating",
    "SOP",
    "LOR",
    "CGPA",
    "Research",
]


@bentoml.service(
    name="admission_prediction_service",
)
class AdmissionPredictionService:
    def __init__(self):
        # Chargement du modele entraine depuis le Model Store BentoML
        self.model = bentoml.sklearn.load_model("admission_lr:latest")

    @bentoml.api(route="/login")
    def login(self, credentials: UserCredentials) -> dict:
        """Endpoint d'authentification verifiant les identifiants utilisateur

        et delivrant un token JWT valide.
        """
        user_pwd = USERS.get(credentials.username)
        if user_pwd is not None and user_pwd == credentials.password:
            token = create_jwt_token(credentials.username)
            return {"token": token}
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid credentials"},
        )

    @bentoml.api(route="/predict")
    def predict(self, input_data: AdmissionInput) -> dict:
        """Endpoint de prediction de la chance d'admission pour un etudiant donne.

        Necessite un token JWT valide dans l'en-tete Authorization.
        """
        # Reconstruction d'un DataFrame avec les colonnes exactes
        df_features = pd.DataFrame(
            [
                [
                    input_data.gre_score,
                    input_data.toefl_score,
                    input_data.university_rating,
                    input_data.sop,
                    input_data.lor,
                    input_data.cgpa,
                    input_data.research,
                ]
            ],
            columns=FEATURE_NAMES,
        )

        prediction = self.model.predict(df_features)
        pred_value = float(np.clip(prediction[0], 0.0, 1.0))

        return {"prediction": [pred_value]}


# Application des middlewares (normalisation du body et securite JWT)
AdmissionPredictionService.add_asgi_middleware(PayloadNormalizerMiddleware)
AdmissionPredictionService.add_asgi_middleware(JWTAuthMiddleware)

# Alias du service exporte pour bentofile.yaml ("src.service:svc")
svc = AdmissionPredictionService
