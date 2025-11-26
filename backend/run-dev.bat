@echo off
REM Development run script for AI Tutor Backend (Windows)
REM This enables auto-reload - changes to Python files will automatically restart the server

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Set development environment variable
set FLASK_ENV=development
set FLASK_DEBUG=1

REM Run Flask application with auto-reload
echo Starting Flask server in DEVELOPMENT mode with auto-reload...
echo Changes to Python files will automatically restart the server.
echo Press Ctrl+C to stop.
echo.
python app.py

