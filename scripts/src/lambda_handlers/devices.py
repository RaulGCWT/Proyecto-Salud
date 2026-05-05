from src.auth import get_record_owner_id
from src.database import table_devices
from src.lambda_handlers.common import is_device_visible_for_user, parse_body, require_user_context, response


def _normalize_device_item(existing=None, body=None, device_id=""):
    existing = existing or {}
    body = body or {}
    normalized_id = str(device_id or body.get("id") or body.get("mac") or existing.get("id") or existing.get("mac") or "").strip().lower()
    normalized_name = str(body.get("name") or existing.get("name") or body.get("deviceId") or existing.get("deviceId") or f"Bed-{normalized_id[-5:]}").strip()
    normalized_type = str(body.get("type") or existing.get("type") or "Standard").strip() or "Standard"

    return {
        "id": normalized_id,
        "mac": str(body.get("mac") or existing.get("mac") or normalized_id).strip().lower(),
        "deviceId": str(body.get("deviceId") or existing.get("deviceId") or normalized_name or normalized_id).strip(),
        "name": normalized_name,
        "type": normalized_type,
        "ownerId": str(body.get("ownerId") or existing.get("ownerId") or "").strip(),
        "tenantKey": str(body.get("tenantKey") or existing.get("tenantKey") or "").strip(),
        "residenceId": str(body.get("residenceId") or existing.get("residenceId") or "").strip(),
        "area": str(body.get("area") or existing.get("area") or "").strip(),
        "residentId": str(body.get("residentId") or existing.get("residentId") or "").strip(),
    }


def get_devices(event, context):
    user_context, auth_error = require_user_context(event, "devices:view")
    if auth_error:
        return auth_error

    items = table_devices.scan().get("Items", [])
    filtered_items = [item for item in items if is_device_visible_for_user(item, user_context)]
    return response(200, filtered_items)


def save_device(event, context):
    user_context, auth_error = require_user_context(event, "devices:edit")
    if auth_error:
        return auth_error

    body = parse_body(event)
    device_id = str((body.get("mac") or body.get("id") or "").strip().lower())
    if not device_id:
        return response(400, {"error": "Device id is required"})

    existing = table_devices.get_item(Key={"id": device_id}).get("Item") or {}
    device = _normalize_device_item(existing, body, device_id)
    device["ownerId"] = get_record_owner_id(user_context) or device["ownerId"]
    device["tenantKey"] = str(user_context.get("tenantKey") or device["tenantKey"] or "").strip()
    device["residenceId"] = str(user_context.get("residenceId") or device["residenceId"] or "").strip()
    device["area"] = str(user_context.get("area") or device["area"] or "").strip()
    device["residentId"] = str(user_context.get("residentId") or device["residentId"] or "").strip()

    table_devices.put_item(Item=device)
    return response(201, device)


def update_device(event, context):
    user_context, auth_error = require_user_context(event, "devices:edit")
    if auth_error:
        return auth_error

    device_id = (event.get("pathParameters") or {}).get("device_id")
    if not device_id:
        return response(400, {"error": "device_id is required"})

    body = parse_body(event)
    current_id = str(device_id).strip().lower()
    name = (body.get("name") or "").strip()
    if not name:
        return response(400, {"error": "Device name is required"})

    existing = table_devices.get_item(Key={"id": current_id}).get("Item") or {}

    item = _normalize_device_item(existing, body, current_id)
    item["name"] = name or item["name"]
    item["ownerId"] = get_record_owner_id(user_context) or item["ownerId"]
    item["tenantKey"] = str(user_context.get("tenantKey") or item["tenantKey"] or "").strip()
    item["residenceId"] = str(user_context.get("residenceId") or item["residenceId"] or "").strip()
    item["area"] = str(user_context.get("area") or item["area"] or "").strip()
    item["residentId"] = str(user_context.get("residentId") or item["residentId"] or "").strip()

    table_devices.put_item(Item=item)
    return response(200, item)
