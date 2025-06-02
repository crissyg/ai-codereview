#!/usr/bin/env python3
"""
Complete setup script for AI-CodeReview project
"""

import os
import subprocess
import sys

def main():
    print("🚀 Setting up AI-CodeReview Project...")
    
    # Create folders
    folders = ['cache', 'logs', 'data', 'models']
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    print("📁 Project structure created")
    
    # Install packages
    packages = [
        "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",
        "tensorflow>=2.0",
        "transformers[torch,tf-cpu]",
        "datasets tokenizers accelerate",
        "fastapi uvicorn aiohttp pydantic python-dotenv",
        "pandas numpy scikit-learn"
    ]
    
    for package in packages:
        print(f"📦 Installing {package.split()[0]}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + package.split())
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("GITHUB_TOKEN=your_token_here\n")
            f.write("DEBUG=true\n")
        print("📝 Created .env file")
    
    # Verify installation
    try:
        from transformers import pipeline
        classifier = pipeline("sentiment-analysis")
        result = classifier("Setup completed successfully!")
        print(f"✅ Verification successful: {result}")
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    
    print("🎉 Setup complete! You can now use AI-CodeReview.")
    print("\nNext steps:")
    print("1. Edit .env file with your GitHub token")
    print("2. Run: python -m uvicorn backend.app.main:app --reload")
    print("3. Visit: http://localhost:8000/docs")

if __name__ == "__main__":
    main()