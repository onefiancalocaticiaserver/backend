from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.comum import ModeloBase


class LoginAdminEntrada(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1)


class TokenAdminResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioAdminResposta(ModeloBase):
    id: UUID
    email: EmailStr
    nome: str
    ativo: bool
