from flask import Blueprint, jsonify, request

from src.auth import require_user_context
from src.database import table_staff_members
from src.services.common import upsert_item

staff_bp = Blueprint('staff', __name__)


def _normalize_text(value):
    return str(value or '').strip()


def _build_staff_item(existing=None, payload=None, staff_id='', owner_id=''):
    existing = existing or {}
    payload = payload or {}

    name = _normalize_text(payload.get('name') or existing.get('name'))
    email = _normalize_text(payload.get('email') or existing.get('email'))
    if not name or not email:
        return None

    return {
        **existing,
        'id': _normalize_text(staff_id or payload.get('id') or existing.get('id')),
        'name': name,
        'email': email,
        'role': _normalize_text(payload.get('role') or existing.get('role')),
        'area': _normalize_text(payload.get('area') or existing.get('area')),
        'ownerId': _normalize_text(
            existing.get('ownerId')
            or payload.get('ownerId')
            or owner_id
        )
    }


@staff_bp.route('/staff-members', methods=['GET', 'POST'])
def handle_staff_members():
    if request.method == 'POST':
        user_context, auth_error = require_user_context('user:create-records')
        if auth_error:
            return auth_error

        payload = dict(request.json or {})
        staff_member = upsert_item(table_staff_members, payload)
        staff_member = _build_staff_item(
            existing=staff_member,
            payload=payload,
            staff_id=staff_member.get('id'),
            owner_id=(
                user_context.get('email')
                or user_context.get('tenantKey')
                or user_context.get('sub')
            )
        )
        if not staff_member:
            return jsonify({"error": "Staff name and email are required"}), 400

        table_staff_members.put_item(Item=staff_member)
        return jsonify(staff_member), 201

    user_context, auth_error = require_user_context('user:create-records')
    if auth_error:
        return auth_error

    response = table_staff_members.scan()
    return jsonify(response.get('Items', [])), 200


@staff_bp.route('/staff-members/<staff_id>', methods=['PUT'])
def update_staff_member(staff_id):
    user_context, auth_error = require_user_context('user:create-records')
    if auth_error:
        return auth_error

    current_id = _normalize_text(staff_id)
    if not current_id:
        return jsonify({"error": "Staff id is required"}), 400

    existing = table_staff_members.get_item(Key={'id': current_id}).get('Item') or {}
    if not existing:
        return jsonify({"error": "Staff member not found"}), 404

    payload = dict(request.json or {})
    staff_member = _build_staff_item(
        existing=existing,
        payload=payload,
        staff_id=current_id,
        owner_id=(
            user_context.get('email')
            or user_context.get('tenantKey')
            or user_context.get('sub')
        )
    )
    if not staff_member:
        return jsonify({"error": "Staff name and email are required"}), 400

    table_staff_members.put_item(Item=staff_member)
    return jsonify(staff_member), 200
