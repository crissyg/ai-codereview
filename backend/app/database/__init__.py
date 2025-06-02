"""
Database Package

Database connection management, ORM models, and migration utilities
for persistent data storage in the AI-CodeReview system.

Components:
- Connection: SQLAlchemy engine and session management
- Schemas: Database table definitions and relationships
- Migrations: Alembic migration scripts and utilities
"""

from .connection import (
    get_database_engine,
    get_db_session,
    create_tables,
    close_database_connections
)

from .schemas import (
    Base,
    AnalysisRecord,
    RepositoryRecord,
    UserRecord,
    WebhookEvent as WebhookEventRecord
)

# Export database components
__all__ = [
    # Connection management
    "get_database_engine",
    "get_db_session", 
    "create_tables",
    "close_database_connections",
    
    # ORM models
    "Base",
    "AnalysisRecord",
    "RepositoryRecord", 
    "UserRecord",
    "WebhookEventRecord",
]

# Database configuration
DATABASE_CONFIG = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 3600,  # 1 hour
    "echo_sql": False,     # Set to True for SQL debugging
}

# Migration configuration
MIGRATION_CONFIG = {
    "script_location": "alembic",
    "version_table": "alembic_version",
    "version_locations": ["alembic/versions"],
}

async def initialize_database(database_url: str = None) -> bool:
    """
    Initialize database connection and create tables if needed.
    
    Args:
        database_url: Database connection string
        
    Returns:
        True if initialization successful, False otherwise
    """
    try:
        # Create database engine
        engine = get_database_engine(database_url)
        
        # Create tables if they don't exist
        await create_tables(engine)
        
        return True
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False

def get_database_info() -> dict:
    """Get database configuration and status information."""
    return {
        "config": DATABASE_CONFIG,
        "migration_config": MIGRATION_CONFIG,
        "available_models": [
            "AnalysisRecord",
            "RepositoryRecord", 
            "UserRecord",
            "WebhookEventRecord"
        ],
    }

async def health_check() -> dict:
    """Perform database health check."""
    try:
        # Test database connection
        db = get_db_session()
        
        # Simple query to test connection
        result = db.execute("SELECT 1").scalar()
        db.close()
        
        return {
            "status": "healthy",
            "connection": "active",
            "query_test": "passed"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "connection": "failed"
        }