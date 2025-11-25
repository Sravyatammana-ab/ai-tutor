#!/usr/bin/env python3
"""
Setup script for AI Tutor Backend
This script helps set up the backend environment and dependencies
"""

import os
import sys
import subprocess

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'audio', 'temp']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_env_file():
    """Create .env file from example if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            with open('env.example', 'r') as f:
                content = f.read()
            with open('.env', 'w') as f:
                f.write(content)
            print("✓ Created .env file from env.example")
            print("⚠ Please update .env with your API keys!")
        else:
            print("⚠ env.example not found. Please create .env manually.")
    else:
        print("✓ .env file already exists")

def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        sys.exit(1)

def main():
    print("Setting up AI Tutor Backend...")
    print("-" * 50)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    install_dependencies()
    
    print("-" * 50)
    print("Setup complete!")
    print("\nNext steps:")
    print("1. Update .env with your API keys")
    print("2. Set up Supabase database (see README.md)")
    print("3. Ensure VECTOR_DB_PATH is writable (see README.md)")
    print("4. Run: python app.py")

if __name__ == '__main__':
    main()


