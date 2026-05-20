from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decodificar_token_admin
from app.db.models.usuarios_admin import UsuarioAdmin
from app.db.session import get_db

admin_bearer = HTTPBearer(auto_error=False)


def obter_admin_atual(
    db: Annotated[Session, Depends(get_db)],
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(admin_bearer)],
) -> UsuarioAdmin:
    if credenciais is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="credenciais_ausentes",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decodificar_token_admin(credenciais.credentials)
        usuario_id = UUID(str(payload["sub"]))
    except (KeyError, ValueError, jwt.PyJWTError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token_admin_invalido",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    usuario = db.get(UsuarioAdmin, usuario_id)
    if usuario is None or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="admin_inativo_ou_nao_encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario
