from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from database import init_db, decimal_default
from mqtt_handler import start_mqtt
from routes.devices import devices_bp
from routes.events import events_bp
from routes.rules import rules_bp
from routes.users import users_bp

app = Flask(__name__)
app.json_provider_class.default = staticmethod(decimal_default)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")
app.register_blueprint(devices_bp)
app.register_blueprint(events_bp)
app.register_blueprint(rules_bp)
app.register_blueprint(users_bp)

if __name__ == '__main__':
    init_db()
    start_mqtt(socketio)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
