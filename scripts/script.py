from flask import Flask, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

@app.route('/sensor-data')
def get_data():
    return jsonify({
        "heartRate": random.randint(45, 115),
        "respiratoryRate": random.randint(8, 25),
        "hrv": random.randint(15, 80),
        "isOccupied": True
    })

if __name__ == '__main__':
    # host='0.0.0.0' es obligatorio en Docker
    app.run(host='0.0.0.0', port=5000, debug=True)