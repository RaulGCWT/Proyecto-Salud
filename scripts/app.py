from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import uuid
from database import init_db, table_rules, table_events, decimal_default
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

@app.route('/rules/<rule_id>', methods=['PUT', 'DELETE'])
def handle_rule_operations(rule_id):
    if request.method == 'PUT':
        new_data = request.json
        new_data['id'] = rule_id
        table_rules.put_item(Item=new_data)
        return jsonify(new_data), 200
    
    if request.method == 'DELETE':
        table_rules.delete_item(Key={'id': rule_id})
        return jsonify({"status": "deleted"}), 200

# NUEVA RUTA: Obtener historial de alertas de la DB
@app.route('/events', methods=['GET'])
def get_events():
    try:
        response = table_events.scan()
        items = response.get('Items', [])
        # Ordenamos por timestamp (más reciente primero)
        items.sort(key=lambda x: float(x.get('timestamp', 0)), reverse=True)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/events/clear', methods=['DELETE'])
def clear_all_events():
    try:
        items = table_events.scan().get('Items', [])
        with table_events.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={'id': item['id']})
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    start_mqtt(socketio)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)