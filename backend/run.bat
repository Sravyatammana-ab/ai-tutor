@echo off
REM Run script for AI Tutor Backend (Windows)

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run Flask application
python app.py


