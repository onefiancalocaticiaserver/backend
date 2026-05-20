from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON, Uuid

from app.db.base import Base
from app.db.models.mixins import TimestampMixin


class EventoAuditoria(TimestampMixin, Base):
    __tablename__ = "eventos_auditoria"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    ator_tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    ator_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    acao: Mapped[str] = mapped_column(String(80), nullable=False)
    entidade_tipo: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entidade_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True, index=True)
    detalhes: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
