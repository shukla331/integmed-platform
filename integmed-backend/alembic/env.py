import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import target metadata from the application's models
try:
    from app.models.database import Base
    target_metadata = Base.metadata
except Exception:
    target_metadata = None


def get_database_url() -> str:
    # Prefer explicit DATABASE_URL env var, fallback to app config
    env_url = os.getenv('DATABASE_URL')
    if env_url:
        return env_url
    # Attempt to read from app core config
    try:
        from app.core.config import settings
        return settings.DATABASE_URL
    except Exception:
        return 'postgresql://integmed:password@localhost:5432/integmed'


def run_migrations_offline() -> None:
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # set sqlalchemy.url in config from environment
    db_url = get_database_url()
    config.set_main_option('sqlalchemy.url', db_url)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
