from flask import Blueprint, jsonify, request

from src.database import table_staff_members
from src.services.common import upsert_item

staff_bp = Blueprint('staff', __name__)


@staff_bp.route('/staff-members', methods=['GET', 'POST'])
def handle_staff_members():
    if request.method == 'POST':
        staff_member = upsert_item(table_staff_members, request.json)
        return jsonify(staff_member), 201

    response = table_staff_members.scan()
    return jsonify(response.get('Items', [])), 200
