#!/bin/bash
# Development run script for AI Tutor Backend
# This enables auto-reload - changes to Python files will automatically restart the server

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set development environment variables
export FLASK_ENV=development
export FLASK_DEBUG=1

# Run Flask application with auto-reload
echo "Starting Flask server in DEVELOPMENT mode with auto-reload..."
echo "Changes to Python files will automatically restart the server."
echo "Press Ctrl+C to stop."
echo ""
python app.py

