from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.validators import validar_uf


class CidadeUf(BaseModel):
    cidade: str = Field(min_length=2, max_length=120)
    uf: str = Field(min_length=2, max_length=2)

    @field_validator("uf")
    @classmethod
    def valida_uf(cls, valor: str) -> str:
        return validar_uf(valor)


class ModeloBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RespostaTokenCadastro(BaseModel):
    id: UUID
    token_cadastro: str


class RespostaMensagem(BaseModel):
    mensagem: str


class AuditoriaResumo(ModeloBase):
    criado_em: datetime
    atualizado_em: datetime
    removido_em: datetime | None
