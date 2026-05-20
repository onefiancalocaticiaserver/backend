from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import ORIGENS_CADASTRO, STATUS_CADASTRO, TIPOS_CORRETOR
from app.core.security import gerar_hash_token, gerar_token_cadastro
from app.db.models.corretores import Corretor, CorretorImobiliariaVinculo
from app.db.models.imobiliarias import Imobiliaria
from app.schemas.corretores import CorretorAtualizar, CorretorCriar, CorretorPublicoAtualizar
from app.services.auditoria_service import registrar_evento
from app.services.exceptions import (
    ConflitoError,
    NaoAutorizadoError,
    NaoEncontradoError,
    ValidacaoNegocioError,
)


def listar_corretores(
    db: Session,
    *,
    incluir_removidos: bool = False,
    status: str | None = None,
    limite: int = 100,
    offset: int = 0,
) -> list[Corretor]:
    consulta = select(Corretor).order_by(Corretor.criado_em.desc()).limit(limite).offset(offset)
    if not incluir_removidos:
        consulta = consulta.where(Corretor.removido_em.is_(None))
    if status is not None:
        _validar_status(status)
        consulta = consulta.where(Corretor.status == status)
    return list(db.scalars(consulta).all())


def obter_corretor(
    db: Session,
    corretor_id: UUID,
    *,
    incluir_removidos: bool = False,
) -> Corretor:
    corretor = db.get(Corretor, corretor_id)
    if corretor is None or (corretor.removido_em is not None and not incluir_removidos):
        raise NaoEncontradoError("corretor_nao_encontrado")
    return corretor


def obter_corretor_publico(db: Session, corretor_id: UUID, token_cadastro: str) -> Corretor:
    corretor = obter_corretor(db, corretor_id)
    if corretor.token_cadastro_hash != gerar_hash_token(token_cadastro):
        raise NaoAutorizadoError("token_cadastro_invalido")
    return corretor


def criar_corretor(
    db: Session,
    dados: CorretorCriar,
    *,
    ator_tipo: str,
    ator_id: UUID | None = None,
    origem_padrao: str = "site",
) -> tuple[Corretor, str]:
    token_cadastro = gerar_token_cadastro()
    payload = _preparar_payload(dados.model_dump(), db, criar=True)
    payload["origem"] = _normalizar_origem(str(payload.get("origem") or origem_padrao))
    payload["token_cadastro_hash"] = gerar_hash_token(token_cadastro)

    corretor = Corretor(**payload)
    db.add(corretor)

    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise ConflitoError("corretor_ja_cadastrado") from exc

    registrar_evento(
        db,
        ator_tipo=ator_tipo,
        ator_id=ator_id,
        acao="criar_corretor",
        entidade_tipo="corretor",
        entidade_id=corretor.id,
    )
    db.commit()
    db.refresh(corretor)
    return corretor, token_cadastro


def atualizar_corretor_publico(
    db: Session,
    corretor_id: UUID,
    dados: CorretorPublicoAtualizar,
    *,
    token_cadastro: str,
) -> Corretor:
    corretor = obter_corretor_publico(db, corretor_id, token_cadastro)
    return _atualizar_corretor(
        db,
        corretor,
        dados.model_dump(exclude_unset=True),
        ator_tipo="publico",
        acao="atualizar_corretor_publico",
    )


def atualizar_corretor_admin(
    db: Session,
    corretor_id: UUID,
    dados: CorretorAtualizar,
    *,
    admin_id: UUID,
) -> Corretor:
    corretor = obter_corretor(db, corretor_id)
    return _atualizar_corretor(
        db,
        corretor,
        dados.model_dump(exclude_unset=True),
        ator_tipo="admin",
        ator_id=admin_id,
        acao="atualizar_corretor",
    )


def atualizar_corretor_operacional(
    db: Session,
    corretor_id: UUID,
    dados: CorretorAtualizar,
    *,
    ator_tipo: str,
    ator_id: UUID | None = None,
) -> Corretor:
    corretor = obter_corretor(db, corretor_id)
    return _atualizar_corretor(
        db,
        corretor,
        dados.model_dump(exclude_unset=True),
        ator_tipo=ator_tipo,
        ator_id=ator_id,
        acao="atualizar_corretor",
    )


def remover_corretor(
    db: Session,
    corretor_id: UUID,
    *,
    ator_tipo: str,
    ator_id: UUID | None = None,
) -> None:
    corretor = obter_corretor(db, corretor_id)
    corretor.removido_em = datetime.now(UTC)
    corretor.status = "inativo"

    vinculos = db.scalars(
        select(CorretorImobiliariaVinculo).where(
            CorretorImobiliariaVinculo.corretor_id == corretor_id,
            CorretorImobiliariaVinculo.removido_em.is_(None),
        )
    ).all()
    for vinculo in vinculos:
        vinculo.ativo = False
        vinculo.removido_em = corretor.removido_em

    registrar_evento(
        db,
        ator_tipo=ator_tipo,
        ator_id=ator_id,
        acao="remover_corretor",
        entidade_tipo="corretor",
        entidade_id=corretor.id,
    )
    db.commit()


