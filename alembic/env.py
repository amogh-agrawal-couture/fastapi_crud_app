import os
import asyncio
import socket
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.engine import Connection
from dotenv import load_dotenv

from app.models import Base  # import ALL models


# ------------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------------
load_dotenv()

# If a full DATABASE_URL is provided, prefer it (useful for external tooling)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB")

    if not all([
        POSTGRES_USER,
        POSTGRES_PASSWORD,
        POSTGRES_HOST,
        POSTGRES_PORT,
        POSTGRES_DB,
    ]):
        raise RuntimeError("Missing PostgreSQL environment variables")

    # Try resolving the configured host. If it's not resolvable from the machine
    # running alembic (for example `postgres_db` only exists inside Docker),
    # fall back to localhost so local migrations can still run.
    try:
        socket.getaddrinfo(POSTGRES_HOST, POSTGRES_PORT)
    except OSError:
        # Only fallback if the host is not already a loopback
        if POSTGRES_HOST not in ("localhost", "127.0.0.1"):
            # Prefer explicit fallback env var if provided, otherwise localhost
            POSTGRES_HOST = os.getenv("ALEMBIC_DB_FALLBACK_HOST", "localhost")

    DATABASE_URL = (
        f"postgresql+asyncpg://{POSTGRES_USER}:"
        f"{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:"
        f"{POSTGRES_PORT}/"
        f"{POSTGRES_DB}"
    )
print(f"DEBUG: Connecting to: {DATABASE_URL}")

# ------------------------------------------------------------------
# Alembic Config
# ------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# ------------------------------------------------------------------
# Offline migrations
# ------------------------------------------------------------------
def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ------------------------------------------------------------------
# Online migrations (async → sync bridge)
# ------------------------------------------------------------------
def run_migrations_online() -> None:
    # Convert async URL to sync URL for migrations
    sync_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    config.set_main_option("sqlalchemy.url", sync_url)

    connectable = config.attributes.get("connection", None)

    if connectable is None:
        from sqlalchemy import create_engine
        connectable = create_engine(sync_url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

# ------------------------------------------------------------------
# Entrypoint
# ------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
