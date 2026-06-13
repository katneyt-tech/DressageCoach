from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import os

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        video_base64 = data.get('video')
        
        if not video_base64:
            return jsonify({'error': 'No video provided'}), 400
        
        # Decode video
        video_bytes = base64.b64decode(video_base64)
        
        # Simpele test: als video > 1000 bytes is goed
        if len(video_bytes) > 1000:
            score = 8.5
            warnings = ["Loodlijn: Goed"]
        else:
            score = 5.0
            warnings = ["Loodlijn: Onvoldoende"]
        
        return jsonify({
            'score': score,
            'warnings': warnings,
            'status': 'success'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Fair Dressage API is running!'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
