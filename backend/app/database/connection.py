"""
Database Connection Management

SQLAlchemy engine and session management with connection pooling.
Provides standardized database access patterns for the application.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
from typing import Generator, Optional
import logging
import os

from ..utils.config import Settings

logger = logging.getLogger(__name__)

# Base class for all ORM models
Base = declarative_base()

# Global engine and session factory
_engine = None
_session_factory = None

def get_database_engine(database_url: Optional[str] = None):
    """
    Get or create database engine with connection pooling.
    
    Args:
        database_url: Database connection string
        
    Returns:
        SQLAlchemy engine instance
    """
    global _engine
    
    if _engine is None:
        if database_url is None:
            settings = Settings()
            database_url = settings.database_url
        
        # Engine configuration based on database type
        if database_url.startswith("sqlite"):
            # SQLite-specific configuration
            connect_args = {
                "check_same_thread": False,
                "timeout": 20,
            }
            engine_kwargs = {
                "poolclass": StaticPool,
                "connect_args": connect_args,
                "echo": False,
            }
        else:
            # PostgreSQL/MySQL configuration
            engine_kwargs = {
                "pool_size": 10,
                "max_overflow": 20,
                "pool_timeout": 30,
                "pool_recycle": 3600,  # 1 hour
                "pool_pre_ping": True,
                "echo": False,
            }
        
        _engine = create_engine(database_url, **engine_kwargs)
        
        # Add connection event listeners
        _setup_engine_events(_engine)
        
        logger.info(f"Database engine created: {database_url.split('://')[0]}")
    
    return _engine

def get_session_factory():
    """Get or create session factory."""
    global _session_factory
    
    if _session_factory is None:
        engine = get_database_engine()
        _session_factory = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
        )
    
    return _session_factory

def get_db_session() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI.
    
    Provides a database session that's automatically closed
    after the request completes.
    
    Yields:
        SQLAlchemy session instance
    """
    session_factory = get_session_factory()
    db = session_factory()
    
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

async def create_tables(engine=None) -> None:
    """
    Create all database tables if they don't exist.
    
    Args:
        engine: SQLAlchemy engine (uses default if None)
    """
    if engine is None:
        engine = get_database_engine()
    
    try:
        # Import all models to ensure they're registered
        from . import schemas
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

async def drop_tables(engine=None) -> None:
    """
    Drop all database tables (use with caution).
    
    Args:
        engine: SQLAlchemy engine (uses default if None)
    """
    if engine is None:
        engine = get_database_engine()
    
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
        
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise

def close_database_connections() -> None:
    """Close all database connections and clean up resources."""
    global _engine, _session_factory
    
    if _session_factory:
        _session_factory.remove()
        _session_factory = None
    
    if _engine:
        _engine.dispose()
        _engine = None
        logger.info("Database connections closed")

def _setup_engine_events(engine) -> None:
    """Setup database engine event listeners for monitoring."""
    
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Set SQLite pragmas for better performance and reliability."""
        if engine.url.drivername == "sqlite":
            cursor = dbapi_connection.cursor()
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON")
            # Set journal mode for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL")
            # Set synchronous mode for better performance
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
    
    @event.listens_for(engine, "checkout")
    def receive_checkout(dbapi_connection, connection_record, connection_proxy):
        """Log database connection checkout."""
        logger.debug("Database connection checked out")
    
    @event.listens_for(engine, "checkin")
    def receive_checkin(dbapi_connection, connection_record):
        """Log database connection checkin."""
        logger.debug("Database connection checked in")

# Health check function
async def check_database_health() -> dict:
    """
    Perform database health check.
    
    Returns:
        Dictionary with health status information
    """
    try:
        engine = get_database_engine()
        
        # Test connection with simple query
        with engine.connect() as conn:
            result = conn.execute("SELECT 1").scalar()
            
        return {
            "status": "healthy",
            "database_type": engine.url.drivername,
            "connection_test": "passed",
            "pool_size": getattr(engine.pool, 'size', 'N/A'),
            "checked_out_connections": getattr(engine.pool, 'checkedout', 'N/A'),
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "connection_test": "failed"
        }

# Initialize database on module import for testing
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Create tables
        await create_tables()
        
        # Run health check
        health = await check_database_health()
        print(f"Database health: {health}")
    
    asyncio.run(main())