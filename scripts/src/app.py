from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from src.database import init_db, decimal_default
from src.mqtt_handler import start_mqtt
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
    mqtt_client = start_mqtt(socketio)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main()
