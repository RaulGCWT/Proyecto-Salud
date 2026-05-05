from flask import Blueprint, jsonify, request

from src.auth import get_scoped_owner_id, require_user_context
from src.database import table_events

events_bp = Blueprint('events', __name__)


def normalize_alert_status(value):
    raw = str(value or '').strip().upper()
    mapping = {
        'PENDIENTE': 'PENDING',
        'LEIDA': 'READ',
        'PENDING': 'PENDING',
        'READ': 'READ'
    }
    return mapping.get(raw, 'PENDING')


@events_bp.route('/events', methods=['GET'])
def get_events():
    user_context, auth_error = require_user_context('alerts:view')
    if auth_error:
        return auth_error

    try:
        response = table_events.scan()
        items = response.get('Items', [])
        scoped_owner_id = get_scoped_owner_id(user_context)

        if scoped_owner_id:
            items = [item for item in items if str(item.get('ownerId') or '') == scoped_owner_id]

        for item in items:
            item['status'] = normalize_alert_status(item.get('status'))
        items.sort(key=lambda x: float(x.get('timestamp', 0)), reverse=True)
        return jsonify(items), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@events_bp.route('/events/<event_id>/status', methods=['PUT'])
def update_event_status(event_id):
    user_context, auth_error = require_user_context('alerts:view')
    if auth_error:
        return auth_error

    try:
        payload = dict(request.json or {})
        new_status = normalize_alert_status(payload.get('status'))
        scoped_owner_id = get_scoped_owner_id(user_context)

        current_item = table_events.get_item(Key={'id': event_id}).get('Item')
        if not current_item:
            return jsonify({"error": "Event not found"}), 404
        if scoped_owner_id and str(current_item.get('ownerId') or '') != scoped_owner_id:
            return jsonify({"error": "Event does not belong to this user"}), 403

        table_events.update_item(
            Key={'id': event_id},
            UpdateExpression='SET #s = :s',
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={':s': new_status}
        )
        return jsonify({"id": event_id, "status": new_status}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@events_bp.route('/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    user_context, auth_error = require_user_context('alerts:clear')
    if auth_error:
        return auth_error

    try:
        scoped_owner_id = get_scoped_owner_id(user_context)
        current_item = table_events.get_item(Key={'id': event_id}).get('Item')
        if not current_item:
            return jsonify({"error": "Event not found"}), 404
        if scoped_owner_id and str(current_item.get('ownerId') or '') != str(scoped_owner_id):
            return jsonify({"error": "Event does not belong to this user"}), 403

        table_events.delete_item(Key={'id': event_id})
        return jsonify({"id": event_id, "status": "deleted"}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@events_bp.route('/events/clear', methods=['DELETE'])
def clear_all_events():
    user_context, auth_error = require_user_context('alerts:clear')
    if auth_error:
        return auth_error

    try:
        scoped_owner_id = get_scoped_owner_id(user_context)
        items = table_events.scan().get('Items', [])

        if scoped_owner_id:
            items = [item for item in items if str(item.get('ownerId') or '') == scoped_owner_id]

        with table_events.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={'id': item['id']})
        return jsonify({"status": "cleared"}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
