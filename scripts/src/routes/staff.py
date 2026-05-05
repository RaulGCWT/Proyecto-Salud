from flask import Blueprint, jsonify, request

from src.auth import require_user_context
from src.database import table_staff_members
from src.services.common import upsert_item

staff_bp = Blueprint('staff', __name__)


@staff_bp.route('/staff-members', methods=['GET', 'POST'])
def handle_staff_members():
    if request.method == 'POST':
        user_context, auth_error = require_user_context('user:create-records')
        if auth_error:
            return auth_error

        staff_member = upsert_item(table_staff_members, request.json)
        if not staff_member.get('ownerId'):
            staff_member['ownerId'] = str(user_context.get('email') or user_context.get('tenantKey') or user_context.get('sub') or '').strip()
            table_staff_members.put_item(Item=staff_member)
        return jsonify(staff_member), 201

    user_context, auth_error = require_user_context('user:create-records')
    if auth_error:
        return auth_error

    response = table_staff_members.scan()
    return jsonify(response.get('Items', [])), 200
