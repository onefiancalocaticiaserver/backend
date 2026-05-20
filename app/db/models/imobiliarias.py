from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON, Uuid

from app.db.base import Base
from app.db.models.mixins import TimestampMixin


class Imobiliaria(TimestampMixin, Base):
    __tablename__ = "imobiliarias"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    razao_social: Mapped[str] = mapped_column(String(220), nullable=False)
    nome_fantasia: Mapped[str] = mapped_column(String(220), nullable=False)
    cnpj: Mapped[str] = mapped_column(String(18), nullable=False, unique=True, index=True)
    whatsapp: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    endereco: Mapped[str] = mapped_column(Text, nullable=False)
    cidades_ufs_atuacao: Mapped[list[dict[str, str]]] = mapped_column(JSON, nullable=False)
    responsavel_principal: Mapped[str] = mapped_column(String(200), nullable=False)
    cargo_responsavel: Mapped[str] = mapped_column(String(120), nullable=False)

    site: Mapped[str | None] = mapped_column(String(300), nullable=True)
    instagram: Mapped[str | None] = mapped_column(String(120), nullable=True)
    media_locacoes_mes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pendente", index=True)
    observacoes_internas: Mapped[str | None] = mapped_column(Text, nullable=True)
    aceite_lgpd: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    opt_in_marketing: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    origem: Mapped[str] = mapped_column(String(30), nullable=False, default="site", index=True)
    origem_nome: Mapped[str | None] = mapped_column(String(120), nullable=True)
    origem_usuario_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("usuarios_admin.id"), nullable=True
    )
    utm_source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    utm_medium: Mapped[str | None] = mapped_column(String(120), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(String(120), nullable=True)
    utm_content: Mapped[str | None] = mapped_column(String(200), nullable=True)
    utm_term: Mapped[str | None] = mapped_column(String(200), nullable=True)
    token_cadastro_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
