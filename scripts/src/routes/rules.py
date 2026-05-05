import uuid

from flask import Blueprint, jsonify, request

from src.auth import (
    can_assign_rules,
    get_record_owner_id,
    get_scoped_owner_id,
    require_user_context,
)
from src.database import table_rules

rules_bp = Blueprint('rules', __name__)


def normalize_assignment_type(value):
    raw = str(value or '').strip().lower()
    if raw in {'device', 'user'}:
        return raw
    return 'none'


@rules_bp.route('/rules', methods=['GET', 'POST'])
def handle_rules():
    if request.method == 'POST':
        user_context, auth_error = require_user_context('rules:manage')
        if auth_error:
            return auth_error

        rule = dict(request.get_json(silent=True) or {})
        assigned_to_type = normalize_assignment_type(rule.get('assignedToType'))
        assigned_to_id = str(rule.get('assignedToId') or '').strip()
        owner_id = get_record_owner_id(user_context)

        if not owner_id:
            return jsonify({"error": "User context is required"}), 401
        if assigned_to_type != 'none' and not can_assign_rules(user_context):
            return jsonify({"error": "You are not allowed to assign rules"}), 403
        if assigned_to_type != 'none' and not assigned_to_id:
            return jsonify({"error": "assignedToId is required when assignedToType is set"}), 400

        rule['id'] = str(uuid.uuid4())
        rule['ownerId'] = owner_id
        rule['assignedToType'] = assigned_to_type
        rule['assignedToId'] = assigned_to_id
        rule['assignedToSide'] = str(rule.get('assignedToSide') or 'all').strip().lower() or 'all'
        table_rules.put_item(Item=rule)
        return jsonify(rule), 201

    user_context, auth_error = require_user_context('rules:view')
    if auth_error:
        return auth_error

    response = table_rules.scan()
    items = response.get('Items', [])
    scoped_owner_id = get_scoped_owner_id(user_context)

    if scoped_owner_id:
        items = [item for item in items if str(item.get('ownerId') or '') == scoped_owner_id]

    for item in items:
        item['assignedToType'] = normalize_assignment_type(item.get('assignedToType'))
        item['assignedToId'] = str(item.get('assignedToId') or '')
        item['assignedToSide'] = str(item.get('assignedToSide') or 'all').strip().lower() or 'all'

    return jsonify(items), 200


@rules_bp.route('/rules/<rule_id>', methods=['PUT', 'DELETE'])
def handle_rule_operations(rule_id):
    user_context, auth_error = require_user_context('rules:manage')
    if auth_error:
        return auth_error

    scoped_owner_id = get_scoped_owner_id(user_context)
    current_rule = table_rules.get_item(Key={'id': rule_id}).get('Item')
    if not current_rule:
        return jsonify({"error": "Rule not found"}), 404
    if scoped_owner_id and str(current_rule.get('ownerId') or '') != scoped_owner_id:
        return jsonify({"error": "Rule does not belong to this user"}), 403

    if request.method == 'PUT':
        new_data = dict(request.get_json(silent=True) or {})
        assigned_to_type = normalize_assignment_type(new_data.get('assignedToType'))
        assigned_to_id = str(new_data.get('assignedToId') or '').strip()

        if assigned_to_type != 'none' and not can_assign_rules(user_context):
            return jsonify({"error": "You are not allowed to assign rules"}), 403
        if assigned_to_type != 'none' and not assigned_to_id:
            return jsonify({"error": "assignedToId is required when assignedToType is set"}), 400

        updated_rule = {
            **current_rule,
            **new_data,
            'id': rule_id,
            'ownerId': current_rule.get('ownerId', get_record_owner_id(user_context)),
            'assignedToType': assigned_to_type,
            'assignedToId': assigned_to_id,
            'assignedToSide': str(new_data.get('assignedToSide') or current_rule.get('assignedToSide') or 'all').strip().lower() or 'all',
        }
        table_rules.put_item(Item=updated_rule)
        return jsonify(updated_rule), 200

    table_rules.delete_item(Key={'id': rule_id})
    return jsonify({"status": "deleted"}), 200
