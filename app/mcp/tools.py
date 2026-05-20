from collections.abc import Callable
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.comum import RespostaMensagem, RespostaTokenCadastro
from app.schemas.corretores import CorretorAtualizar, CorretorCriar, CorretorResposta
from app.schemas.imobiliarias import ImobiliariaAtualizar, ImobiliariaCriar, ImobiliariaResposta
from app.services.auditoria_service import registrar_evento
from app.services.corretores_service import (
    adicionar_observacao_corretor,
    atualizar_corretor_operacional,
)
from app.services.corretores_service import (
    criar_corretor as criar_corretor_service,
)
from app.services.corretores_service import (
    obter_corretor as obter_corretor_service,
)
from app.services.corretores_service import (
    remover_corretor as remover_corretor_service,
)
from app.services.corretores_service import (
    vincular_corretor_imobiliaria as vincular_corretor_imobiliaria_service,
)
from app.services.exceptions import ErroServico
from app.services.imobiliarias_service import (
    adicionar_observacao_imobiliaria,
    atualizar_imobiliaria_operacional,
)
from app.services.imobiliarias_service import (
    criar_imobiliaria as criar_imobiliaria_service,
)
from app.services.imobiliarias_service import (
    obter_imobiliaria as obter_imobiliaria_service,
)
from app.services.imobiliarias_service import (
    remover_imobiliaria as remover_imobiliaria_service,
)


def criar_imobiliaria(dados: dict[str, Any]) -> dict[str, Any]:
    payload = dict(dados)
    payload["origem"] = str(payload.get("origem") or "chatbot")
    entrada = ImobiliariaCriar.model_validate(payload)

    def operacao(db: Session) -> dict[str, Any]:
        imobiliaria, token = criar_imobiliaria_service(
            db,
            entrada,
            ator_tipo="hermes",
            origem_padrao="chatbot",
        )
        return RespostaTokenCadastro(id=imobiliaria.id, token_cadastro=token).model_dump(
            mode="json"
        )

    return _executar(operacao)


def obter_imobiliaria(imobiliaria_id: str) -> dict[str, Any]:
    entidade_id = UUID(imobiliaria_id)

    def operacao(db: Session) -> dict[str, Any]:
        imobiliaria = obter_imobiliaria_service(db, entidade_id)
        registrar_evento(
            db,
            ator_tipo="hermes",
            acao="obter_imobiliaria",
            entidade_tipo="imobiliaria",
            entidade_id=imobiliaria.id,
        )
        db.commit()
        return ImobiliariaResposta.model_validate(imobiliaria).model_dump(mode="json")

    return _executar(operacao)


def atualizar_imobiliaria(imobiliaria_id: str, dados: dict[str, Any]) -> dict[str, Any]:
    entidade_id = UUID(imobiliaria_id)
    entrada = ImobiliariaAtualizar.model_validate(dados)

    def operacao(db: Session) -> dict[str, Any]:
        imobiliaria = atualizar_imobiliaria_operacional(
            db,
            entidade_id,
            entrada,
            ator_tipo="hermes",
        )
        return ImobiliariaResposta.model_validate(imobiliaria).model_dump(mode="json")

    return _executar(operacao)


def remover_imobiliaria(imobiliaria_id: str) -> dict[str, Any]:
    entidade_id = UUID(imobiliaria_id)

    def operacao(db: Session) -> dict[str, Any]:
        remover_imobiliaria_service(db, entidade_id, ator_tipo="hermes")
        return RespostaMensagem(mensagem="imobiliaria_removida").model_dump(mode="json")

    return _executar(operacao)


def criar_corretor(dados: dict[str, Any]) -> dict[str, Any]:
    payload = dict(dados)
    payload["origem"] = str(payload.get("origem") or "chatbot")
    entrada = CorretorCriar.model_validate(payload)

    def operacao(db: Session) -> dict[str, Any]:
        corretor, token = criar_corretor_service(
            db,
            entrada,
            ator_tipo="hermes",
            origem_padrao="chatbot",
        )
        return RespostaTokenCadastro(id=corretor.id, token_cadastro=token).model_dump(mode="json")

    return _executar(operacao)


def obter_corretor(corretor_id: str) -> dict[str, Any]:
    entidade_id = UUID(corretor_id)

    def operacao(db: Session) -> dict[str, Any]:
        corretor = obter_corretor_service(db, entidade_id)
        registrar_evento(
            db,
            ator_tipo="hermes",
            acao="obter_corretor",
            entidade_tipo="corretor",
            entidade_id=corretor.id,
        )
        db.commit()
        return CorretorResposta.model_validate(corretor).model_dump(mode="json")

    return _executar(operacao)


def atualizar_corretor(corretor_id: str, dados: dict[str, Any]) -> dict[str, Any]:
    entidade_id = UUID(corretor_id)
    entrada = CorretorAtualizar.model_validate(dados)

    def operacao(db: Session) -> dict[str, Any]:
        corretor = atualizar_corretor_operacional(
            db,
            entidade_id,
            entrada,
            ator_tipo="hermes",
        )
        return CorretorResposta.model_validate(corretor).model_dump(mode="json")

    return _executar(operacao)


def remover_corretor(corretor_id: str) -> dict[str, Any]:
    entidade_id = UUID(corretor_id)

    def operacao(db: Session) -> dict[str, Any]:
        remover_corretor_service(db, entidade_id, ator_tipo="hermes")
        return RespostaMensagem(mensagem="corretor_removido").model_dump(mode="json")

    return _executar(operacao)


def vincular_corretor_imobiliaria(
    corretor_id: str,
    imobiliaria_id: str,
    principal: bool = True,
) -> dict[str, Any]:
    corretor_uuid = UUID(corretor_id)
    imobiliaria_uuid = UUID(imobiliaria_id)

    def operacao(db: Session) -> dict[str, Any]:
        vinculo = vincular_corretor_imobiliaria_service(
            db,
            corretor_id=corretor_uuid,
            imobiliaria_id=imobiliaria_uuid,
            principal=principal,
            ator_tipo="hermes",
        )
        return {
            "id": str(vinculo.id),
            "corretor_id": str(vinculo.corretor_id),
            "imobiliaria_id": str(vinculo.imobiliaria_id),
            "ativo": vinculo.ativo,
            "principal": vinculo.principal,
        }

    return _executar(operacao)


def adicionar_observacao_parceiro(
    tipo_parceiro: str,
    parceiro_id: str,
    observacao: str,
) -> dict[str, Any]:
    entidade_id = UUID(parceiro_id)
    tipo = tipo_parceiro.strip().lower()

    def operacao(db: Session) -> dict[str, Any]:
        if tipo == "imobiliaria":
            imobiliaria = adicionar_observacao_imobiliaria(
                db,
                entidade_id,
                observacao,
                ator_tipo="hermes",
            )
            return ImobiliariaResposta.model_validate(imobiliaria).model_dump(mode="json")
        if tipo == "corretor":
            corretor = adicionar_observacao_corretor(
                db,
                entidade_id,
                observacao,
                ator_tipo="hermes",
            )
            return CorretorResposta.model_validate(corretor).model_dump(mode="json")
        raise ValueError("tipo_parceiro_invalido")

    return _executar(operacao)


def _executar(operacao: Callable[[Session], dict[str, Any]]) -> dict[str, Any]:
    with SessionLocal() as db:
        try:
            return operacao(db)
        except ErroServico as exc:
            db.rollback()
            raise ValueError(str(exc)) from exc
