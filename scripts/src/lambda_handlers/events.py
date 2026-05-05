from src.database import table_events
from src.auth import get_scoped_owner_id
from src.lambda_handlers.common import normalize_alert_status, parse_body, require_user_context, response


def get_events(event, context):
    user_context, auth_error = require_user_context(event, "alerts:view")
    if auth_error:
        return auth_error

    items = table_events.scan().get("Items", [])
    owner_id = get_scoped_owner_id(user_context)
    normalized_items = []

    for item in items:
        if owner_id and str(item.get("ownerId") or "") != str(owner_id):
            continue
        normalized_item = dict(item)
        normalized_item["status"] = normalize_alert_status(normalized_item.get("status"))
        normalized_items.append(normalized_item)

    normalized_items.sort(key=lambda x: float(x.get("timestamp", 0)), reverse=True)
    return response(200, normalized_items)


def update_event_status(event, context):
    user_context, auth_error = require_user_context(event, "alerts:view")
    if auth_error:
        return auth_error

    event_id = (event.get("pathParameters") or {}).get("event_id")
    if not event_id:
        return response(400, {"error": "event_id is required"})

    body = parse_body(event)
    new_status = normalize_alert_status(body.get("status"))
    owner_id = get_scoped_owner_id(user_context)

    current_item = table_events.get_item(Key={"id": event_id}).get("Item")
    if not current_item:
        return response(404, {"error": "Event not found"})
    if owner_id and str(current_item.get("ownerId") or "") != str(owner_id):
        return response(403, {"error": "Event does not belong to this user"})

    response_data = table_events.update_item(
        Key={"id": event_id},
        UpdateExpression="SET #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": new_status},
        ReturnValues="ALL_NEW",
    )

    return response(200, response_data.get("Attributes", {"id": event_id, "status": new_status}))


def delete_event(event, context):
    user_context, auth_error = require_user_context(event, "alerts:clear")
    if auth_error:
        return auth_error

    event_id = (event.get("pathParameters") or {}).get("event_id")
    if not event_id:
        return response(400, {"error": "event_id is required"})

    owner_id = get_scoped_owner_id(user_context)
    current_item = table_events.get_item(Key={"id": event_id}).get("Item")
    if not current_item:
        return response(404, {"error": "Event not found"})
    if owner_id and str(current_item.get("ownerId") or "") != str(owner_id):
        return response(403, {"error": "Event does not belong to this user"})

    table_events.delete_item(Key={"id": event_id})
    return response(200, {"id": event_id, "status": "deleted"})


def clear_events(event, context):
    user_context, auth_error = require_user_context(event, "alerts:clear")
    if auth_error:
        return auth_error

    items = table_events.scan().get("Items", [])
    owner_id = get_scoped_owner_id(user_context)
    with table_events.batch_writer() as batch:
        for item in items:
            if owner_id and str(item.get("ownerId") or "") != str(owner_id):
                continue
            batch.delete_item(Key={"id": item["id"]})

    return response(200, {"status": "cleared"})
