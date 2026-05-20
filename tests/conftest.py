from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.services.autenticacao_service import criar_ou_atualizar_admin_inicial


@pytest.fixture()
def session_factory() -> Generator[sessionmaker[Session], None, None]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=engine,
    )
    try:
        yield testing_session_local
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(session_factory: sessionmaker[Session]) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_token(client: TestClient, session_factory: sessionmaker[Session]) -> str:
    with session_factory() as db:
        criar_ou_atualizar_admin_inicial(
            db,
            email="admin@onefiancalocaticia.com.br",
            senha="senha-admin-teste",
            nome="Admin Teste",
        )

    response = client.post(
        "/v1/admin/autenticacao/login",
        json={"email": "admin@onefiancalocaticia.com.br", "senha": "senha-admin-teste"},
    )
    assert response.status_code == 200
    return str(response.json()["access_token"])
