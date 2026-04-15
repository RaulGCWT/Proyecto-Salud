import base64
import json
import uuid
from decimal import Decimal

from database import table_devices, table_events, table_family_users, table_invites, table_residents, table_rules, table_staff_members
from services.invites import (
    INVITE_ACCEPTED,
    INVITE_CANCELLED,
    INVITE_EXPIRED,
    INVITE_PENDING,
    build_accept_url,
    change_invitation_state,
    create_invitation,
    get_invitation_by_id,
    get_invitation_by_token,
    list_invitations,
    register_family_user_from_invitation,
)


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        },
        "body": json.dumps(body, default=_json_default),
    }


def _json_default(value):
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


def _parse_body(event):
    raw_body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        raw_body = base64.b64decode(raw_body)
    if isinstance(raw_body, bytes):
        raw_body = raw_body.decode("utf-8")
    return json.loads(raw_body)


def _get_owner_id(event, body=None):
    body = body or {}
    headers = event.get("headers") or {}
    return (
        body.get("ownerId")
        or (event.get("queryStringParameters") or {}).get("ownerId")
        or headers.get("x-owner-id")
        or headers.get("X-Owner-Id")
        or ""
    )


def get_rules(event, context):
    items = table_rules.scan().get("Items", [])
    owner_id = _get_owner_id(event)
    if owner_id:
        items = [item for item in items if str(item.get("ownerId") or "") == str(owner_id)]
    return _response(200, items)


def create_rule(event, context):
    body = _parse_body(event)
    owner_id = _get_owner_id(event, body)
    value = body.get("value", 0)

    rule = {
        "id": str(uuid.uuid4()),
        "ownerId": owner_id,
        "name": body.get("name", "").strip(),
        "variable": body.get("variable", "hr"),
        "operator": body.get("operator", ">"),
        "value": Decimal(str(value)),
    }

    if not rule["name"]:
        return _response(400, {"error": "Rule name is required"})
    if not rule["ownerId"]:
        return _response(400, {"error": "ownerId is required"})

    table_rules.put_item(Item=rule)
    return _response(201, rule)


def update_rule(event, context):
    rule_id = (event.get("pathParameters") or {}).get("rule_id")
    if not rule_id:
        return _response(400, {"error": "rule_id is required"})

    body = _parse_body(event)
    owner_id = _get_owner_id(event, body)
    value = body.get("value", 0)
    name = body.get("name", "").strip()
    if not name:
        return _response(400, {"error": "Rule name is required"})

    current_item = table_rules.get_item(Key={"id": rule_id}).get("Item")
    if not current_item:
        return _response(404, {"error": "Rule not found"})
    if owner_id and str(current_item.get("ownerId") or "") != str(owner_id):
        return _response(403, {"error": "Rule does not belong to this user"})

    response = table_rules.update_item(
        Key={"id": rule_id},
        UpdateExpression="SET #n = :n, #v = :v, #o = :o, #val = :val, #owner = :owner",
        ExpressionAttributeNames={
            "#n": "name",
            "#v": "variable",
            "#o": "operator",
            "#val": "value",
            "#owner": "ownerId",
        },
        ExpressionAttributeValues={
            ":n": name,
            ":v": body.get("variable", "hr"),
            ":o": body.get("operator", ">"),
            ":val": Decimal(str(value)),
            ":owner": owner_id or current_item.get("ownerId", ""),
        },
        ReturnValues="ALL_NEW",
    )

    return _response(200, response.get("Attributes", {"id": rule_id}))


def delete_rule(event, context):
    rule_id = (event.get("pathParameters") or {}).get("rule_id")
    if not rule_id:
        return _response(400, {"error": "rule_id is required"})

    owner_id = _get_owner_id(event)
    current_item = table_rules.get_item(Key={"id": rule_id}).get("Item")
    if not current_item:
        return _response(404, {"error": "Rule not found"})
    if owner_id and str(current_item.get("ownerId") or "") != str(owner_id):
        return _response(403, {"error": "Rule does not belong to this user"})

    table_rules.delete_item(Key={"id": rule_id})
    return _response(200, {"status": "deleted", "id": rule_id})


