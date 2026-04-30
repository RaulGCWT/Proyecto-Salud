from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
from src.database import init_db, decimal_default, table_telemetry
from src.mqtt_handler import start_mqtt, get_latest_telemetry
from src.storage import init_storage
from src.routes.devices import devices_bp
from src.routes.events import events_bp
from src.routes.family_users import family_users_bp
from src.routes.invites import invites_bp
from src.routes.residents import residents_bp
from src.routes.rules import rules_bp
from src.routes.staff import staff_bp

app = Flask(__name__)
app.json_provider_class.default = staticmethod(decimal_default)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
app.register_blueprint(devices_bp)
app.register_blueprint(events_bp)
app.register_blueprint(family_users_bp)
app.register_blueprint(invites_bp)
app.register_blueprint(residents_bp)
app.register_blueprint(rules_bp)
app.register_blueprint(staff_bp)


mqtt_client = None


def main():
    global mqtt_client

    init_db()
    init_storage()
    mqtt_client = start_mqtt(socketio)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)


@app.route('/telemetry/latest', methods=['GET'])
def get_latest_telemetry_route():
    return jsonify(get_latest_telemetry()), 200


@app.route('/telemetry/history', methods=['GET'])
def get_telemetry_history_route():
    try:
        owner_id = request.args.get('ownerId') or request.headers.get('X-Owner-Id') or request.headers.get('x-owner-id')
        mac = str(request.args.get('mac') or '').strip().lower()
        limit = request.args.get('limit', 200)

        try:
            limit_value = max(1, min(int(limit), 500))
        except (TypeError, ValueError):
            limit_value = 200

        items = table_telemetry.scan().get('Items', [])
        if owner_id:
            items = [item for item in items if str(item.get('ownerId') or '') == str(owner_id)]
        if mac:
            items = [item for item in items if str(item.get('mac') or '').strip().lower() == mac]

        items.sort(key=lambda item: float(item.get('timestamp', 0)), reverse=True)
        return jsonify(items[:limit_value]), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


if __name__ == '__main__':
    main()
