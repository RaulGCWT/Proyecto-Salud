from flask import Blueprint, jsonify, request

from src.database import table_family_users

family_users_bp = Blueprint('family_users', __name__)


@family_users_bp.route('/family-users', methods=['GET'])
def get_family_users():
    response = table_family_users.scan()
    return jsonify(response.get('Items', [])), 200


@family_users_bp.route('/family-users/<family_user_id>', methods=['PUT'])
def update_family_user(family_user_id):
    payload = dict(request.json or {})
    response = table_family_users.get_item(Key={'id': family_user_id})
    family_user = response.get('Item')

    if not family_user:
        return jsonify({"error": "Family user not found"}), 404

    updated_user = {
        **family_user,
        **payload,
        'id': family_user_id
    }
    table_family_users.put_item(Item=updated_user)
    return jsonify(updated_user), 200
