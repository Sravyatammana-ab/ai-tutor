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

# Enable CORS for frontend
CORS(app, resources={r"/*": {"origins": "*"}})

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

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'AI Tutor API is running'})

if __name__ == '__main__':
    # Disable the Werkzeug auto-reloader so changes inside the virtualenv (e.g. pip installs)
    # don't trigger endless restart loops while still keeping debug features enabled.
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)


