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
allowed_origins = Config.FRONTEND_ALLOWED_ORIGINS

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


@app.after_request
def add_cors_headers(response):
    """Ensure every response carries the necessary CORS headers."""
    origin = request.headers.get('Origin')
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Vary'] = 'Origin'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
    return response

if __name__ == '__main__':
    # Bind to Render-provided PORT (defaults to 5000 locally) with debug disabled for production
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)