def get_devices(event, context):
    items = table_devices.scan().get("Items", [])
    return _response(200, items)


def _normalize_alert_status(value):
    raw = str(value or "").strip().upper()
    mapping = {
        "PENDIENTE": "PENDING",
        "LEIDA": "READ",
        "PENDING": "PENDING",
        "READ": "READ",
    }
    return mapping.get(raw, "PENDING")


def get_events(event, context):
    items = table_events.scan().get("Items", [])
    owner_id = _get_owner_id(event)
    normalized_items = []

    for item in items:
        if owner_id and str(item.get("ownerId") or "") != str(owner_id):
            continue
        normalized_item = dict(item)
        normalized_item["status"] = _normalize_alert_status(normalized_item.get("status"))
        normalized_items.append(normalized_item)

    normalized_items.sort(key=lambda x: float(x.get("timestamp", 0)), reverse=True)
    return _response(200, normalized_items)


def update_event_status(event, context):
    event_id = (event.get("pathParameters") or {}).get("event_id")
    if not event_id:
        return _response(400, {"error": "event_id is required"})

    body = _parse_body(event)
    new_status = _normalize_alert_status(body.get("status"))
    owner_id = _get_owner_id(event, body)

    current_item = table_events.get_item(Key={"id": event_id}).get("Item")
    if not current_item:
        return _response(404, {"error": "Event not found"})
    if owner_id and str(current_item.get("ownerId") or "") != str(owner_id):
        return _response(403, {"error": "Event does not belong to this user"})

    response = table_events.update_item(
        Key={"id": event_id},
        UpdateExpression="SET #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": new_status},
        ReturnValues="ALL_NEW",
    )

    return _response(200, response.get("Attributes", {"id": event_id, "status": new_status}))


def clear_events(event, context):
    items = table_events.scan().get("Items", [])
    owner_id = _get_owner_id(event)
    with table_events.batch_writer() as batch:
        for item in items:
            if owner_id and str(item.get("ownerId") or "") != str(owner_id):
                continue
            batch.delete_item(Key={"id": item["id"]})

    return _response(200, {"status": "cleared"})


def save_device(event, context):
    body = _parse_body(event)
    device_id = str((body.get("mac") or body.get("id") or "").strip().lower())
    if not device_id:
        return _response(400, {"error": "Device id is required"})

    device = {
        "id": device_id,
        "mac": device_id,
        "name": body.get("name") or f"Bed-{device_id[-5:]}",
        "type": body.get("type") or "Standard",
    }

    table_devices.put_item(Item=device)
    return _response(201, device)


def update_device(event, context):
    device_id = (event.get("pathParameters") or {}).get("device_id")
    if not device_id:
        return _response(400, {"error": "device_id is required"})

    body = _parse_body(event)
    current_id = str(device_id).strip().lower()
    name = (body.get("name") or "").strip()
    if not name:
        return _response(400, {"error": "Device name is required"})

    response = table_devices.update_item(
        Key={"id": current_id},
        UpdateExpression="SET #n = :n, #t = :t, #m = :m",
        ExpressionAttributeNames={
            "#n": "name",
            "#t": "type",
            "#m": "mac",
        },
        ExpressionAttributeValues={
            ":n": name,
            ":t": body.get("type") or "Standard",
            ":m": current_id,
        },
        ReturnValues="ALL_NEW",
    )

    return _response(200, response.get("Attributes", {"id": current_id}))


def get_staff_members(event, context):
    items = table_staff_members.scan().get("Items", [])
    return _response(200, items)


def save_staff_member(event, context):
    body = _parse_body(event)
    name = (body.get("name") or "").strip()
    email = (body.get("email") or "").strip()

    if not name or not email:
        return _response(400, {"error": "Staff name and email are required"})

    item = dict(body)
    item["id"] = item.get("id") or str(uuid.uuid4())
    item["name"] = name
    item["email"] = email
    item["role"] = item.get("role") or "Technical Operator"
    item["area"] = item.get("area") or "Devices"

    table_staff_members.put_item(Item=item)
    return _response(201, item)


def get_residents(event, context):
    items = table_residents.scan().get("Items", [])
    return _response(200, items)


