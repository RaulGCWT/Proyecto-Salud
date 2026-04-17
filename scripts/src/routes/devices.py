from flask import Blueprint, jsonify, request

from src.database import table_devices

devices_bp = Blueprint('devices', __name__)


@devices_bp.route('/devices', methods=['GET', 'POST'])
def handle_devices():
    if request.method == 'POST':
        device = dict(request.json or {})
        mac = (device.get('mac') or '').strip().lower()
        fallback_id = (device.get('id') or '').strip()
        device_id = mac or fallback_id

        if not device_id:
            return jsonify({"error": "Device id is required"}), 400

        device['id'] = device_id
        device['mac'] = mac or fallback_id
        device.pop('name', None)
        table_devices.put_item(Item=device)
        return jsonify(device), 201

    response = table_devices.scan()
    return jsonify(response.get('Items', [])), 200
