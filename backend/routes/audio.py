from flask import Blueprint, send_file
import os
from config import Config

audio_bp = Blueprint('audio', __name__)

@audio_bp.route('/<filename>', methods=['GET'])
def get_audio(filename):
    """
    Serve audio files
    """
    try:
        audio_path = os.path.join(Config.AUDIO_FOLDER, filename)
        if os.path.exists(audio_path):
            return send_file(audio_path, mimetype='audio/mpeg')
        else:
            return {'error': 'Audio file not found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500


