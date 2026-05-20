from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.models.auditoria import EventoAuditoria
from app.mcp import tools as mcp_tools
from tests.factories import payload_corretor, payload_imobiliaria


def test_mcp_cria_e_audita_imobiliaria(
    monkeypatch,
    session_factory: sessionmaker[Session],
) -> None:
    monkeypatch.setattr(mcp_tools, "SessionLocal", session_factory)

    resposta = mcp_tools.criar_imobiliaria(payload_imobiliaria())

    assert resposta["id"]
    assert resposta["token_cadastro"]
    with session_factory() as db:
        total = db.scalar(select(func.count()).select_from(EventoAuditoria))
    assert total == 1


def test_mcp_vincula_corretor_imobiliaria(
    monkeypatch,
    session_factory: sessionmaker[Session],
) -> None:
    monkeypatch.setattr(mcp_tools, "SessionLocal", session_factory)

    imobiliaria = mcp_tools.criar_imobiliaria(payload_imobiliaria())
    corretor = mcp_tools.criar_corretor(payload_corretor())

    resposta = mcp_tools.vincular_corretor_imobiliaria(
        corretor_id=str(corretor["id"]),
        imobiliaria_id=str(imobiliaria["id"]),
    )

    assert resposta["ativo"] is True
    assert resposta["principal"] is True
    assert resposta["corretor_id"] == corretor["id"]
    assert resposta["imobiliaria_id"] == imobiliaria["id"]
