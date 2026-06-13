from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import tempfile
import os

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Fair Dressage API'}), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        video_base64 = data.get('video')
        
        if not video_base64:
            return jsonify({'error': 'No video'}), 400
        
        video_bytes = base64.b64decode(video_base64)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as f:
            f.write(video_bytes)
            temp_path = f.name
        
        try:
            cap = cv2.VideoCapture(temp_path)
            
            if not cap.isOpened():
                return jsonify({'error': 'Cannot open video'}), 400
            
            frame_count = 0
            plumb_violations = 0
            detected_frames = 0
            
            while cap.isOpened() and frame_count < 100:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Detect center of motion
                h, w = frame.shape[:2]
                frame_small = cv2.resize(frame, (int(w*0.3), int(h*0.3)))
                
                gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (5, 5), 0)
                edges = cv2.Canny(blur, 50, 150)
                
                contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    largest = max(contours, key=cv2.contourArea)
                    M = cv2.moments(largest)
                    
                    if M['m00'] > 0:
                        detected_frames += 1
                        cx = int(M['m10'] / M['m00'])
                        w_small = frame_small.shape[1]
                        cx_norm = cx / w_small
                        
                        # Loodlijn: 0.45-0.55 is goed
                        if cx_norm < 0.45 or cx_norm > 0.55:
                            plumb_violations += 1
            
            cap.release()
            os.unlink(temp_path)
            
            if detected_frames == 0:
                return jsonify({
                    'score': 0,
                    'warnings': ['Geen object gedetecteerd'],
                    'status': 'error'
                }), 200
            
            violation_rate = (plumb_violations / detected_frames) * 100
            score = max(0, 10 - (violation_rate / 10))
            score = round(score, 1)
            
            if violation_rate > 70:
                msg = f"⚠️ VEEL afwijkingen: {violation_rate:.0f}%"
            elif violation_rate > 40:
                msg = f"⚠️ Enkele afwijkingen: {violation_rate:.0f}%"
            else:
                msg = f"✓ Loodlijn: Goed! ({violation_rate:.0f}%)"
            
            return jsonify({
                'score': score,
                'warnings': [msg],
                'violation_rate': round(violation_rate, 1),
                'status': 'success'
            }), 200
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
