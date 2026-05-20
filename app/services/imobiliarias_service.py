from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import ORIGENS_CADASTRO, STATUS_CADASTRO
from app.core.security import gerar_hash_token, gerar_token_cadastro
from app.db.models.imobiliarias import Imobiliaria
from app.schemas.imobiliarias import (
    ImobiliariaAtualizar,
    ImobiliariaCriar,
    ImobiliariaPublicaAtualizar,
)
from app.services.auditoria_service import registrar_evento
from app.services.exceptions import (
    ConflitoError,
    NaoAutorizadoError,
    NaoEncontradoError,
    ValidacaoNegocioError,
)


def listar_imobiliarias(
    db: Session,
    *,
    incluir_removidos: bool = False,
    status: str | None = None,
    limite: int = 100,
    offset: int = 0,
) -> list[Imobiliaria]:
    consulta = (
        select(Imobiliaria).order_by(Imobiliaria.criado_em.desc()).limit(limite).offset(offset)
    )
    if not incluir_removidos:
        consulta = consulta.where(Imobiliaria.removido_em.is_(None))
    if status is not None:
        _validar_status(status)
        consulta = consulta.where(Imobiliaria.status == status)
    return list(db.scalars(consulta).all())


def obter_imobiliaria(
    db: Session,
    imobiliaria_id: UUID,
    *,
    incluir_removidos: bool = False,
) -> Imobiliaria:
    imobiliaria = db.get(Imobiliaria, imobiliaria_id)
    if imobiliaria is None or (imobiliaria.removido_em is not None and not incluir_removidos):
        raise NaoEncontradoError("imobiliaria_nao_encontrada")
    return imobiliaria


def obter_imobiliaria_publica(
    db: Session, imobiliaria_id: UUID, token_cadastro: str
) -> Imobiliaria:
    imobiliaria = obter_imobiliaria(db, imobiliaria_id)
    if imobiliaria.token_cadastro_hash != gerar_hash_token(token_cadastro):
        raise NaoAutorizadoError("token_cadastro_invalido")
    return imobiliaria


def criar_imobiliaria(
    db: Session,
    dados: ImobiliariaCriar,
    *,
    ator_tipo: str,
    ator_id: UUID | None = None,
    origem_padrao: str = "site",
) -> tuple[Imobiliaria, str]:
    token_cadastro = gerar_token_cadastro()
    payload = _preparar_payload(dados.model_dump())
    payload["origem"] = _normalizar_origem(str(payload.get("origem") or origem_padrao))
    payload["token_cadastro_hash"] = gerar_hash_token(token_cadastro)

    imobiliaria = Imobiliaria(**payload)
    db.add(imobiliaria)

    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise ConflitoError("imobiliaria_ja_cadastrada") from exc

    registrar_evento(
        db,
        ator_tipo=ator_tipo,
        ator_id=ator_id,
        acao="criar_imobiliaria",
        entidade_tipo="imobiliaria",
        entidade_id=imobiliaria.id,
    )
    db.commit()
    db.refresh(imobiliaria)
    return imobiliaria, token_cadastro


def atualizar_imobiliaria_publica(
    db: Session,
    imobiliaria_id: UUID,
    dados: ImobiliariaPublicaAtualizar,
    *,
    token_cadastro: str,
) -> Imobiliaria:
    imobiliaria = obter_imobiliaria_publica(db, imobiliaria_id, token_cadastro)
    return _atualizar_imobiliaria(
        db,
        imobiliaria,
        dados.model_dump(exclude_unset=True),
        ator_tipo="publico",
        acao="atualizar_imobiliaria_publica",
    )


def atualizar_imobiliaria_admin(
    db: Session,
    imobiliaria_id: UUID,
    dados: ImobiliariaAtualizar,
    *,
    admin_id: UUID,
) -> Imobiliaria:
    imobiliaria = obter_imobiliaria(db, imobiliaria_id)
    return _atualizar_imobiliaria(
        db,
        imobiliaria,
        dados.model_dump(exclude_unset=True),
        ator_tipo="admin",
        ator_id=admin_id,
        acao="atualizar_imobiliaria",
    )


