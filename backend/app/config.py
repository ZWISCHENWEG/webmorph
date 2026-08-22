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


settings = Settings()
