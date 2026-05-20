from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.db.base import Base
from app.db.models.mixins import TimestampMixin


class Corretor(TimestampMixin, Base):
    __tablename__ = "corretores"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    nome_completo: Mapped[str] = mapped_column(String(220), nullable=False)
    cpf: Mapped[str] = mapped_column(String(14), nullable=False, unique=True, index=True)
    creci: Mapped[str] = mapped_column(String(40), nullable=False)
    whatsapp: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    cidade: Mapped[str] = mapped_column(String(120), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    tipo_corretor: Mapped[str] = mapped_column(String(40), nullable=False, default="autonomo")

    perfil_profissional: Mapped[str | None] = mapped_column(Text, nullable=True)
    imobiliaria_vinculada_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("imobiliarias.id"), nullable=True
    )
    volume_indicacoes: Mapped[int | None] = mapped_column(Integer, nullable=True)

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


class CorretorImobiliariaVinculo(TimestampMixin, Base):
    __tablename__ = "corretor_imobiliaria_vinculos"
    __table_args__ = (
        UniqueConstraint("corretor_id", "imobiliaria_id", name="uq_vinculo_corretor_imobiliaria"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    corretor_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("corretores.id"), nullable=False, index=True
    )
    imobiliaria_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("imobiliarias.id"), nullable=False, index=True
    )
    ativo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    principal: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
