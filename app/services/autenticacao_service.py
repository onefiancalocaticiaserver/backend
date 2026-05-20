from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import criar_token_admin, gerar_hash_senha, verificar_senha
from app.core.validators import normalizar_email
from app.db.models.usuarios_admin import UsuarioAdmin
from app.services.auditoria_service import registrar_evento
from app.services.exceptions import NaoAutorizadoError


def obter_admin_por_email(db: Session, email: str) -> UsuarioAdmin | None:
    email_normalizado = normalizar_email(email)
    return db.scalar(select(UsuarioAdmin).where(UsuarioAdmin.email == email_normalizado))


def criar_ou_atualizar_admin_inicial(
    db: Session,
    *,
    email: str,
    senha: str,
    nome: str,
) -> UsuarioAdmin:
    email_normalizado = normalizar_email(email)
    usuario = db.scalar(select(UsuarioAdmin).where(UsuarioAdmin.email == email_normalizado))
    senha_hash = gerar_hash_senha(senha)

    if usuario is None:
        usuario = UsuarioAdmin(
            email=email_normalizado,
            senha_hash=senha_hash,
            nome=nome,
            ativo=True,
        )
        db.add(usuario)
        acao = "admin_criado"
    else:
        usuario.senha_hash = senha_hash
        usuario.nome = nome
        usuario.ativo = True
        acao = "admin_atualizado"

    db.flush()
    registrar_evento(
        db,
        ator_tipo="sistema",
        acao=acao,
        entidade_tipo="usuario_admin",
        entidade_id=usuario.id,
    )
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar_admin(db: Session, *, email: str, senha: str) -> tuple[UsuarioAdmin, str]:
    usuario = obter_admin_por_email(db, email)
    if usuario is None or not usuario.ativo or not verificar_senha(senha, usuario.senha_hash):
        raise NaoAutorizadoError("credenciais_invalidas")

    usuario.ultimo_login_em = datetime.now(UTC)
    registrar_evento(
        db,
        ator_tipo="admin",
        ator_id=usuario.id,
        acao="login_admin",
        entidade_tipo="usuario_admin",
        entidade_id=usuario.id,
    )
    db.commit()
    db.refresh(usuario)
    return usuario, criar_token_admin(usuario.id, usuario.email)