def vincular_corretor_imobiliaria(
    db: Session,
    *,
    corretor_id: UUID,
    imobiliaria_id: UUID,
    principal: bool = True,
    ator_tipo: str,
    ator_id: UUID | None = None,
) -> CorretorImobiliariaVinculo:
    corretor = obter_corretor(db, corretor_id)
    imobiliaria = db.get(Imobiliaria, imobiliaria_id)
    if imobiliaria is None or imobiliaria.removido_em is not None:
        raise NaoEncontradoError("imobiliaria_nao_encontrada")

    if principal:
        vinculos_principais = db.scalars(
            select(CorretorImobiliariaVinculo).where(
                CorretorImobiliariaVinculo.corretor_id == corretor_id,
                CorretorImobiliariaVinculo.principal.is_(True),
                CorretorImobiliariaVinculo.removido_em.is_(None),
            )
        ).all()
        for vinculo_principal in vinculos_principais:
            vinculo_principal.principal = False

    vinculo = db.scalar(
        select(CorretorImobiliariaVinculo).where(
            CorretorImobiliariaVinculo.corretor_id == corretor_id,
            CorretorImobiliariaVinculo.imobiliaria_id == imobiliaria_id,
        )
    )
    if vinculo is None:
        vinculo = CorretorImobiliariaVinculo(
            corretor_id=corretor_id,
            imobiliaria_id=imobiliaria_id,
            ativo=True,
            principal=principal,
        )
        db.add(vinculo)
    else:
        vinculo.ativo = True
        vinculo.principal = principal
        vinculo.removido_em = None

    corretor.tipo_corretor = "vinculado_imobiliaria"
    corretor.imobiliaria_vinculada_id = imobiliaria_id
    registrar_evento(
        db,
        ator_tipo=ator_tipo,
        ator_id=ator_id,
        acao="vincular_corretor_imobiliaria",
        entidade_tipo="corretor_imobiliaria_vinculo",
        entidade_id=vinculo.id,
        detalhes={"corretor_id": str(corretor_id), "imobiliaria_id": str(imobiliaria_id)},
    )
    db.commit()
    db.refresh(vinculo)
    return vinculo


def remover_vinculo_corretor_imobiliaria(
    db: Session,
    *,
    corretor_id: UUID,
    imobiliaria_id: UUID,
    ator_tipo: str,
    ator_id: UUID | None = None,
) -> None:
    corretor = obter_corretor(db, corretor_id)
    vinculo = db.scalar(
        select(CorretorImobiliariaVinculo).where(
            CorretorImobiliariaVinculo.corretor_id == corretor_id,
            CorretorImobiliariaVinculo.imobiliaria_id == imobiliaria_id,
            CorretorImobiliariaVinculo.removido_em.is_(None),
        )
    )
    if vinculo is None:
        raise NaoEncontradoError("vinculo_nao_encontrado")

    vinculo.ativo = False
    vinculo.removido_em = datetime.now(UTC)
    if corretor.imobiliaria_vinculada_id == imobiliaria_id:
        corretor.imobiliaria_vinculada_id = None
        corretor.tipo_corretor = "autonomo"

    registrar_evento(
        db,
        ator_tipo=ator_tipo,
        ator_id=ator_id,
        acao="remover_vinculo_corretor_imobiliaria",
        entidade_tipo="corretor_imobiliaria_vinculo",
        entidade_id=vinculo.id,
    )
    db.commit()


def adicionar_observacao_corretor(
    db: Session,
    corretor_id: UUID,
    observacao: str,
    *,
    ator_tipo: str,
    ator_id: UUID | None = None,
) -> Corretor:
    corretor = obter_corretor(db, corretor_id)
    observacao_limpa = observacao.strip()
    if not observacao_limpa:
        raise ValidacaoNegocioError("observacao_obrigatoria")

    observacoes = [item for item in (corretor.observacoes_internas or "").split("\n") if item]
    observacoes.append(observacao_limpa)
    corretor.observacoes_internas = "\n".join(observacoes)
    registrar_evento(
        db,
        ator_tipo=ator_tipo,
        ator_id=ator_id,
        acao="adicionar_observacao_corretor",
        entidade_tipo="corretor",
        entidade_id=corretor.id,
    )
    db.commit()
    db.refresh(corretor)
    return corretor


def _atualizar_corretor(
    db: Session,
    corretor: Corretor,
    payload: dict[str, Any],
    *,
    ator_tipo: str,
    acao: str,
    ator_id: UUID | None = None,
) -> Corretor:
    payload = _preparar_payload(payload, db, criar=False)
    if "status" in payload and payload["status"] is not None:
        payload["status"] = _validar_status(str(payload["status"]))
    if "origem" in payload and payload["origem"] is not None:
        payload["origem"] = _normalizar_origem(str(payload["origem"]))

    for campo, valor in payload.items():
        setattr(corretor, campo, valor)

    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise ConflitoError("corretor_ja_cadastrado") from exc

    registrar_evento(
        db,
        ator_tipo=ator_tipo,
        ator_id=ator_id,
        acao=acao,
        entidade_tipo="corretor",
        entidade_id=corretor.id,
        detalhes={"campos": sorted(payload.keys())},
    )
    db.commit()
    db.refresh(corretor)
    return corretor


def _preparar_payload(payload: dict[str, Any], db: Session, *, criar: bool) -> dict[str, Any]:
    tipo_corretor = (
        str(payload.get("tipo_corretor") or ("autonomo" if criar else "")).strip().lower()
    )
    if "tipo_corretor" in payload:
        payload["tipo_corretor"] = _validar_tipo_corretor(tipo_corretor)

    if tipo_corretor == "autonomo":
        payload["imobiliaria_vinculada_id"] = None
        return payload

    imobiliaria_id = payload.get("imobiliaria_vinculada_id")
    if imobiliaria_id is not None:
        imobiliaria = db.get(Imobiliaria, imobiliaria_id)
        if imobiliaria is None or imobiliaria.removido_em is not None:
            raise NaoEncontradoError("imobiliaria_nao_encontrada")
        if "tipo_corretor" not in payload:
            payload["tipo_corretor"] = "vinculado_imobiliaria"

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


def _validar_tipo_corretor(valor: str) -> str:
    tipo = valor.strip().lower()
    if tipo not in TIPOS_CORRETOR:
        raise ValidacaoNegocioError("tipo_corretor_invalido")
    return tipo
