import base64
import hashlib
import hmac
import os
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt

from app.core.config import get_settings


def gerar_token_cadastro() -> str:
    return secrets.token_urlsafe(32)


def gerar_hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def gerar_hash_senha(senha: str) -> str:
    sal = os.urandom(16)
    chave = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), sal, 390_000)
    return (
        f"pbkdf2_sha256$390000${base64.b64encode(sal).decode()}${base64.b64encode(chave).decode()}"
    )


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        algoritmo, iteracoes_raw, sal_raw, chave_raw = senha_hash.split("$", 3)
        if algoritmo != "pbkdf2_sha256":
            return False
        iteracoes = int(iteracoes_raw)
        sal = base64.b64decode(sal_raw)
        chave_esperada = base64.b64decode(chave_raw)
    except (ValueError, TypeError):
        return False

    chave = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), sal, iteracoes)
    return hmac.compare_digest(chave, chave_esperada)


def criar_token_admin(usuario_id: UUID, email: str) -> str:
    settings = get_settings()
    agora = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(usuario_id),
        "email": email,
        "iat": int(agora.timestamp()),
        "exp": int((agora + timedelta(minutes=settings.admin_jwt_expires_minutes)).timestamp()),
        "tipo": "admin",
    }
    return jwt.encode(payload, settings.admin_jwt_secret.get_secret_value(), algorithm="HS256")


def decodificar_token_admin(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.admin_jwt_secret.get_secret_value(), algorithms=["HS256"])


def token_bearer_valido(token: str) -> bool:
    esperado = get_settings().one_mcp_auth_token.get_secret_value()
    return hmac.compare_digest(token, esperado)