def atualizar_imobiliaria_operacional(
    db: Session,
    imobiliaria_id: UUID,
    dados: ImobiliariaAtualizar,
    *,
    ator_tipo: str,
    ator_id: UUID | None = None,
) -> Imobiliaria:
    imobiliaria = obter_imobiliaria(db, imobiliaria_id)
    return _atualizar_imobiliaria(
        db,
        imobiliaria,
        dados.model_dump(exclude_unset=True),
        ator_tipo=ator_tipo,
        ator_id=ator_id,
        acao="atualizar_imobiliaria",
    )


def remover_imobiliaria(
    db: Session,
    imobiliaria_id: UUID,
    *,
    ator_tipo: str,
    ator_id: UUID | None = None,
) -> None:
    imobiliaria = obter_imobiliaria(db, imobiliaria_id)
    imobiliaria.removido_em = datetime.now(UTC)
    imobiliaria.status = "inativo"
    registrar_evento(
        db,
        ator_tipo=ator_tipo,
        ator_id=ator_id,
        acao="remover_imobiliaria",
        entidade_tipo="imobiliaria",
        entidade_id=imobiliaria.id,
    )
    db.commit()


def adicionar_observacao_imobiliaria(
    db: Session,
    imobiliaria_id: UUID,
    observacao: str,
    *,
    ator_tipo: str,
    ator_id: UUID | None = None,
) -> Imobiliaria:
    imobiliaria = obter_imobiliaria(db, imobiliaria_id)
    observacao_limpa = observacao.strip()
    if not observacao_limpa:
        raise ValidacaoNegocioError("observacao_obrigatoria")

    observacoes = [item for item in (imobiliaria.observacoes_internas or "").split("\n") if item]
    observacoes.append(observacao_limpa)
    imobiliaria.observacoes_internas = "\n".join(observacoes)
    registrar_evento(
        db,
        ator_tipo=ator_tipo,
        ator_id=ator_id,
        acao="adicionar_observacao_imobiliaria",
        entidade_tipo="imobiliaria",
        entidade_id=imobiliaria.id,
    )
    db.commit()
    db.refresh(imobiliaria)
    return imobiliaria


def _atualizar_imobiliaria(
    db: Session,
    imobiliaria: Imobiliaria,
    payload: dict[str, Any],
    *,
    ator_tipo: str,
    acao: str,
    ator_id: UUID | None = None,
) -> Imobiliaria:
    payload = _preparar_payload(payload)
    if "status" in payload and payload["status"] is not None:
        payload["status"] = _validar_status(str(payload["status"]))
    if "origem" in payload and payload["origem"] is not None:
        payload["origem"] = _normalizar_origem(str(payload["origem"]))

    for campo, valor in payload.items():
        setattr(imobiliaria, campo, valor)

    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise ConflitoError("imobiliaria_ja_cadastrada") from exc

    registrar_evento(
        db,
        ator_tipo=ator_tipo,
        ator_id=ator_id,
        acao=acao,
        entidade_tipo="imobiliaria",
        entidade_id=imobiliaria.id,
        detalhes={"campos": sorted(payload.keys())},
    )
    db.commit()
    db.refresh(imobiliaria)
    return imobiliaria


def _preparar_payload(payload: dict[str, Any]) -> dict[str, Any]:
    cidades = payload.get("cidades_ufs_atuacao")
    if isinstance(cidades, Iterable) and not isinstance(cidades, (str, bytes, dict)):
        payload["cidades_ufs_atuacao"] = [
            cidade.model_dump() if isinstance(cidade, BaseModel) else dict(cidade)
            for cidade in cidades
        ]
    return payload


def _normalizar_origem(valor: str) -> str:
    origem = valor.strip().lower()
    if origem not in ORIGENS_CADASTRO:
        raise ValidacaoNegocioError("origem_invalida")
    return origem


def _validar_status(valor: str) -> str:
    status = valor.strip().lower()
    if status not in STATUS_CADASTRO:
        raise ValidacaoNegocioError("status_invalido")
    return status
