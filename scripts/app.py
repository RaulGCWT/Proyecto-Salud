from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import uuid
import secrets
from datetime import datetime, timezone
from database import init_db, table_rules, table_events, table_devices, table_invites, table_family_users, table_residents, table_staff_members, decimal_default
from mqtt_handler import start_mqtt

app = Flask(__name__)
app.json_provider_class.default = staticmethod(decimal_default)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def upsert_item(table, payload):
    item = dict(payload or {})
    item['id'] = item.get('id') or str(uuid.uuid4())
    table.put_item(Item=item)
    return item


@app.route('/devices', methods=['GET', 'POST'])
def handle_devices():
    if request.method == 'POST':
        device = dict(request.json or {})
        device_id = device.get('id') or device.get('mac')

        if not device_id:
            return jsonify({"error": "Device id is required"}), 400

        device['id'] = device_id
        device.pop('mac', None)
        table_devices.put_item(Item=device)
        return jsonify(device), 201

    response = table_devices.scan()
    return jsonify(response.get('Items', [])), 200


@app.route('/staff-members', methods=['GET', 'POST'])
def handle_staff_members():
    if request.method == 'POST':
        staff_member = upsert_item(table_staff_members, request.json)
        return jsonify(staff_member), 201

    response = table_staff_members.scan()
    return jsonify(response.get('Items', [])), 200


@app.route('/residents', methods=['GET', 'POST'])
def handle_residents():
    if request.method == 'POST':
        resident = upsert_item(table_residents, request.json)
        return jsonify(resident), 201

    response = table_residents.scan()
    return jsonify(response.get('Items', [])), 200


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


@app.route('/events', methods=['GET'])
def get_events():
    try:
        response = table_events.scan()
        items = response.get('Items', [])
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
        return jsonify({"status": "cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/invites', methods=['GET', 'POST'])
def handle_invites():
    if request.method == 'POST':
        invite = dict(request.json or {})

        if not invite.get('email') or not invite.get('name'):
            return jsonify({"error": "Invite name and email are required"}), 400

        invite_id = str(uuid.uuid4())
        token = secrets.token_urlsafe(24)
        created_at = utc_now_iso()
        invitation = {
            'id': invite_id,
            'token': token,
            'email': invite.get('email'),
            'name': invite.get('name'),
            'relationship': invite.get('relationship', ''),
            'residentId': invite.get('residentId'),
            'patientName': invite.get('patientName', 'Unassigned'),
            'deviceId': invite.get('deviceId', ''),
            'state': 'PENDING',
            'createdAt': created_at,
            'acceptedAt': None,
            'history': [
                {
                    'status': 'PENDING',
                    'date': created_at
                }
            ]
        }

        table_invites.put_item(Item=invitation)

        accept_url = f"http://localhost:3000/accept-invite?token={token}"

        response_payload = {
            **invitation,
            'acceptUrl': accept_url
        }
        return jsonify(response_payload), 201

    response = table_invites.scan()
    return jsonify(response.get('Items', [])), 200


@app.route('/invites/verify', methods=['GET'])
def verify_invite():
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Token is required"}), 400

    items = table_invites.scan().get('Items', [])
    invitation = next((item for item in items if item.get('token') == token), None)

    if not invitation or invitation.get('state') not in ['PENDING', 'ACCEPTED']:
        return jsonify({"error": "Invitation not found"}), 404

    return jsonify(invitation), 200


@app.route('/invites/accept', methods=['POST'])
def accept_invite():
    token = (request.json or {}).get('token')
    if not token:
        return jsonify({"error": "Token is required"}), 400

    items = table_invites.scan().get('Items', [])
    invitation = next((item for item in items if item.get('token') == token), None)

    if not invitation:
        return jsonify({"error": "Invitation not found"}), 404

    if invitation.get('state') == 'ACCEPTED':
        return jsonify(invitation), 200

    accepted_at = utc_now_iso()
    invitation['state'] = 'ACCEPTED'
    invitation['acceptedAt'] = accepted_at
    invitation['history'] = invitation.get('history', []) + [{
        'status': 'ACCEPTED',
        'date': accepted_at
    }]
    table_invites.put_item(Item=invitation)

    return jsonify(invitation), 200


@app.route('/invites/register', methods=['POST'])
def register_from_invite():
    payload = dict(request.json or {})
    token = payload.get('token')
    password = payload.get('password')
    name = payload.get('name')

    if not token or not password or not name:
        return jsonify({"error": "Token, name and password are required"}), 400

    items = table_invites.scan().get('Items', [])
    invitation = next((item for item in items if item.get('token') == token), None)

    if not invitation:
        return jsonify({"error": "Invitation not found"}), 404

    if invitation.get('state') == 'ACCEPTED':
        return jsonify({"error": "Invitation already used"}), 409

    user = {
        'id': str(uuid.uuid4()),
        'email': invitation.get('email'),
        'name': name,
        'password': password,
        'role': 'family',
        'state': 'Active',
        'residentId': invitation.get('residentId'),
        'relationship': invitation.get('relationship', ''),
        'patientName': invitation.get('patientName', 'Unassigned'),
        'deviceId': invitation.get('deviceId', ''),
        'deviceIdOverride': '',
        'invitationId': invitation.get('id'),
        'createdAt': utc_now_iso()
    }
    table_family_users.put_item(Item=user)

    accepted_at = utc_now_iso()
    invitation['name'] = name
    invitation['state'] = 'ACCEPTED'
    invitation['acceptedAt'] = accepted_at
    invitation['history'] = invitation.get('history', []) + [{
        'status': 'REGISTERED',
        'date': accepted_at
    }]
    table_invites.put_item(Item=invitation)

    return jsonify({
        "status": "registered",
        "user": {
            "id": user['id'],
            "email": user['email'],
            "name": user['name'],
            "role": user['role']
        }
    }), 201


@app.route('/family-users', methods=['GET'])
def get_family_users():
    response = table_family_users.scan()
    return jsonify(response.get('Items', [])), 200


@app.route('/family-users/<family_user_id>', methods=['PUT'])
def update_family_user(family_user_id):
    payload = dict(request.json or {})
    items = table_family_users.scan().get('Items', [])
    family_user = next((item for item in items if item.get('id') == family_user_id), None)

    if not family_user:
        return jsonify({"error": "Family user not found"}), 404

    updated_user = {
        **family_user,
        **payload,
        'id': family_user_id
    }
    table_family_users.put_item(Item=updated_user)
    return jsonify(updated_user), 200


if __name__ == '__main__':
    init_db()
    start_mqtt(socketio)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
