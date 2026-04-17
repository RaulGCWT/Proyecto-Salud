from flask import Blueprint, jsonify, request

from database import table_residents
from services.common import upsert_item

residents_bp = Blueprint('residents', __name__)


@residents_bp.route('/residents', methods=['GET', 'POST'])
def handle_residents():
    if request.method == 'POST':
        resident = upsert_item(table_residents, request.json)
        return jsonify(resident), 201

    response = table_residents.scan()
    return jsonify(response.get('Items', [])), 200
