from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import obter_admin_atual
from app.api.errors import converter_erro_servico
from app.db.models.usuarios_admin import UsuarioAdmin
from app.db.session import get_db
from app.schemas.autenticacao import LoginAdminEntrada, TokenAdminResposta, UsuarioAdminResposta
from app.schemas.comum import RespostaMensagem
from app.schemas.corretores import CorretorAtualizar, CorretorResposta
from app.schemas.imobiliarias import ImobiliariaAtualizar, ImobiliariaResposta
from app.services.autenticacao_service import autenticar_admin
from app.services.corretores_service import (
    atualizar_corretor_admin,
    listar_corretores,
    obter_corretor,
    remover_corretor,
    remover_vinculo_corretor_imobiliaria,
    vincular_corretor_imobiliaria,
)
from app.services.exceptions import ErroServico, NaoAutorizadoError
from app.services.imobiliarias_service import (
    atualizar_imobiliaria_admin,
    listar_imobiliarias,
    obter_imobiliaria,
    remover_imobiliaria,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/autenticacao/login", response_model=TokenAdminResposta)
def login_admin(
    dados: LoginAdminEntrada,
    db: Annotated[Session, Depends(get_db)],
) -> TokenAdminResposta:
    try:
        _, token = autenticar_admin(db, email=str(dados.email), senha=dados.senha)
    except NaoAutorizadoError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return TokenAdminResposta(access_token=token)


@router.get("/eu", response_model=UsuarioAdminResposta)
def obter_admin_logado(
    admin: Annotated[UsuarioAdmin, Depends(obter_admin_atual)],
) -> UsuarioAdminResposta:
    return UsuarioAdminResposta.model_validate(admin)


@router.get("/imobiliarias", response_model=list[ImobiliariaResposta])
def listar_imobiliarias_admin(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAdmin, Depends(obter_admin_atual)],
    incluir_removidos: bool = False,
    status_cadastro: Annotated[str | None, Query(alias="status")] = None,
    limite: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ImobiliariaResposta]:
    try:
        imobiliarias = listar_imobiliarias(
            db,
            incluir_removidos=incluir_removidos,
            status=status_cadastro,
            limite=limite,
            offset=offset,
        )
    except ErroServico as exc:
        converter_erro_servico(exc)
    return [ImobiliariaResposta.model_validate(imobiliaria) for imobiliaria in imobiliarias]


@router.get("/imobiliarias/{imobiliaria_id}", response_model=ImobiliariaResposta)
def obter_imobiliaria_admin(
    imobiliaria_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAdmin, Depends(obter_admin_atual)],
) -> ImobiliariaResposta:
    try:
        return ImobiliariaResposta.model_validate(obter_imobiliaria(db, imobiliaria_id))
    except ErroServico as exc:
        converter_erro_servico(exc)


@router.patch("/imobiliarias/{imobiliaria_id}", response_model=ImobiliariaResposta)
def atualizar_imobiliaria_admin_endpoint(
    imobiliaria_id: UUID,
    dados: ImobiliariaAtualizar,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[UsuarioAdmin, Depends(obter_admin_atual)],
) -> ImobiliariaResposta:
    try:
        return ImobiliariaResposta.model_validate(
            atualizar_imobiliaria_admin(db, imobiliaria_id, dados, admin_id=admin.id)
        )
    except ErroServico as exc:
        converter_erro_servico(exc)


@router.delete("/imobiliarias/{imobiliaria_id}", response_model=RespostaMensagem)
def remover_imobiliaria_admin_endpoint(
    imobiliaria_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[UsuarioAdmin, Depends(obter_admin_atual)],
) -> RespostaMensagem:
    try:
        remover_imobiliaria(db, imobiliaria_id, ator_tipo="admin", ator_id=admin.id)
    except ErroServico as exc:
        converter_erro_servico(exc)
    return RespostaMensagem(mensagem="imobiliaria_removida")


@router.get("/corretores", response_model=list[CorretorResposta])
def listar_corretores_admin(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAdmin, Depends(obter_admin_atual)],
    incluir_removidos: bool = False,
    status_cadastro: Annotated[str | None, Query(alias="status")] = None,
    limite: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[CorretorResposta]:
    try:
        corretores = listar_corretores(
            db,
            incluir_removidos=incluir_removidos,
            status=status_cadastro,
            limite=limite,
            offset=offset,
        )
    except ErroServico as exc:
        converter_erro_servico(exc)
    return [CorretorResposta.model_validate(corretor) for corretor in corretores]


@router.get("/corretores/{corretor_id}", response_model=CorretorResposta)
def obter_corretor_admin(
    corretor_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[UsuarioAdmin, Depends(obter_admin_atual)],
) -> CorretorResposta:
    try:
        return CorretorResposta.model_validate(obter_corretor(db, corretor_id))
    except ErroServico as exc:
        converter_erro_servico(exc)


@router.patch("/corretores/{corretor_id}", response_model=CorretorResposta)
def atualizar_corretor_admin_endpoint(
    corretor_id: UUID,
    dados: CorretorAtualizar,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[UsuarioAdmin, Depends(obter_admin_atual)],
) -> CorretorResposta:
    try:
        return CorretorResposta.model_validate(
            atualizar_corretor_admin(db, corretor_id, dados, admin_id=admin.id)
        )
    except ErroServico as exc:
        converter_erro_servico(exc)


@router.delete("/corretores/{corretor_id}", response_model=RespostaMensagem)
def remover_corretor_admin_endpoint(
    corretor_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[UsuarioAdmin, Depends(obter_admin_atual)],
) -> RespostaMensagem:
    try:
        remover_corretor(db, corretor_id, ator_tipo="admin", ator_id=admin.id)
    except ErroServico as exc:
        converter_erro_servico(exc)
    return RespostaMensagem(mensagem="corretor_removido")


@router.post(
    "/imobiliarias/{imobiliaria_id}/corretores/{corretor_id}",
    response_model=RespostaMensagem,
)
def vincular_corretor_imobiliaria_admin_endpoint(
    imobiliaria_id: UUID,
    corretor_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[UsuarioAdmin, Depends(obter_admin_atual)],
    principal: bool = True,
) -> RespostaMensagem:
    try:
        vincular_corretor_imobiliaria(
            db,
            corretor_id=corretor_id,
            imobiliaria_id=imobiliaria_id,
            principal=principal,
            ator_tipo="admin",
            ator_id=admin.id,
        )
    except ErroServico as exc:
        converter_erro_servico(exc)
    return RespostaMensagem(mensagem="corretor_vinculado")


@router.delete(
    "/imobiliarias/{imobiliaria_id}/corretores/{corretor_id}",
    response_model=RespostaMensagem,
)
def remover_vinculo_corretor_imobiliaria_admin_endpoint(
    imobiliaria_id: UUID,
    corretor_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[UsuarioAdmin, Depends(obter_admin_atual)],
) -> RespostaMensagem:
    try:
        remover_vinculo_corretor_imobiliaria(
            db,
            corretor_id=corretor_id,
            imobiliaria_id=imobiliaria_id,
            ator_tipo="admin",
            ator_id=admin.id,
        )
    except ErroServico as exc:
        converter_erro_servico(exc)
    return RespostaMensagem(mensagem="vinculo_removido")
