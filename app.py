from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Fair Dressage API running!'}), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        if not data or 'video' not in data:
            return jsonify({'error': 'No video'}), 400
        
        # SIMPELE test: geef altijd score 8.5
        return jsonify({
            'score': 8.5,
            'warnings': ['✓ Test - API werkt!'],
            'status': 'success'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
