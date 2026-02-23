from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Import your settings so Alembic uses DATABASE_URL from .env
from app.core.config import settings

# Alembic Config object (reads alembic.ini)
config = context.config

# Configure Python logging using alembic.ini, if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Phase 1: no models yet (we'll wire Base.metadata in Phase 2)
target_metadata = None


def get_url() -> str:
    """
    Prefer application settings so migrations work consistently
    across local/dev/prod.
    """
    return settings.database_url


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""
    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()