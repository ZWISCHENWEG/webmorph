# Temporary migration runner for production deployments (Render)
# This script is NOT part of the application runtime.
# It is used ONLY during the initial deployment to bring the database schema
# up‑to‑date by applying Alembic migrations.
# It reads the existing Alembic configuration file (backend/alembic.ini)
# and executes `alembic upgrade head` using the DATABASE_URL env var.

import sys

from alembic import command
from alembic.config import Config


def main() -> None:
    # Load the Alembic config file located in the backend directory.
    cfg_path = "backend/alembic.ini"
    alembic_cfg = Config(cfg_path)
    # Ensure the config uses the DATABASE_URL environment variable.
    # Alembic's env.py already pulls settings.database_url, which reads the env var.
    # No further action required – just run the upgrade.
    command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    sys.exit(main())
