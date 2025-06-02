"""
Development Server Runner

Starts the FastAPI development server with hot reload and debug features.
Handles environment setup and provides convenient development configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import uvicorn
        import fastapi
        return True
    except ImportError as e:
        print(f"Missing required dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def setup_environment():
    """Setup development environment variables and paths."""
    # Add project root to Python path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    # Set development environment variables
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("DEBUG", "true")
    os.environ.setdefault("LOG_LEVEL", "DEBUG")
    
    # Create necessary directories
    cache_dir = project_root / "cache"
    logs_dir = project_root / "logs"
    cache_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    
    print("Development environment configured")

def run_development_server():
    """Start the FastAPI development server with optimal settings."""
    if not check_dependencies():
        sys.exit(1)
    
    setup_environment()
    
    try:
        import uvicorn
        
        print("Starting AI-CodeReview development server...")
        print("Server will be available at: http://localhost:8000")
        print("API documentation at: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server")
        
        uvicorn.run(
            "backend.app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,           # Enable hot reload for development
            reload_dirs=["backend"],  # Watch backend directory for changes
            debug=True,            # Enable debug mode
            log_level="debug",     # Verbose logging
            access_log=True,       # Log all requests
            use_colors=True,       # Colored console output
        )
        
    except KeyboardInterrupt:
        print("\nDevelopment server stopped")
    except Exception as e:
        print(f"Failed to start development server: {e}")
        sys.exit(1)

def install_dependencies():
    """Install required dependencies if missing."""
    print("Installing required dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", "requirements.txt"
        ])
        print("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install dependencies")
        return False

def main():
    """Main entry point with dependency checking and installation."""
    if not check_dependencies():
        print("Attempting to install missing dependencies...")
        if install_dependencies():
            print("Dependencies installed. Starting server...")
        else:
            print("Please manually install dependencies and try again")
            sys.exit(1)
    
    run_development_server()

if __name__ == "__main__":
    main()