from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

from routes.upload import upload_bp
from routes.chat import chat_bp
from routes.audio import audio_bp
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS globally for all routes with specific allowed origins
allowed_origins = [
    "http://localhost:3000",
    "https://cereshikshak.cerevyn.in",
    "https://cerevyn.in",
    "https://ai-tutor-frontend-domain-if-any.com"
]

CORS(app,
     resources={r"/*": {
         "origins": allowed_origins,
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
         "expose_headers": ["Content-Type", "Content-Length"],
         "supports_credentials": True,
         "max_age": 3600
     }},
     supports_credentials=True)

# Register blueprints
app.register_blueprint(upload_bp, url_prefix='/api/upload')
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(audio_bp, url_prefix='/api/audio')

# Create necessary directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('audio', exist_ok=True)
os.makedirs('temp', exist_ok=True)

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'AI Tutor API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'upload': '/api/upload/document',
            'chat': '/api/chat',
            'audio': '/api/audio'
        }
    })

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint with CORS support"""
    return jsonify({'status': 'healthy', 'message': 'AI Tutor API is running'})

if __name__ == '__main__':
    # Disable the Werkzeug auto-reloader so changes inside the virtualenv (e.g. pip installs)
    # don't trigger endless restart loops while still keeping debug features enabled.
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)


