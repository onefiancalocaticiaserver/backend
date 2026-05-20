from uuid import UUID

from pydantic import Field, field_validator, model_validator

from app.core.validators import (
    normalizar_email,
    normalizar_whatsapp,
    validar_cpf,
    validar_creci,
    validar_uf,
)
from app.schemas.comum import ModeloBase


class CorretorBase(ModeloBase):
    nome_completo: str = Field(min_length=2, max_length=220)
    cpf: str = Field(min_length=11, max_length=14)
    creci: str = Field(min_length=3, max_length=40)
    whatsapp: str = Field(min_length=10, max_length=30)
    email: str = Field(max_length=255)
    cidade: str = Field(min_length=2, max_length=120)
    uf: str = Field(min_length=2, max_length=2)
    tipo_corretor: str = "autonomo"
    perfil_profissional: str | None = None
    imobiliaria_vinculada_id: UUID | None = None
    volume_indicacoes: int | None = Field(default=None, ge=0)
    aceite_lgpd: bool = True
    opt_in_marketing: bool = True
    origem: str = "site"
    origem_nome: str | None = Field(default=None, max_length=120)
    utm_source: str | None = Field(default=None, max_length=120)
    utm_medium: str | None = Field(default=None, max_length=120)
    utm_campaign: str | None = Field(default=None, max_length=120)
    utm_content: str | None = Field(default=None, max_length=200)
    utm_term: str | None = Field(default=None, max_length=200)

    @field_validator("cpf")
    @classmethod
    def valida_cpf(cls, valor: str) -> str:
        return validar_cpf(valor)

    @field_validator("creci")
    @classmethod
    def valida_creci(cls, valor: str) -> str:
        return validar_creci(valor)

    @field_validator("whatsapp")
    @classmethod
    def valida_whatsapp(cls, valor: str) -> str:
        return normalizar_whatsapp(valor)

    @field_validator("email")
    @classmethod
    def valida_email(cls, valor: str) -> str:
        return normalizar_email(valor)

    @field_validator("uf")
    @classmethod
    def valida_uf(cls, valor: str) -> str:
        return validar_uf(valor)

    @model_validator(mode="after")
    def valida_tipo_autonomo(self) -> "CorretorBase":
        if self.tipo_corretor == "autonomo":
            self.imobiliaria_vinculada_id = None
        return self


class CorretorCriar(CorretorBase):
    pass


class CorretorAtualizar(ModeloBase):
    nome_completo: str | None = Field(default=None, min_length=2, max_length=220)
    cpf: str | None = Field(default=None, min_length=11, max_length=14)
    creci: str | None = Field(default=None, min_length=3, max_length=40)
    whatsapp: str | None = Field(default=None, min_length=10, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    cidade: str | None = Field(default=None, min_length=2, max_length=120)
    uf: str | None = Field(default=None, min_length=2, max_length=2)
    tipo_corretor: str | None = None
    perfil_profissional: str | None = None
    imobiliaria_vinculada_id: UUID | None = None
    volume_indicacoes: int | None = Field(default=None, ge=0)
    status: str | None = None
    observacoes_internas: str | None = None
    aceite_lgpd: bool | None = None
    opt_in_marketing: bool | None = None
    origem: str | None = None
    origem_nome: str | None = Field(default=None, max_length=120)
    utm_source: str | None = Field(default=None, max_length=120)
    utm_medium: str | None = Field(default=None, max_length=120)
    utm_campaign: str | None = Field(default=None, max_length=120)
    utm_content: str | None = Field(default=None, max_length=200)
    utm_term: str | None = Field(default=None, max_length=200)

    @field_validator("cpf")
    @classmethod
    def valida_cpf(cls, valor: str | None) -> str | None:
        return validar_cpf(valor) if valor is not None else None

    @field_validator("creci")
    @classmethod
    def valida_creci(cls, valor: str | None) -> str | None:
        return validar_creci(valor) if valor is not None else None

    @field_validator("whatsapp")
    @classmethod
    def valida_whatsapp(cls, valor: str | None) -> str | None:
        return normalizar_whatsapp(valor) if valor is not None else None

    @field_validator("email")
    @classmethod
    def valida_email(cls, valor: str | None) -> str | None:
        return normalizar_email(valor) if valor is not None else None

    @field_validator("uf")
    @classmethod
    def valida_uf(cls, valor: str | None) -> str | None:
        return validar_uf(valor) if valor is not None else None


class CorretorPublicoAtualizar(ModeloBase):
    nome_completo: str | None = Field(default=None, min_length=2, max_length=220)
    cpf: str | None = Field(default=None, min_length=11, max_length=14)
    creci: str | None = Field(default=None, min_length=3, max_length=40)
    whatsapp: str | None = Field(default=None, min_length=10, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    cidade: str | None = Field(default=None, min_length=2, max_length=120)
    uf: str | None = Field(default=None, min_length=2, max_length=2)
    tipo_corretor: str | None = None
    perfil_profissional: str | None = None
    imobiliaria_vinculada_id: UUID | None = None
    volume_indicacoes: int | None = Field(default=None, ge=0)
    aceite_lgpd: bool | None = None
    opt_in_marketing: bool | None = None
    origem: str | None = None
    origem_nome: str | None = Field(default=None, max_length=120)
    utm_source: str | None = Field(default=None, max_length=120)
    utm_medium: str | None = Field(default=None, max_length=120)
    utm_campaign: str | None = Field(default=None, max_length=120)
    utm_content: str | None = Field(default=None, max_length=200)
    utm_term: str | None = Field(default=None, max_length=200)

    @field_validator("cpf")
    @classmethod
    def valida_cpf(cls, valor: str | None) -> str | None:
        return validar_cpf(valor) if valor is not None else None

    @field_validator("creci")
    @classmethod
    def valida_creci(cls, valor: str | None) -> str | None:
        return validar_creci(valor) if valor is not None else None

    @field_validator("whatsapp")
    @classmethod
    def valida_whatsapp(cls, valor: str | None) -> str | None:
        return normalizar_whatsapp(valor) if valor is not None else None

    @field_validator("email")
    @classmethod
    def valida_email(cls, valor: str | None) -> str | None:
        return normalizar_email(valor) if valor is not None else None

    @field_validator("uf")
    @classmethod
    def valida_uf(cls, valor: str | None) -> str | None:
        return validar_uf(valor) if valor is not None else None


class CorretorResposta(CorretorBase):
    id: UUID
    status: str
    observacoes_internas: str | None = None
