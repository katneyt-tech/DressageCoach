from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import tempfile
import os

app = Flask(__name__)
CORS(app)

try:
    import mediapipe as mp
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    MEDIAPIPE_AVAILABLE = True
except Exception as e:
    MEDIAPIPE_AVAILABLE = False
    print(f"MediaPipe import error: {e}")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'mediapipe': MEDIAPIPE_AVAILABLE}), 200

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
        
        # Decode video
        video_bytes = base64.b64decode(video_base64)
        
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as f:
            f.write(video_bytes)
            temp_path = f.name
        
        try:
            cap = cv2.VideoCapture(temp_path)
            
            if not cap.isOpened():
                return jsonify({'error': 'Cannot open video'}), 400
            
            frame_count = 0
            violations = 0
            detected_frames = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                if frame_count % 3 != 0:  # Skip frames
                    continue
                
                if MEDIAPIPE_AVAILABLE and frame_count <= 100:
                    # Resize
                    h, w = frame.shape[:2]
                    frame_small = cv2.resize(frame, (int(w*0.5), int(h*0.5)))
                    rgb = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)
                    
                    result = pose.process(rgb)
                    
                    if result.pose_landmarks:
                        detected_frames += 1
                        nose_x = result.pose_landmarks[0].x
                        
                        # Loodlijn check: center is 0.5
                        if nose_x < 0.45 or nose_x > 0.55:
                            violations += 1
            
            cap.release()
            os.unlink(temp_path)
            
            # Calculate score
            if detected_frames == 0:
                return jsonify({
                    'score': 0,
                    'warnings': ['Geen paard gedetecteerd'],
                    'status': 'error'
                }), 200
            
            violation_rate = (violations / detected_frames) * 100
            score = max(0, 10 - (violation_rate / 10))
            score = round(score, 1)
            
            if violation_rate > 60:
                msg = f"⚠️ Loodlijn afwijkingen: {violation_rate:.0f}%"
            elif violation_rate > 20:
                msg = f"⚠️ Enkele loodlijn afwijkingen: {violation_rate:.0f}%"
            else:
                msg = f"✓ Loodlijn: Goed ({violation_rate:.0f}%)"
            
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
        return jsonify({'error': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
