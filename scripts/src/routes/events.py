from flask import Blueprint, jsonify, request

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
    try:
        response = table_events.scan()
        items = response.get('Items', [])
        for item in items:
            item['status'] = normalize_alert_status(item.get('status'))
        items.sort(key=lambda x: float(x.get('timestamp', 0)), reverse=True)
        return jsonify(items), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@events_bp.route('/events/<event_id>/status', methods=['PUT'])
def update_event_status(event_id):
    try:
        payload = dict(request.json or {})
        new_status = normalize_alert_status(payload.get('status'))

        table_events.update_item(
            Key={'id': event_id},
            UpdateExpression='SET #s = :s',
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={':s': new_status}
        )
        return jsonify({"id": event_id, "status": new_status}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@events_bp.route('/events/clear', methods=['DELETE'])
def clear_all_events():
    try:
        items = table_events.scan().get('Items', [])
        with table_events.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={'id': item['id']})
        return jsonify({"status": "cleared"}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
