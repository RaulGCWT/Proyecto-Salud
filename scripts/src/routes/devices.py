import time

from flask import Blueprint, jsonify, request

from src.auth import require_user_context
from src.database import table_devices
from src.mqtt_handler import build_device_command_topic, publish_device_command

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
        'telemetryTopic': (payload.get('telemetryTopic') or existing.get('telemetryTopic') or '').strip(),
        'commandTopic': (payload.get('commandTopic') or existing.get('commandTopic') or '').strip(),
        'statusTopic': (payload.get('statusTopic') or existing.get('statusTopic') or '').strip(),
        'ownerId': (payload.get('ownerId') or existing.get('ownerId') or '').strip(),
        'tenantKey': (payload.get('tenantKey') or existing.get('tenantKey') or '').strip(),
        'residenceId': (payload.get('residenceId') or existing.get('residenceId') or '').strip(),
        'area': (payload.get('area') or existing.get('area') or '').strip(),
        'residentId': (payload.get('residentId') or existing.get('residentId') or '').strip()
    }


def _normalize_device_id(value):
    return str(value or '').strip().lower()


def _normalize_mode_payload(payload=None):
    payload = payload or {}
    mode = str(payload.get('mode') or '').strip().lower()

    try:
        duration_seconds = int(payload.get('durationSeconds', 30))
    except (TypeError, ValueError):
        duration_seconds = 30

    return {
        'mode': mode,
        'durationSeconds': max(5, min(duration_seconds, 300)),
    }


@devices_bp.route('/devices', methods=['GET', 'POST'])
def handle_devices():
    if request.method == 'POST':
        user_context, auth_error = require_user_context('devices:edit')
        if auth_error:
            return auth_error

        device = dict(request.json or {})
        mac = (device.get('mac') or '').strip().lower()
        fallback_id = (device.get('id') or '').strip()
        device_id = mac or fallback_id

        if not device_id:
            return jsonify({"error": "Device id is required"}), 400

        device = _normalize_device_fields(payload=device, device_id=device_id)
        if not device.get('ownerId'):
            device['ownerId'] = str(user_context.get('email') or user_context.get('tenantKey') or user_context.get('sub') or '').strip()
        table_devices.put_item(Item=device)
        return jsonify(device), 201

    user_context, auth_error = require_user_context('devices:view')
    if auth_error:
        return auth_error

    response = table_devices.scan()
    items = response.get('Items', [])
    if not items:
        return jsonify([]), 200

    return jsonify(items), 200


@devices_bp.route('/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    user_context, auth_error = require_user_context('devices:edit')
    if auth_error:
        return auth_error

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
    if not item.get('ownerId'):
        item['ownerId'] = str(user_context.get('email') or user_context.get('tenantKey') or user_context.get('sub') or '').strip()

    table_devices.put_item(Item=item)
    return jsonify(item), 200


@devices_bp.route('/devices/<device_id>/stream-mode', methods=['POST'])
def set_device_stream_mode(device_id):
    user_context, auth_error = require_user_context('devices:edit')
    if auth_error:
        return auth_error

    current_id = _normalize_device_id(device_id)
    if not current_id:
        return jsonify({"error": "Device id is required"}), 400

    device = table_devices.get_item(Key={'id': current_id}).get('Item') or {}
    if not device:
        return jsonify({"error": "Device not found"}), 404

    normalized_payload = _normalize_mode_payload(request.json or {})
    mode = normalized_payload['mode']
    if mode not in {'normal', 'realtime'}:
        return jsonify({"error": "Mode must be 'normal' or 'realtime'"}), 400

    command_topic = build_device_command_topic(device)
    if not command_topic:
        return jsonify({"error": "Device command topic is not available"}), 409

    command_payload = {
        'type': 'set_stream_mode',
        'mode': mode,
        'durationSeconds': normalized_payload['durationSeconds'],
        'requestedAt': int(time.time()),
        'requestedBy': str(
            user_context.get('email')
            or user_context.get('tenantKey')
            or user_context.get('sub')
            or ''
        ).strip(),
    }

    try:
        publish_device_command(command_topic, command_payload)
        return jsonify({
            "ok": True,
            "deviceId": device.get('deviceId') or current_id,
            "mac": device.get('mac') or current_id,
            "mode": mode,
            "durationSeconds": normalized_payload['durationSeconds'],
            "commandTopic": command_topic,
        }), 200
    except Exception as error:
        return jsonify({"error": f"Could not publish device command: {error}"}), 502