def save_resident(event, context):
    body = _parse_body(event)
    name = (body.get("name") or "").strip()
    if not name:
        return _response(400, {"error": "Resident name is required"})

    item = dict(body)
    item["id"] = item.get("id") or str(uuid.uuid4())
    item["name"] = name
    item["deviceId"] = item.get("deviceId") or ""
    item["status"] = item.get("status") or "Pending Setup"
    item["notes"] = item.get("notes") or ""

    table_residents.put_item(Item=item)
    return _response(201, item)


def get_family_users(event, context):
    items = table_family_users.scan().get("Items", [])
    return _response(200, items)


def update_family_user(event, context):
    family_user_id = (event.get("pathParameters") or {}).get("family_user_id")
    if not family_user_id:
        return _response(400, {"error": "family_user_id is required"})

    body = _parse_body(event)
    name = (body.get("name") or "").strip()
    email = (body.get("email") or "").strip()

    if not name or not email:
        return _response(400, {"error": "Family user name and email are required"})

    response = table_family_users.update_item(
        Key={"id": family_user_id},
        UpdateExpression=(
            "SET #n = :n, #e = :e, #r = :r, #s = :s, "
            "#resident = :resident, #patient = :patient, #device = :device, #deviceOverride = :deviceOverride"
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
        },
        ReturnValues="ALL_NEW",
    )

    return _response(200, response.get("Attributes", {"id": family_user_id}))


def get_invites(event, context):
    return _response(200, list_invitations())


def create_invite(event, context):
    body = _parse_body(event)
    if not body.get("email") or not body.get("name"):
        return _response(400, {"error": "Invite name and email are required"})
    return _response(201, create_invitation(body))


def update_invite_state(event, context):
    invite_id = (event.get("pathParameters") or {}).get("invite_id")
    if not invite_id:
        return _response(400, {"error": "invite_id is required"})

    payload = _parse_body(event)
    new_state = str(payload.get("state") or "").upper()
    if new_state not in [INVITE_PENDING, INVITE_CANCELLED]:
        return _response(400, {"error": "Unsupported invitation state"})

    invitation = get_invitation_by_id(invite_id)
    if not invitation:
        return _response(404, {"error": "Invitation not found"})

    current_state = invitation.get("state")
    if current_state == INVITE_ACCEPTED:
        return _response(409, {"error": "Accepted invitations cannot be modified"})
    if current_state == INVITE_EXPIRED and new_state != INVITE_PENDING:
        return _response(409, {"error": "Expired invitations can only be re-opened"})

    return _response(200, change_invitation_state(invitation, new_state))


def verify_invite(event, context):
    token = (event.get("queryStringParameters") or {}).get("token")
    if not token:
        return _response(400, {"error": "Token is required"})

    invitation = get_invitation_by_token(token)
    if not invitation:
        return _response(404, {"error": "Invitation not found"})

    return _response(200, invitation)


def accept_invite(event, context):
    body = _parse_body(event)
    token = body.get("token")
    if not token:
        return _response(400, {"error": "Token is required"})

    invitation = get_invitation_by_token(token)
    if not invitation:
        return _response(404, {"error": "Invitation not found"})
    if invitation.get("state") == INVITE_ACCEPTED:
        return _response(200, invitation)
    if invitation.get("state") != INVITE_PENDING:
        return _response(409, {"error": f"Invitation is {invitation.get('state', 'invalid').lower()}"})

    return _response(200, change_invitation_state(invitation, INVITE_ACCEPTED))


def register_invite(event, context):
    body = _parse_body(event)
    token = body.get("token")
    password = body.get("password")
    name = body.get("name")

    if not token or not password or not name:
        return _response(400, {"error": "Token, name and password are required"})

    invitation = get_invitation_by_token(token)
    if not invitation:
        return _response(404, {"error": "Invitation not found"})
    if invitation.get("state") == INVITE_ACCEPTED:
        return _response(409, {"error": "Invitation already used"})
    if invitation.get("state") != INVITE_PENDING:
        return _response(409, {"error": f"Invitation is {invitation.get('state', 'invalid').lower()}"})

    user = register_family_user_from_invitation(invitation, name, password)
    return _response(201, {
        "status": "registered",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
        },
    })
