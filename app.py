from flask import Flask, request, jsonify
from analysis_logic import bereken_hoek, geef_feedback
import os

app = Flask(__name__)

@app.route('/analyseer', methods=['POST'])
def analyseer():
    # Controleer of er een bestand is meegestuurd
    if 'video' not in request.files:
        return jsonify({"fout": "Geen video gevonden"}), 400
    
    video = request.files['video']
    video_pad = "temp_video.mp4"
    video.save(video_pad)
    
    # Analyseer de video
    hoek = bereken_hoek(video_pad)
    resultaat = geef_feedback(hoek)
    
    # Verwijder tijdelijk bestand
    os.remove(video_pad)
    
    return jsonify(resultaat)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
