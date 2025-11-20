#!/bin/bash
# Run script for AI Tutor Backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Flask application
python app.py


