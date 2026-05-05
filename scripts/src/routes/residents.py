from flask import Blueprint, jsonify, request

from src.auth import require_user_context
from src.database import table_residents
from src.services.common import upsert_item

residents_bp = Blueprint('residents', __name__)


@residents_bp.route('/residents', methods=['GET', 'POST'])
def handle_residents():
    if request.method == 'POST':
        user_context, auth_error = require_user_context('user:create-records')
        if auth_error:
            return auth_error

        resident = upsert_item(table_residents, request.json)
        if not resident.get('ownerId'):
            resident['ownerId'] = str(user_context.get('email') or user_context.get('tenantKey') or user_context.get('sub') or '').strip()
            table_residents.put_item(Item=resident)
        return jsonify(resident), 201

    user_context, auth_error = require_user_context('user:create-records')
    if auth_error:
        return auth_error

    response = table_residents.scan()
    return jsonify(response.get('Items', [])), 200
