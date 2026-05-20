from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.auditoria import EventoAuditoria


def registrar_evento(
    db: Session,
    *,
    ator_tipo: str,
    acao: str,
    entidade_tipo: str,
    entidade_id: UUID | None = None,
    ator_id: UUID | None = None,
    detalhes: dict[str, object] | None = None,
) -> EventoAuditoria:
    evento = EventoAuditoria(
        ator_tipo=ator_tipo,
        ator_id=ator_id,
        acao=acao,
        entidade_tipo=entidade_tipo,
        entidade_id=entidade_id,
        detalhes=detalhes,
    )
    db.add(evento)
    return evento
