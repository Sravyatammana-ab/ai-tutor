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
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # For production Render/Gunicorn, app.run won't be used; still fine locally.
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
