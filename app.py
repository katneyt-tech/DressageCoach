from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
import base64
import io

app = Flask(__name__)
CORS(app)

# Initialize MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Fair Dressage API is running!'}), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        video_base64 = data.get('video')
        
        if not video_base64:
            return jsonify({'error': 'No video provided'}), 400
        
        video_bytes = base64.b64decode(video_base64)
        
        temp_path = '/tmp/temp_video.mp4'
        with open(temp_path, 'wb') as f:
            f.write(video_bytes)
        
        cap = cv2.VideoCapture(temp_path)
        
        if not cap.isOpened():
            return jsonify({'error': 'Could not open video'}), 400
        
        frame_count = 0
        plumb_line_violations = 0
        horse_detected_frames = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            if frame_count % 2 != 0:
                continue
            
            height, width = frame.shape[:2]
            small_frame = cv2.resize(frame, (int(width * 0.5), int(height * 0.5)))
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            result = pose.process(rgb_frame)
            
            if result.pose_landmarks:
                horse_detected_frames += 1
                nose = result.pose_landmarks[0]
                nose_x = nose.x
                
                if nose_x < 0.45 or nose_x > 0.55:
                    plumb_line_violations += 1
            
            if frame_count > 150:
                break
        
        cap.release()
        
        if horse_detected_frames == 0:
            return jsonify({
                'score': 0,
                'warnings': ['Geen paard gedetecteerd'],
                'status': 'error'
            }), 200
        
        violation_rate = (plumb_line_violations / horse_detected_frames) * 100
        score = max(0, 10 - (violation_rate / 10))
        score = round(score, 1)
        
        warnings = []
        if violation_rate > 70:
            warnings.append(f"⚠️ Loodlijn: VEEL afwijkingen ({violation_rate:.0f}%)")
        elif violation_rate > 40:
            warnings.append(f"⚠️ Loodlijn: Enkele afwijkingen ({violation_rate:.0f}%)")
        else:
            warnings.append(f"✓ Loodlijn: Goed! ({violation_rate:.0f}%)")
        
        return jsonify({
            'score': score,
            'warnings': warnings,
            'status': 'success'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
