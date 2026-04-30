from flask import Blueprint, jsonify, request

from src.database import table_devices

devices_bp = Blueprint('devices', __name__)


def _normalize_device_fields(existing=None, payload=None, device_id=''):
    existing = existing or {}
    payload = payload or {}
    normalized_id = (device_id or payload.get('id') or payload.get('mac') or existing.get('id') or existing.get('mac') or '').strip().lower()
    normalized_name = (payload.get('name') or existing.get('name') or payload.get('deviceId') or existing.get('deviceId') or f"Bed-{normalized_id[-5:]}").strip()
    normalized_type = (payload.get('type') or existing.get('type') or 'Standard').strip() or 'Standard'

    return {
        'id': normalized_id,
        'mac': (payload.get('mac') or existing.get('mac') or normalized_id).strip().lower(),
        'deviceId': (payload.get('deviceId') or existing.get('deviceId') or normalized_name or normalized_id).strip(),
        'name': normalized_name,
        'type': normalized_type,
        'ownerId': (payload.get('ownerId') or existing.get('ownerId') or '').strip(),
        'tenantKey': (payload.get('tenantKey') or existing.get('tenantKey') or '').strip(),
        'residenceId': (payload.get('residenceId') or existing.get('residenceId') or '').strip(),
        'area': (payload.get('area') or existing.get('area') or '').strip(),
        'residentId': (payload.get('residentId') or existing.get('residentId') or '').strip()
    }


@devices_bp.route('/devices', methods=['GET', 'POST'])
def handle_devices():
    if request.method == 'POST':
        device = dict(request.json or {})
        mac = (device.get('mac') or '').strip().lower()
        fallback_id = (device.get('id') or '').strip()
        device_id = mac or fallback_id

        if not device_id:
            return jsonify({"error": "Device id is required"}), 400

        device = _normalize_device_fields(payload=device, device_id=device_id)
        table_devices.put_item(Item=device)
        return jsonify(device), 201

    response = table_devices.scan()
    return jsonify(response.get('Items', [])), 200


@devices_bp.route('/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    current_id = (device_id or '').strip().lower()
    if not current_id:
        return jsonify({"error": "Device id is required"}), 400

    device = dict(request.json or {})
    name = (device.get('name') or '').strip()
    if not name:
      return jsonify({"error": "Device name is required"}), 400

    existing = table_devices.get_item(Key={'id': current_id}).get('Item') or {}
    item = _normalize_device_fields(existing=existing, payload=device, device_id=current_id)
    item['name'] = name

    table_devices.put_item(Item=item)
    return jsonify(item), 200
