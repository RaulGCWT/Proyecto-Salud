import os

from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
from src.auth import build_user_context, decode_verified_token, get_scoped_owner_id, require_user_context, AuthError
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

def _parse_allowed_origins():
    raw_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').strip()
    origins = [origin.strip() for origin in raw_origins.split(',') if origin.strip()]
    return origins or ['http://localhost:3000']


def _is_debug_enabled():
    return os.getenv('FLASK_DEBUG', '0').strip().lower() in {'1', 'true', 'yes', 'on'}


ALLOWED_ORIGINS = _parse_allowed_origins()
DEBUG_MODE = _is_debug_enabled()

CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})
socketio = SocketIO(app, cors_allowed_origins=ALLOWED_ORIGINS)
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
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=DEBUG_MODE,
        use_reloader=DEBUG_MODE,
        allow_unsafe_werkzeug=True
    )


@socketio.on('connect')
def handle_socket_connect(auth=None):
    token = ''

    if isinstance(auth, dict):
        token = str(auth.get('token') or auth.get('idToken') or auth.get('accessToken') or '').strip()

    if not token:
        auth_header = str(request.headers.get('Authorization') or '').strip()
        if auth_header.lower().startswith('bearer '):
            token = auth_header.split(' ', 1)[1].strip()

    if not token:
        return False

    try:
        claims = decode_verified_token(token)
        build_user_context(claims)
        return True
    except AuthError:
        return False


@app.route('/telemetry/latest', methods=['GET'])
def get_latest_telemetry_route():
    user_context, auth_error = require_user_context('dashboard:view')
    if auth_error:
        return auth_error

    telemetry = get_latest_telemetry() or {}

    return jsonify(telemetry), 200


@app.route('/telemetry/history', methods=['GET'])
def get_telemetry_history_route():
    try:
        user_context, auth_error = require_user_context('dashboard:view')
        if auth_error:
            return auth_error

        mac = str(request.args.get('mac') or '').strip().lower()
        limit = request.args.get('limit', 200)
        scoped_owner_id = get_scoped_owner_id(user_context)

        try:
            limit_value = max(1, min(int(limit), 500))
        except (TypeError, ValueError):
            limit_value = 200

        items = table_telemetry.scan().get('Items', [])
        if scoped_owner_id:
            items = [item for item in items if str(item.get('ownerId') or '') == str(scoped_owner_id)]
        if mac:
            items = [item for item in items if str(item.get('mac') or '').strip().lower() == mac]

        items.sort(key=lambda item: float(item.get('timestamp', 0)), reverse=True)
        return jsonify(items[:limit_value]), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


if __name__ == '__main__':
    main()
