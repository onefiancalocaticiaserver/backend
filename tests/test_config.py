from app.core.config import get_settings


def test_csv_environment_values_are_split(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://a.example,https://b.example")

    try:
        settings = get_settings()
        assert settings.cors_allowed_origin_list == ["https://a.example", "https://b.example"]
    finally:
        get_settings.cache_clear()
