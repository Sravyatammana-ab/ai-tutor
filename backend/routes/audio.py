from flask import Blueprint, send_file
import os
from config import Config

audio_bp = Blueprint('audio', __name__)

@audio_bp.route('/<filename>', methods=['GET'])
def get_audio(filename):
    """
    Serve audio files with proper range request support for streaming
    """
    try:
        audio_path = os.path.join(Config.AUDIO_FOLDER, filename)
        if not os.path.exists(audio_path):
            return {'error': 'Audio file not found'}, 404
        
        # Use send_file which automatically handles range requests (206 Partial Content)
        # This is perfect for audio streaming - browsers will request byte ranges
        return send_file(
            audio_path,
            mimetype='audio/mpeg',
            as_attachment=False,  # Stream, don't force download
            conditional=True  # Enable conditional requests (ETag, Last-Modified)
        )
    except Exception as e:
        return {'error': str(e)}, 500


