import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import get_settings  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.services.autenticacao_service import criar_ou_atualizar_admin_inicial  # noqa: E402


def main() -> None:
    settings = get_settings()
    senha = settings.bootstrap_admin_password.get_secret_value()
    with SessionLocal() as db:
        usuario = criar_ou_atualizar_admin_inicial(
            db,
            email=settings.bootstrap_admin_email,
            senha=senha,
            nome=settings.bootstrap_admin_full_name,
        )
    print(f"Admin inicial pronto: {usuario.email}")


if __name__ == "__main__":
    main()
