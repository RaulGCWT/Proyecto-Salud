from flask import Blueprint, jsonify, request

from src.auth import require_user_context
from src.database import scan_all
from src.database import table_devices, table_residents
from src.services.common import upsert_item

residents_bp = Blueprint('residents', __name__)


def _normalize_text(value):
    return str(value or '').strip()


def _normalize_device_id(value):
    return _normalize_text(value).lower()


def _sync_resident_device_assignment(previous_device_id='', next_device_id='', resident_id=''):
    previous_device_id = _normalize_device_id(previous_device_id)
    next_device_id = _normalize_device_id(next_device_id)
    resident_id = _normalize_text(resident_id)

    if previous_device_id and previous_device_id != next_device_id:
        previous_device = table_devices.get_item(Key={'id': previous_device_id}).get('Item') or {}
        if previous_device and _normalize_text(previous_device.get('residentId')) == resident_id:
            previous_device['residentId'] = ''
            table_devices.put_item(Item=previous_device)

    if next_device_id:
        next_device = table_devices.get_item(Key={'id': next_device_id}).get('Item') or {}
        if next_device:
            next_device['residentId'] = resident_id
            table_devices.put_item(Item=next_device)


def _build_resident_item(existing=None, payload=None, resident_id='', owner_id=''):
    existing = existing or {}
    payload = payload or {}

    name = _normalize_text(payload.get('name') or existing.get('name'))
    if not name:
        return None

    return {
        **existing,
        'id': _normalize_text(resident_id or payload.get('id') or existing.get('id')),
        'name': name,
        'deviceId': _normalize_device_id(payload.get('deviceId') or existing.get('deviceId')),
        'status': _normalize_text(payload.get('status') or existing.get('status')),
        'notes': _normalize_text(payload.get('notes') or existing.get('notes')),
        'ownerId': _normalize_text(
            existing.get('ownerId')
            or payload.get('ownerId')
            or owner_id
        )
    }


@residents_bp.route('/residents', methods=['GET', 'POST'])
def handle_residents():
    if request.method == 'POST':
        user_context, auth_error = require_user_context('user:create-records')
        if auth_error:
            return auth_error

        payload = dict(request.json or {})
        resident = upsert_item(table_residents, payload)
        resident = _build_resident_item(
            existing=resident,
            payload=payload,
            resident_id=resident.get('id'),
            owner_id=(
                user_context.get('email')
                or user_context.get('tenantKey')
                or user_context.get('sub')
            )
        )
        if not resident:
            return jsonify({"error": "Resident name is required"}), 400

        table_residents.put_item(Item=resident)
        _sync_resident_device_assignment('', resident.get('deviceId'), resident.get('id'))
        return jsonify(resident), 201

    user_context, auth_error = require_user_context('user:create-records')
    if auth_error:
        return auth_error

    return jsonify(scan_all(table_residents)), 200


@residents_bp.route('/residents/<resident_id>', methods=['PUT'])
def update_resident(resident_id):
    user_context, auth_error = require_user_context('user:create-records')
    if auth_error:
        return auth_error

    current_id = _normalize_text(resident_id)
    if not current_id:
        return jsonify({"error": "Resident id is required"}), 400

    existing = table_residents.get_item(Key={'id': current_id}).get('Item') or {}
    if not existing:
        return jsonify({"error": "Resident not found"}), 404

    payload = dict(request.json or {})
    previous_device_id = _normalize_text(existing.get('deviceId'))
    resident = _build_resident_item(
        existing=existing,
        payload=payload,
        resident_id=current_id,
        owner_id=(
            user_context.get('email')
            or user_context.get('tenantKey')
            or user_context.get('sub')
        )
    )
    if not resident:
        return jsonify({"error": "Resident name is required"}), 400

    table_residents.put_item(Item=resident)
    _sync_resident_device_assignment(previous_device_id, resident.get('deviceId'), current_id)
    return jsonify(resident), 200
