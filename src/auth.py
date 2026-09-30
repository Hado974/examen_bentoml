import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Cle secrete et algorithme pour la signature des jetons JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "examen_bentoml_secret_key_2026")
JWT_ALGORITHM = "HS256"

# Utilisateurs autorises pour l'authentification
USERS: Dict[str, str] = {
    "user123": "password123",
    "admin": "admin123",
}


def create_jwt_token(user_id: str, expires_minutes: int = 60) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {
        "sub": user_id,
        "exp": expiration,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


class PayloadNormalizerMiddleware:
    """Middleware ASGI permettant d'accepter les requetes JSON avec les champs au niveau racine

    (ex: {"gre_score": ...}) tout comme la syntaxe enveloppee BentoML 1.4
    (ex: {"input_data": {"gre_score": ...}}).
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope.get("method") == "POST":
            path = scope.get("path", "").rstrip("/")
            if path.endswith("/predict") or path.endswith("/login"):
                body_chunks = []
                while True:
                    msg = await receive()
                    body_chunks.append(msg.get("body", b""))
                    if not msg.get("more_body", False):
                        break
                body = b"".join(body_chunks)

                if body:
                    try:
                        data = json.loads(body)
                        if isinstance(data, dict):
                            if path.endswith("/predict") and "input_data" not in data:
                                body = json.dumps({"input_data": data}).encode("utf-8")
                            elif path.endswith("/login") and "credentials" not in data:
                                body = json.dumps({"credentials": data}).encode("utf-8")
                    except Exception:
                        pass

                sent = False

                async def new_receive():
                    nonlocal sent
                    if not sent:
                        sent = True
                        return {"type": "http.request", "body": body, "more_body": False}
                    return {"type": "http.request", "body": b"", "more_body": False}

                await self.app(scope, new_receive, send)
                return

        await self.app(scope, receive, send)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    # Middleware Starlette verifiant la presence et la validite du jeton JWT sur la route /predict.
    async def dispatch(self, request: Request, call_next):
        path = request.url.path.rstrip("/")
        if path.endswith("/predict"):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Missing authentication token"},
                )

            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid token"},
                )

            token = parts[1]
            try:
                payload = verify_jwt_token(token)
                request.state.user = payload.get("sub")
            except jwt.ExpiredSignatureError:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Token has expired"},
                )
            except jwt.InvalidTokenError:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid token"},
                )

        return await call_next(request)
