"""
Database Migration Helper

Manages database schema migrations using Alembic.
Provides convenient commands for creating, applying, and managing migrations.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

def setup_alembic_environment():
    """Setup Alembic environment and configuration."""
    project_root = Path(__file__).parent.parent.parent
    alembic_dir = project_root / "backend" / "alembic"
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    # Change to backend directory for Alembic commands
    backend_dir = project_root / "backend"
    os.chdir(backend_dir)
    
    return alembic_dir, backend_dir

def run_alembic_command(command: list) -> bool:
    """Run an Alembic command and handle errors."""
    try:
        result = subprocess.run(
            ["alembic"] + command,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Alembic command failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Alembic not found. Please install with: pip install alembic")
        return False

def initialize_alembic():
    """Initialize Alembic configuration if not already present."""
    alembic_dir, backend_dir = setup_alembic_environment()
    
    if not (backend_dir / "alembic.ini").exists():
        print("Initializing Alembic configuration...")
        if run_alembic_command(["init", "alembic"]):
            print("Alembic initialized successfully")
            print("Please configure your database URL in alembic.ini")
        else:
            print("Failed to initialize Alembic")
            return False
    
    return True

def create_migration(message: str, auto_generate: bool = True):
    """Create a new database migration."""
    setup_alembic_environment()
    
    print(f"Creating migration: {message}")
    
    command = ["revision"]
    if auto_generate:
        command.append("--autogenerate")
    command.extend(["-m", message])
    
    if run_alembic_command(command):
        print("Migration created successfully")
        print("Review the generated migration file before applying")
    else:
        print("Failed to create migration")

def apply_migrations(revision: Optional[str] = None):
    """Apply database migrations."""
    setup_alembic_environment()
    
    target = revision or "head"
    print(f"Applying migrations to: {target}")
    
    if run_alembic_command(["upgrade", target]):
        print("Migrations applied successfully")
    else:
        print("Failed to apply migrations")

def rollback_migration(revision: str = "-1"):
    """Rollback database migrations."""
    setup_alembic_environment()
    
    print(f"Rolling back to: {revision}")
    
    if run_alembic_command(["downgrade", revision]):
        print("Rollback completed successfully")
    else:
        print("Failed to rollback migration")

def show_migration_history():
    """Show migration history."""
    setup_alembic_environment()
    
    print("Migration history:")
    run_alembic_command(["history", "--verbose"])

def show_current_revision():
    """Show current database revision."""
    setup_alembic_environment()
    
    print("Current database revision:")
    run_alembic_command(["current"])

def check_migration_status():
    """Check if database is up to date with migrations."""
    setup_alembic_environment()
    
    print("Checking migration status...")
    
    # Get current revision
    current_result = subprocess.run(
        ["alembic", "current"],
        capture_output=True,
        text=True
    )
    
    # Get head revision
    head_result = subprocess.run(
        ["alembic", "heads"],
        capture_output=True,
        text=True
    )
    
    if current_result.returncode == 0 and head_result.returncode == 0:
        current = current_result.stdout.strip()
        head = head_result.stdout.strip()
        
        if current and head and current.split()[0] == head.split()[0]:
            print("✅ Database is up to date")
        else:
            print("⚠️  Database needs migration")
            print(f"Current: {current}")
            print(f"Head: {head}")
    else:
        print("❌ Could not check migration status")

def reset_database():
    """Reset database by dropping all tables and reapplying migrations."""
    setup_alembic_environment()
    
    print("⚠️  WARNING: This will drop all database tables!")
    confirm = input("Are you sure you want to continue? (yes/no): ")
    
    if confirm.lower() != "yes":
        print("Database reset cancelled")
        return
    
    print("Resetting database...")
    
    # Downgrade to base (drop all tables)
    if run_alembic_command(["downgrade", "base"]):
        print("All tables dropped")
        
        # Apply all migrations
        if run_alembic_command(["upgrade", "head"]):
            print("Database reset completed successfully")
        else:
            print("Failed to reapply migrations")
    else:
        print("Failed to drop tables")

def main():
    """Main CLI interface for migration management."""
    if len(sys.argv) < 2:
        print("Database Migration Helper")
        print("\nUsage: python migrate.py <command> [options]")
        print("\nCommands:")
        print("  init                     - Initialize Alembic configuration")
        print("  create <message>         - Create new migration")
        print("  create-auto <message>    - Create auto-generated migration")
        print("  apply [revision]         - Apply migrations (default: head)")
        print("  rollback [revision]      - Rollback migrations (default: -1)")
        print("  history                  - Show migration history")
        print("  current                  - Show current revision")
        print("  status                   - Check migration status")
        print("  reset                    - Reset database (dangerous!)")
        print("\nExamples:")
        print("  python migrate.py create-auto 'Add user table'")
        print("  python migrate.py apply")
        print("  python migrate.py rollback")
        return
    
    command = sys.argv[1]
    
    try:
        if command == "init":
            initialize_alembic()
        
        elif command == "create":
            if len(sys.argv) < 3:
                print("Please provide a migration message")
                return
            create_migration(sys.argv[2], auto_generate=False)
        
        elif command == "create-auto":
            if len(sys.argv) < 3:
                print("Please provide a migration message")
                return
            create_migration(sys.argv[2], auto_generate=True)
        
        elif command == "apply":
            revision = sys.argv[2] if len(sys.argv) > 2 else None
            apply_migrations(revision)
        
        elif command == "rollback":
            revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
            rollback_migration(revision)
        
        elif command == "history":
            show_migration_history()
        
        elif command == "current":
            show_current_revision()
        
        elif command == "status":
            check_migration_status()
        
        elif command == "reset":
            reset_database()
        
        else:
            print(f"Unknown command: {command}")
            print("Run 'python migrate.py' for help")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()