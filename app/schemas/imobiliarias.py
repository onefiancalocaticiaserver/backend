from uuid import UUID

from pydantic import Field, field_validator

from app.core.validators import normalizar_email, normalizar_whatsapp, validar_cnpj
from app.schemas.comum import CidadeUf, ModeloBase


class ImobiliariaBase(ModeloBase):
    razao_social: str = Field(min_length=2, max_length=220)
    nome_fantasia: str = Field(min_length=2, max_length=220)
    cnpj: str = Field(min_length=14, max_length=18)
    whatsapp: str = Field(min_length=10, max_length=30)
    email: str = Field(max_length=255)
    endereco: str = Field(min_length=5)
    cidades_ufs_atuacao: list[CidadeUf] = Field(min_length=1)
    responsavel_principal: str = Field(min_length=2, max_length=200)
    cargo_responsavel: str = Field(min_length=2, max_length=120)
    site: str | None = Field(default=None, max_length=300)
    instagram: str | None = Field(default=None, max_length=120)
    media_locacoes_mes: int | None = Field(default=None, ge=0)
    aceite_lgpd: bool = True
    opt_in_marketing: bool = True
    origem: str = "site"
    origem_nome: str | None = Field(default=None, max_length=120)
    utm_source: str | None = Field(default=None, max_length=120)
    utm_medium: str | None = Field(default=None, max_length=120)
    utm_campaign: str | None = Field(default=None, max_length=120)
    utm_content: str | None = Field(default=None, max_length=200)
    utm_term: str | None = Field(default=None, max_length=200)

    @field_validator("cnpj")
    @classmethod
    def valida_cnpj(cls, valor: str) -> str:
        return validar_cnpj(valor)

    @field_validator("whatsapp")
    @classmethod
    def valida_whatsapp(cls, valor: str) -> str:
        return normalizar_whatsapp(valor)

    @field_validator("email")
    @classmethod
    def valida_email(cls, valor: str) -> str:
        return normalizar_email(valor)


class ImobiliariaCriar(ImobiliariaBase):
    pass


class ImobiliariaAtualizar(ModeloBase):
    razao_social: str | None = Field(default=None, min_length=2, max_length=220)
    nome_fantasia: str | None = Field(default=None, min_length=2, max_length=220)
    cnpj: str | None = Field(default=None, min_length=14, max_length=18)
    whatsapp: str | None = Field(default=None, min_length=10, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    endereco: str | None = Field(default=None, min_length=5)
    cidades_ufs_atuacao: list[CidadeUf] | None = None
    responsavel_principal: str | None = Field(default=None, min_length=2, max_length=200)
    cargo_responsavel: str | None = Field(default=None, min_length=2, max_length=120)
    site: str | None = Field(default=None, max_length=300)
    instagram: str | None = Field(default=None, max_length=120)
    media_locacoes_mes: int | None = Field(default=None, ge=0)
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

    @field_validator("cnpj")
    @classmethod
    def valida_cnpj(cls, valor: str | None) -> str | None:
        return validar_cnpj(valor) if valor is not None else None

    @field_validator("whatsapp")
    @classmethod
    def valida_whatsapp(cls, valor: str | None) -> str | None:
        return normalizar_whatsapp(valor) if valor is not None else None

    @field_validator("email")
    @classmethod
    def valida_email(cls, valor: str | None) -> str | None:
        return normalizar_email(valor) if valor is not None else None


class ImobiliariaPublicaAtualizar(ModeloBase):
    razao_social: str | None = Field(default=None, min_length=2, max_length=220)
    nome_fantasia: str | None = Field(default=None, min_length=2, max_length=220)
    cnpj: str | None = Field(default=None, min_length=14, max_length=18)
    whatsapp: str | None = Field(default=None, min_length=10, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    endereco: str | None = Field(default=None, min_length=5)
    cidades_ufs_atuacao: list[CidadeUf] | None = None
    responsavel_principal: str | None = Field(default=None, min_length=2, max_length=200)
    cargo_responsavel: str | None = Field(default=None, min_length=2, max_length=120)
    site: str | None = Field(default=None, max_length=300)
    instagram: str | None = Field(default=None, max_length=120)
    media_locacoes_mes: int | None = Field(default=None, ge=0)
    aceite_lgpd: bool | None = None
    opt_in_marketing: bool | None = None
    origem: str | None = None
    origem_nome: str | None = Field(default=None, max_length=120)
    utm_source: str | None = Field(default=None, max_length=120)
    utm_medium: str | None = Field(default=None, max_length=120)
    utm_campaign: str | None = Field(default=None, max_length=120)
    utm_content: str | None = Field(default=None, max_length=200)
    utm_term: str | None = Field(default=None, max_length=200)

    @field_validator("cnpj")
    @classmethod
    def valida_cnpj(cls, valor: str | None) -> str | None:
        return validar_cnpj(valor) if valor is not None else None

    @field_validator("whatsapp")
    @classmethod
    def valida_whatsapp(cls, valor: str | None) -> str | None:
        return normalizar_whatsapp(valor) if valor is not None else None

    @field_validator("email")
    @classmethod
    def valida_email(cls, valor: str | None) -> str | None:
        return normalizar_email(valor) if valor is not None else None


class ImobiliariaResposta(ImobiliariaBase):
    id: UUID
    status: str
    observacoes_internas: str | None = None
