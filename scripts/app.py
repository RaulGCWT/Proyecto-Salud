from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import uuid
from database import init_db, table_rules, decimal_default
from mqtt_handler import start_mqtt

app = Flask(__name__)
app.json_provider_class.default = staticmethod(decimal_default)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# --- RUTAS API ---
@app.route('/rules', methods=['GET', 'POST'])
def handle_rules():
    if request.method == 'POST':
        rule = request.json
        rule['id'] = str(uuid.uuid4())
        table_rules.put_item(Item=rule)
        return jsonify(rule), 201
    return jsonify(table_rules.scan().get('Items', []))

@app.route('/rules/<rule_id>', methods=['PUT'])
def update_rule(rule_id):
    try:
        new_data = request.json
        new_data['id'] = rule_id
        table_rules.put_item(Item=new_data)
        return jsonify(new_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()        # Iniciamos DB
    start_mqtt(socketio) # Iniciamos MQTT pasando SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)