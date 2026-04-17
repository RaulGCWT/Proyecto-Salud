import uuid

from flask import Blueprint, jsonify, request

from database import table_rules

rules_bp = Blueprint('rules', __name__)


@rules_bp.route('/rules', methods=['GET', 'POST'])
def handle_rules():
    if request.method == 'POST':
        rule = dict(request.json or {})
        rule['id'] = str(uuid.uuid4())
        table_rules.put_item(Item=rule)
        return jsonify(rule), 201

    response = table_rules.scan()
    return jsonify(response.get('Items', [])), 200


@rules_bp.route('/rules/<rule_id>', methods=['PUT', 'DELETE'])
def handle_rule_operations(rule_id):
    if request.method == 'PUT':
        new_data = dict(request.json or {})
        new_data['id'] = rule_id
        table_rules.put_item(Item=new_data)
        return jsonify(new_data), 200

    if request.method == 'DELETE':
        table_rules.delete_item(Key={'id': rule_id})
        return jsonify({"status": "deleted"}), 200
