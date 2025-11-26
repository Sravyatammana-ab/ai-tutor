import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes.upload import upload_bp
from routes.chat import chat_bp
from routes.audio import audio_bp

app = Flask(__name__)
app.config.from_object(Config)

# parse allowed origins in config (list or "*")
allowed_origins = Config.FRONTEND_ALLOWED_ORIGINS

# Use Flask-CORS only (no after_request manual headers)
CORS(app,
     resources={r"/*": {"origins": allowed_origins}},
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
    return jsonify({'status': 'healthy', 'message': 'AI Tutor API is running'})

@app.route('/api/debug/config', methods=['GET'])
def debug_config():
    """Debug endpoint to check environment variables (without exposing sensitive values)"""
    import os
    from config import Config
    
    return jsonify({
        'azure_endpoint_set': bool(Config.AZURE_ENDPOINT),
        'azure_endpoint_preview': Config.AZURE_ENDPOINT[:50] + '...' if Config.AZURE_ENDPOINT and len(Config.AZURE_ENDPOINT) > 50 else (Config.AZURE_ENDPOINT if Config.AZURE_ENDPOINT else None),
        'azure_key_set': bool(Config.AZURE_KEY),
        'azure_key_length': len(Config.AZURE_KEY) if Config.AZURE_KEY else 0,
        'env_azure_endpoint': bool(os.getenv('AZURE_ENDPOINT')),
        'env_azure_key': bool(os.getenv('AZURE_KEY')),
    })
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # Enable auto-reload in development (set FLASK_ENV=development or FLASK_DEBUG=1)
    is_development = os.environ.get("FLASK_ENV") == "development" or os.environ.get("FLASK_DEBUG") == "1"
    
    # For production Render/Gunicorn, app.run won't be used; still fine locally.
    # In development, enable debug mode and auto-reloader for hot-reloading
    app.run(
        debug=is_development,
        host='0.0.0.0',
        port=port,
        use_reloader=is_development  # Auto-reload on file changes
    )
