import uuid

from src.auth import get_record_owner_id, get_scoped_owner_id
from src.database import table_family_users, table_residents, table_staff_members
from src.lambda_handlers.common import parse_body, require_user_context, response


def get_staff_members(event, context):
    user_context, auth_error = require_user_context(event, "user:create-records")
    if auth_error:
        return auth_error

    items = table_staff_members.scan().get("Items", [])
    scoped_owner_id = get_scoped_owner_id(user_context)
    if scoped_owner_id:
        items = [item for item in items if str(item.get("ownerId") or "") == scoped_owner_id]
    return response(200, items)


def save_staff_member(event, context):
    user_context, auth_error = require_user_context(event, "user:create-records")
    if auth_error:
        return auth_error

    body = parse_body(event)
    name = (body.get("name") or "").strip()
    email = (body.get("email") or "").strip()

    if not name or not email:
        return response(400, {"error": "Staff name and email are required"})

    item = dict(body)
    item["id"] = item.get("id") or str(uuid.uuid4())
    item["name"] = name
    item["email"] = email
    item["role"] = item.get("role") or "Technical Operator"
    item["area"] = item.get("area") or "Devices"
    item["ownerId"] = get_record_owner_id(user_context) or item.get("ownerId") or ""

    table_staff_members.put_item(Item=item)
    return response(201, item)


def get_residents(event, context):
    user_context, auth_error = require_user_context(event, "user:create-records")
    if auth_error:
        return auth_error

    items = table_residents.scan().get("Items", [])
    scoped_owner_id = get_scoped_owner_id(user_context)
    if scoped_owner_id:
        items = [item for item in items if str(item.get("ownerId") or "") == scoped_owner_id]
    return response(200, items)


def save_resident(event, context):
    user_context, auth_error = require_user_context(event, "user:create-records")
    if auth_error:
        return auth_error

    body = parse_body(event)
    name = (body.get("name") or "").strip()
    if not name:
        return response(400, {"error": "Resident name is required"})

    item = dict(body)
    item["id"] = item.get("id") or str(uuid.uuid4())
    item["name"] = name
    item["deviceId"] = item.get("deviceId") or ""
    item["status"] = item.get("status") or "Pending Setup"
    item["notes"] = item.get("notes") or ""
    item["ownerId"] = get_record_owner_id(user_context) or item.get("ownerId") or ""

    table_residents.put_item(Item=item)
    return response(201, item)


def get_family_users(event, context):
    user_context, auth_error = require_user_context(event, "user:create-records")
    if auth_error:
        return auth_error

    items = table_family_users.scan().get("Items", [])
    scoped_owner_id = get_scoped_owner_id(user_context)
    if scoped_owner_id:
        items = [item for item in items if str(item.get("ownerId") or "") == scoped_owner_id]
    return response(200, items)


def update_family_user(event, context):
    user_context, auth_error = require_user_context(event, "user:create-records")
    if auth_error:
        return auth_error

    family_user_id = (event.get("pathParameters") or {}).get("family_user_id")
    if not family_user_id:
        return response(400, {"error": "family_user_id is required"})

    body = parse_body(event)
    name = (body.get("name") or "").strip()
    email = (body.get("email") or "").strip()

    if not name or not email:
        return response(400, {"error": "Family user name and email are required"})

    existing = table_family_users.get_item(Key={"id": family_user_id}).get("Item")
    if not existing:
        return response(404, {"error": "Family user not found"})

    scoped_owner_id = get_scoped_owner_id(user_context)
    if scoped_owner_id and str(existing.get("ownerId") or "") != scoped_owner_id:
        return response(403, {"error": "Family user does not belong to this user"})

    response_data = table_family_users.update_item(
        Key={"id": family_user_id},
        UpdateExpression=(
            "SET #n = :n, #e = :e, #r = :r, #s = :s, "
            "#resident = :resident, #patient = :patient, #device = :device, #deviceOverride = :deviceOverride, #owner = :owner"
        ),
        ExpressionAttributeNames={
            "#n": "name",
            "#e": "email",
            "#r": "relationship",
            "#s": "state",
            "#resident": "residentId",
            "#patient": "patientName",
            "#device": "deviceId",
            "#deviceOverride": "deviceIdOverride",
            "#owner": "ownerId",
        },
        ExpressionAttributeValues={
            ":n": name,
            ":e": email,
            ":r": body.get("relationship") or "Family",
            ":s": body.get("state") or "Active",
            ":resident": body.get("residentId"),
            ":patient": body.get("patientName") or "Unassigned",
            ":device": body.get("deviceId") or "",
            ":deviceOverride": body.get("deviceIdOverride") or "",
            ":owner": get_record_owner_id(user_context) or existing.get("ownerId") or "",
        },
        ReturnValues="ALL_NEW",
    )

    return response(200, response_data.get("Attributes", {"id": family_user_id}))
