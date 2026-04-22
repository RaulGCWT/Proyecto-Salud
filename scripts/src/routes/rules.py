import uuid

from flask import Blueprint, jsonify, request

from src.database import table_rules

rules_bp = Blueprint('rules', __name__)

ALLOWED_ASSIGNMENT_ROLES = {'admin', 'technician', 'members'}


def normalize_assignment_type(value):
    raw = str(value or '').strip().lower()
    if raw in {'device', 'user'}:
        return raw
    return 'none'


def is_assignment_allowed() -> bool:
    role = str(request.headers.get('X-Role') or request.headers.get('x-role') or '').strip().lower()
    return role in ALLOWED_ASSIGNMENT_ROLES


def get_owner_id():
    payload = request.get_json(silent=True) or {}
    return (
        request.headers.get('X-Owner-Id')
        or request.headers.get('x-owner-id')
        or request.args.get('ownerId')
        or payload.get('ownerId')
        or ''
    )


@rules_bp.route('/rules', methods=['GET', 'POST'])
def handle_rules():
    if request.method == 'POST':
        rule = dict(request.get_json(silent=True) or {})
        owner_id = str(get_owner_id() or '').strip()
        assigned_to_type = normalize_assignment_type(rule.get('assignedToType'))
        assigned_to_id = str(rule.get('assignedToId') or '').strip()

        if not owner_id:
            return jsonify({"error": "ownerId is required"}), 400
        if assigned_to_type != 'none' and not is_assignment_allowed():
            return jsonify({"error": "You are not allowed to assign rules"}), 403
        if assigned_to_type != 'none' and not assigned_to_id:
            return jsonify({"error": "assignedToId is required when assignedToType is set"}), 400

        rule['id'] = str(uuid.uuid4())
        rule['ownerId'] = owner_id
        rule['assignedToType'] = assigned_to_type
        rule['assignedToId'] = assigned_to_id
        table_rules.put_item(Item=rule)
        return jsonify(rule), 201

    response = table_rules.scan()
    items = response.get('Items', [])
    owner_id = str(get_owner_id() or '').strip()
    if owner_id:
        items = [item for item in items if str(item.get('ownerId') or '') == owner_id]
    for item in items:
        item['assignedToType'] = normalize_assignment_type(item.get('assignedToType'))
        item['assignedToId'] = str(item.get('assignedToId') or '')
    return jsonify(items), 200


@rules_bp.route('/rules/<rule_id>', methods=['PUT', 'DELETE'])
def handle_rule_operations(rule_id):
    if request.method == 'PUT':
        new_data = dict(request.get_json(silent=True) or {})
        owner_id = str(get_owner_id() or '').strip()
        assigned_to_type = normalize_assignment_type(new_data.get('assignedToType'))
        assigned_to_id = str(new_data.get('assignedToId') or '').strip()

        if assigned_to_type != 'none' and not is_assignment_allowed():
            return jsonify({"error": "You are not allowed to assign rules"}), 403
        if assigned_to_type != 'none' and not assigned_to_id:
            return jsonify({"error": "assignedToId is required when assignedToType is set"}), 400

        current_rule = table_rules.get_item(Key={'id': rule_id}).get('Item')
        if not current_rule:
            return jsonify({"error": "Rule not found"}), 404
        if owner_id and str(current_rule.get('ownerId') or '') != owner_id:
            return jsonify({"error": "Rule does not belong to this user"}), 403

        updated_rule = {
            **current_rule,
            **new_data,
            'id': rule_id,
            'ownerId': owner_id or current_rule.get('ownerId', ''),
            'assignedToType': assigned_to_type,
            'assignedToId': assigned_to_id,
        }
        table_rules.put_item(Item=updated_rule)
        return jsonify(updated_rule), 200

    if request.method == 'DELETE':
        owner_id = str(get_owner_id() or '').strip()
        current_rule = table_rules.get_item(Key={'id': rule_id}).get('Item')
        if not current_rule:
            return jsonify({"error": "Rule not found"}), 404
        if owner_id and str(current_rule.get('ownerId') or '') != owner_id:
            return jsonify({"error": "Rule does not belong to this user"}), 403
        table_rules.delete_item(Key={'id': rule_id})
        return jsonify({"status": "deleted"}), 200
