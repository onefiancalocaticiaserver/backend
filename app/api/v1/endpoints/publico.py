from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from app.api.errors import converter_erro_servico
from app.db.session import get_db
from app.schemas.comum import RespostaTokenCadastro
from app.schemas.corretores import CorretorCriar, CorretorPublicoAtualizar, CorretorResposta
from app.schemas.imobiliarias import (
    ImobiliariaCriar,
    ImobiliariaPublicaAtualizar,
    ImobiliariaResposta,
)
from app.services.corretores_service import (
    atualizar_corretor_publico,
    criar_corretor,
    obter_corretor_publico,
)
from app.services.exceptions import ErroServico
from app.services.imobiliarias_service import (
    atualizar_imobiliaria_publica,
    criar_imobiliaria,
    obter_imobiliaria_publica,
)

router = APIRouter(prefix="/publico", tags=["publico"])


@router.post(
    "/imobiliarias",
    response_model=RespostaTokenCadastro,
    status_code=status.HTTP_201_CREATED,
)
def criar_imobiliaria_publica(
    dados: ImobiliariaCriar,
    db: Annotated[Session, Depends(get_db)],
) -> RespostaTokenCadastro:
    try:
        imobiliaria, token = criar_imobiliaria(db, dados, ator_tipo="publico", origem_padrao="site")
    except ErroServico as exc:
        converter_erro_servico(exc)
    return RespostaTokenCadastro(id=imobiliaria.id, token_cadastro=token)


@router.get("/imobiliarias/{imobiliaria_id}", response_model=ImobiliariaResposta)
def obter_imobiliaria_publica_endpoint(
    imobiliaria_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    token_cadastro: Annotated[str, Header(alias="X-Cadastro-Token")],
) -> ImobiliariaResposta:
    try:
        return ImobiliariaResposta.model_validate(
            obter_imobiliaria_publica(db, imobiliaria_id, token_cadastro)
        )
    except ErroServico as exc:
        converter_erro_servico(exc)


@router.patch("/imobiliarias/{imobiliaria_id}", response_model=ImobiliariaResposta)
def atualizar_imobiliaria_publica_endpoint(
    imobiliaria_id: UUID,
    dados: ImobiliariaPublicaAtualizar,
    db: Annotated[Session, Depends(get_db)],
    token_cadastro: Annotated[str, Header(alias="X-Cadastro-Token")],
) -> ImobiliariaResposta:
    try:
        return ImobiliariaResposta.model_validate(
            atualizar_imobiliaria_publica(db, imobiliaria_id, dados, token_cadastro=token_cadastro)
        )
    except ErroServico as exc:
        converter_erro_servico(exc)


@router.post(
    "/corretores",
    response_model=RespostaTokenCadastro,
    status_code=status.HTTP_201_CREATED,
)
def criar_corretor_publico(
    dados: CorretorCriar,
    db: Annotated[Session, Depends(get_db)],
) -> RespostaTokenCadastro:
    try:
        corretor, token = criar_corretor(db, dados, ator_tipo="publico", origem_padrao="site")
    except ErroServico as exc:
        converter_erro_servico(exc)
    return RespostaTokenCadastro(id=corretor.id, token_cadastro=token)


@router.get("/corretores/{corretor_id}", response_model=CorretorResposta)
def obter_corretor_publico_endpoint(
    corretor_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    token_cadastro: Annotated[str, Header(alias="X-Cadastro-Token")],
) -> CorretorResposta:
    try:
        return CorretorResposta.model_validate(
            obter_corretor_publico(db, corretor_id, token_cadastro)
        )
    except ErroServico as exc:
        converter_erro_servico(exc)


@router.patch("/corretores/{corretor_id}", response_model=CorretorResposta)
def atualizar_corretor_publico_endpoint(
    corretor_id: UUID,
    dados: CorretorPublicoAtualizar,
    db: Annotated[Session, Depends(get_db)],
    token_cadastro: Annotated[str, Header(alias="X-Cadastro-Token")],
) -> CorretorResposta:
    try:
        return CorretorResposta.model_validate(
            atualizar_corretor_publico(db, corretor_id, dados, token_cadastro=token_cadastro)
        )
    except ErroServico as exc:
        converter_erro_servico(exc)
