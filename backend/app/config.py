"""
WEBMORPH Backend — Application Configuration.

All configuration is loaded from environment variables.
Secrets must NEVER be hardcoded.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "sqlite+aiosqlite:///./webmorph.db"

    @property
    def normalized_db_url(self) -> str:
        """Parses the DATABASE_URL and removes asyncpg-incompatible query parameters."""
        from sqlalchemy.engine.url import make_url

        url_obj = make_url(self.database_url)
        if url_obj.drivername in ("postgresql", "postgresql+asyncpg"):
            url_obj = url_obj.set(drivername="postgresql+asyncpg")
            query = dict(url_obj.query)
            query.pop("sslmode", None)
            query.pop("channel_binding", None)
            url_obj = url_obj.set(query=query)
        return url_obj.render_as_string(hide_password=False)

    @property
    def db_connect_args(self) -> dict:
        """Extracts SSL requirements into SQLAlchemy connection arguments."""
        from sqlalchemy.engine.url import make_url

        url_obj = make_url(self.database_url)
        if url_obj.drivername in ("postgresql", "postgresql+asyncpg"):
            query = dict(url_obj.query)
            sslmode = query.get("sslmode")
            is_ssl = sslmode in ("require", "verify-ca", "verify-full")
            is_neon = url_obj.host and "neon.tech" in url_obj.host
            if is_ssl or is_neon:
                import ssl

                return {"ssl": ssl.create_default_context()}
        return {}

    # Bright Data
    bright_data_api_token: str = ""
    bright_data_collector_id: str = ""
    bright_data_target_url: str = ""

    # CLI
    bdata_cli_path: str = "npx -y -p @brightdata/cli bdata"
    bdata_cli_timeout_seconds: int = 120
    bdata_cli_max_output_bytes: int = 5_242_880  # 5MB

    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    demo_mode: bool = False
    allowed_origins: str = "*"


settings = Settings()
