"""Alembic environment configuration for async SQLAlchemy migrations."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import settings

# Import Base and all models so they are registered with metadata
from app.models.base import Base
from app.models import (  # noqa: F401
    Battle,
    BattleAction,
    Card,
    CardAbility,
    CardAttack,
    CardFunction,
    CardSet,
    CardUsageStats,
    Deck,
    DeckCard,
    DeckUsageStats,
    MetaDeck,
    MetaDeckCard,
    MetaMatchup,
    NewsArticle,
    Tournament,
    User,
    UserCollection,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata target for 'autogenerate' support
target_metadata = Base.metadata


def get_sync_url() -> str:
    """Convert the async DATABASE_URL to a synchronous one for Alembic.

    Replaces 'postgresql+asyncpg://' with 'postgresql://' so that
    Alembic can use a standard synchronous psycopg2 driver.
    """
    url = settings.DATABASE_URL
    return url.replace("postgresql+asyncpg://", "postgresql://")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_sync_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we create a synchronous Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_sync_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
