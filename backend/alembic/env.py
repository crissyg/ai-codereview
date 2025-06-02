"""
Alembic Environment Configuration

Configures Alembic for database migrations with support for both
online and offline migration modes. Handles SQLAlchemy model
discovery and database connection management.
"""

import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import os
import sys

# Add the backend directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import application models and configuration
from app.database.connection import Base
from app.utils.config import get_settings

# Alembic Config object for access to .ini file values
config = context.config

# Setup logging configuration from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = Base.metadata

def get_database_url():
    """Get database URL from application settings."""
    try:
        settings = get_settings()
        return settings.database_url
    except Exception:
        # Fallback to environment variable
        return os.getenv("DATABASE_URL", "sqlite:///ai_codereview.db")

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine.
    Calls to context.execute() emit the given string to the script output.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Run migrations with database connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in async mode for async database engines."""
    configuration = config.get_section(config.config_ini_section)
    
    # Override database URL with application settings
    configuration["sqlalchemy.url"] = get_database_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    
    Creates an Engine and associates a connection with the context.
    Supports both sync and async database engines.
    """
    database_url = get_database_url()
    
    # Check if we're using an async database URL
    if database_url.startswith(("postgresql+asyncpg://", "mysql+aiomysql://")):
        asyncio.run(run_async_migrations())
    else:
        # Synchronous migration for SQLite and other sync drivers
        configuration = config.get_section(config.config_ini_section)
        configuration["sqlalchemy.url"] = database_url
        
        connectable = context.config.attributes.get("connection", None)
        
        if connectable is None:
            from sqlalchemy import create_engine
            connectable = create_engine(
                database_url,
                poolclass=pool.NullPool,
            )

        with connectable.connect() as connection:
            do_run_migrations(connection)

# Determine which migration mode to run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()