"""fase 1 cadastros

Revision ID: 0002_fase_1_cadastros
Revises: 0001_enable_pgcrypto
Create Date: 2026-05-20 00:00:01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_fase_1_cadastros"
down_revision: str | None = "0001_enable_pgcrypto"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def uuid_pk() -> sa.Column[sa.UUID]:
    return sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("uuidv7()"))


def timestamps() -> list[sa.Column[sa.DateTime]]:
    return [
        sa.Column(
            "criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("removido_em", sa.DateTime(timezone=True), nullable=True),
    ]


def origem_columns() -> list[sa.Column[sa.String]]:
    return [
        sa.Column(
            "origem",
            sa.String(length=30),
            nullable=False,
            server_default="site",
        ),
        sa.Column("origem_nome", sa.String(length=120), nullable=True),
        sa.Column("origem_usuario_id", sa.Uuid(), nullable=True),
        sa.Column("utm_source", sa.String(length=120), nullable=True),
        sa.Column("utm_medium", sa.String(length=120), nullable=True),
        sa.Column("utm_campaign", sa.String(length=120), nullable=True),
        sa.Column("utm_content", sa.String(length=200), nullable=True),
        sa.Column("utm_term", sa.String(length=200), nullable=True),
    ]


def origem_checks(table_name: str) -> None:
    op.create_check_constraint(
        f"ck_{table_name}_origem",
        table_name,
        "origem IN ('site','chatbot','one','app_interno','api','importacao','outro')",
    )


def status_checks(table_name: str) -> None:
    op.create_check_constraint(
        f"ck_{table_name}_status",
        table_name,
        "status IN ('pendente','ativo','inativo','rejeitado')",
    )


def upgrade() -> None:
    op.create_table(
        "usuarios_admin",
        uuid_pk(),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("ultimo_login_em", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.UniqueConstraint("email", name="uq_usuarios_admin_email"),
    )
    op.create_index("ix_usuarios_admin_email", "usuarios_admin", ["email"])

    op.create_table(
        "imobiliarias",
        uuid_pk(),
        sa.Column("razao_social", sa.String(length=220), nullable=False),
        sa.Column("nome_fantasia", sa.String(length=220), nullable=False),
        sa.Column("cnpj", sa.String(length=18), nullable=False),
        sa.Column("whatsapp", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("endereco", sa.Text(), nullable=False),
        sa.Column("cidades_ufs_atuacao", sa.JSON(), nullable=False),
        sa.Column("responsavel_principal", sa.String(length=200), nullable=False),
        sa.Column("cargo_responsavel", sa.String(length=120), nullable=False),
        sa.Column("site", sa.String(length=300), nullable=True),
        sa.Column("instagram", sa.String(length=120), nullable=True),
        sa.Column("media_locacoes_mes", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pendente"),
        sa.Column("observacoes_internas", sa.Text(), nullable=True),
        sa.Column("aceite_lgpd", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("opt_in_marketing", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        *origem_columns(),
        sa.Column("token_cadastro_hash", sa.String(length=64), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["origem_usuario_id"], ["usuarios_admin.id"]),
        sa.UniqueConstraint("cnpj", name="uq_imobiliarias_cnpj"),
        sa.UniqueConstraint("token_cadastro_hash", name="uq_imobiliarias_token_cadastro_hash"),
    )
    op.create_index("ix_imobiliarias_cnpj", "imobiliarias", ["cnpj"])
    op.create_index("ix_imobiliarias_email", "imobiliarias", ["email"])
    op.create_index("ix_imobiliarias_origem", "imobiliarias", ["origem"])
    op.create_index("ix_imobiliarias_status", "imobiliarias", ["status"])
    op.create_index("ix_imobiliarias_whatsapp", "imobiliarias", ["whatsapp"])
    origem_checks("imobiliarias")
    status_checks("imobiliarias")

    op.create_table(
        "corretores",
        uuid_pk(),
        sa.Column("nome_completo", sa.String(length=220), nullable=False),
        sa.Column("cpf", sa.String(length=14), nullable=False),
        sa.Column("creci", sa.String(length=40), nullable=False),
        sa.Column("whatsapp", sa.String(length=30), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("cidade", sa.String(length=120), nullable=False),
        sa.Column("uf", sa.String(length=2), nullable=False),
        sa.Column("tipo_corretor", sa.String(length=40), nullable=False, server_default="autonomo"),
        sa.Column("perfil_profissional", sa.Text(), nullable=True),
        sa.Column("imobiliaria_vinculada_id", sa.Uuid(), nullable=True),
        sa.Column("volume_indicacoes", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pendente"),
        sa.Column("observacoes_internas", sa.Text(), nullable=True),
        sa.Column("aceite_lgpd", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("opt_in_marketing", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        *origem_columns(),
        sa.Column("token_cadastro_hash", sa.String(length=64), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["imobiliaria_vinculada_id"], ["imobiliarias.id"]),
        sa.ForeignKeyConstraint(["origem_usuario_id"], ["usuarios_admin.id"]),
        sa.UniqueConstraint("cpf", name="uq_corretores_cpf"),
        sa.UniqueConstraint("token_cadastro_hash", name="uq_corretores_token_cadastro_hash"),
    )
    op.create_index("ix_corretores_cpf", "corretores", ["cpf"])
    op.create_index("ix_corretores_email", "corretores", ["email"])
    op.create_index("ix_corretores_origem", "corretores", ["origem"])
    op.create_index("ix_corretores_status", "corretores", ["status"])
    op.create_index("ix_corretores_whatsapp", "corretores", ["whatsapp"])
    origem_checks("corretores")
    status_checks("corretores")
    op.create_check_constraint(
        "ck_corretores_tipo_corretor",
        "corretores",
        "tipo_corretor IN ('autonomo','vinculado_imobiliaria','consultor','outro')",
    )
    op.create_check_constraint(
        "ck_corretores_autonomo_sem_imobiliaria",
        "corretores",
        "tipo_corretor <> 'autonomo' OR imobiliaria_vinculada_id IS NULL",
    )

    op.create_table(
        "corretor_imobiliaria_vinculos",
        uuid_pk(),
        sa.Column("corretor_id", sa.Uuid(), nullable=False),
        sa.Column("imobiliaria_id", sa.Uuid(), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("principal", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        *timestamps(),
        sa.ForeignKeyConstraint(["corretor_id"], ["corretores.id"]),
        sa.ForeignKeyConstraint(["imobiliaria_id"], ["imobiliarias.id"]),
        sa.UniqueConstraint(
            "corretor_id", "imobiliaria_id", name="uq_vinculo_corretor_imobiliaria"
        ),
    )
    op.create_index(
        "ix_corretor_imobiliaria_vinculos_corretor_id",
        "corretor_imobiliaria_vinculos",
        ["corretor_id"],
    )
    op.create_index(
        "ix_corretor_imobiliaria_vinculos_imobiliaria_id",
        "corretor_imobiliaria_vinculos",
        ["imobiliaria_id"],
    )

    op.create_table(
        "eventos_auditoria",
        uuid_pk(),
        sa.Column("ator_tipo", sa.String(length=40), nullable=False),
        sa.Column("ator_id", sa.Uuid(), nullable=True),
        sa.Column("acao", sa.String(length=80), nullable=False),
        sa.Column("entidade_tipo", sa.String(length=80), nullable=False),
        sa.Column("entidade_id", sa.Uuid(), nullable=True),
        sa.Column("detalhes", sa.JSON(), nullable=True),
        *timestamps(),
    )
    op.create_index("ix_eventos_auditoria_entidade_tipo", "eventos_auditoria", ["entidade_tipo"])
    op.create_index("ix_eventos_auditoria_entidade_id", "eventos_auditoria", ["entidade_id"])


def downgrade() -> None:
    op.drop_table("eventos_auditoria")
    op.drop_table("corretor_imobiliaria_vinculos")
    op.drop_table("corretores")
    op.drop_table("imobiliarias")
    op.drop_table("usuarios_admin")
