from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "one-fianca-backend"
    app_env: Literal["local", "development", "staging", "production"] = "local"
    app_debug: bool = False
    app_version: str = "0.1.0"
    app_timezone: str = "America/Sao_Paulo"

    cors_allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    trusted_hosts: str = "localhost,127.0.0.1"

    postgres_container_name: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "one"
    postgres_user: str = "one_app"
    postgres_password: SecretStr = SecretStr("local-only-change-me")
    postgres_sslmode: str = "disable"

    app_db_user: str = "one_app"
    app_db_password: SecretStr = SecretStr("local-only-change-me")
    app_database_url: str = "postgresql+psycopg://one_app:one_app_dev_password@localhost:5432/one"

    migration_db_user: str = "one_migrator"
    migration_db_password: SecretStr = SecretStr("local-only-change-me")
    migration_database_url: str | None = None

    one_api_host: str = "0.0.0.0"
    one_api_port: int = 8000
    one_api_log_level: str = "info"
    one_api_internal_token: SecretStr = SecretStr("local-dev-token")
    admin_jwt_secret: SecretStr = SecretStr("local-dev-admin-secret-change-me-32b")
    admin_jwt_expires_minutes: int = 720
    bootstrap_admin_email: str = "admin@onefiancalocaticia.com.br"
    bootstrap_admin_password: SecretStr = SecretStr("change-me")
    bootstrap_admin_full_name: str = "One Admin"

    one_mcp_host: str = "0.0.0.0"
    one_mcp_port: int = 8100
    one_mcp_auth_token: SecretStr = SecretStr("local-dev-token")

    @property
    def cors_allowed_origin_list(self) -> list[str]:
        return split_csv(self.cors_allowed_origins)

    @property
    def trusted_host_list(self) -> list[str]:
        return split_csv(self.trusted_hosts)


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
