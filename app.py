from flask import Flask, request, jsonify
from analysis_logic import analyseer_loodlijn

app = Flask(__name__)

@app.route('/analyseer', methods=['POST'])
def analyseer():
    # Dit stukje code haalt de data uit je app
    data = request.json
    hoek = data.get('hoek', 0) # De app stuurt de gemeten hoek mee
    
    # We roepen onze slimme logica aan
    resultaat = analyseer_loodlijn(hoek)
    
    return jsonify(resultaat)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
