import uuid
from decimal import Decimal

from src.auth import can_assign_rules, get_record_owner_id, get_scoped_owner_id
from src.database import table_rules
from src.lambda_handlers.common import parse_body, require_user_context, response


def normalize_assignment_type(value):
    raw = str(value or '').strip().lower()
    if raw in {'device', 'user'}:
        return raw
    return 'none'


def normalize_rule_side(value):
    raw = str(value or '').strip().lower()
    if raw in {'left', 'right'}:
        return raw
    return 'all'


def get_rules(event, context):
    user_context, auth_error = require_user_context(event, "rules:view")
    if auth_error:
        return auth_error

    items = table_rules.scan().get("Items", [])
    scoped_owner_id = get_scoped_owner_id(user_context)
    if scoped_owner_id:
        items = [item for item in items if str(item.get("ownerId") or "") == str(scoped_owner_id)]
    for item in items:
        item["assignedToType"] = normalize_assignment_type(item.get("assignedToType"))
        item["assignedToId"] = str(item.get("assignedToId") or "")
        item["assignedToSide"] = normalize_rule_side(item.get("assignedToSide"))
    return response(200, items)


def create_rule(event, context):
    user_context, auth_error = require_user_context(event, "rules:manage")
    if auth_error:
        return auth_error

    body = parse_body(event)
    owner_id = get_record_owner_id(user_context)
    value = body.get("value", 0)
    assigned_to_type = normalize_assignment_type(body.get("assignedToType"))
    assigned_to_id = str(body.get("assignedToId") or "").strip()
    assigned_to_side = normalize_rule_side(body.get("assignedToSide"))

    if assigned_to_type != 'none' and not can_assign_rules(user_context):
        return response(403, {"error": "You are not allowed to assign rules"})
    if assigned_to_type != 'none' and not assigned_to_id:
        return response(400, {"error": "assignedToId is required when assignedToType is set"})

    rule = {
        "id": str(uuid.uuid4()),
        "ownerId": owner_id,
        "name": body.get("name", "").strip(),
        "variable": body.get("variable", "hr"),
        "operator": body.get("operator", ">"),
        "value": Decimal(str(value)),
        "assignedToType": assigned_to_type,
        "assignedToId": assigned_to_id,
        "assignedToSide": assigned_to_side,
    }

    if not rule["name"]:
        return response(400, {"error": "Rule name is required"})
    if not rule["ownerId"]:
        return response(400, {"error": "ownerId is required"})

    table_rules.put_item(Item=rule)
    return response(201, rule)


def update_rule(event, context):
    user_context, auth_error = require_user_context(event, "rules:manage")
    if auth_error:
        return auth_error

    rule_id = (event.get("pathParameters") or {}).get("rule_id")
    if not rule_id:
        return response(400, {"error": "rule_id is required"})

    body = parse_body(event)
    owner_id = get_record_owner_id(user_context)
    value = body.get("value", 0)
    name = body.get("name", "").strip()
    assigned_to_type = normalize_assignment_type(body.get("assignedToType"))
    assigned_to_id = str(body.get("assignedToId") or "").strip()
    assigned_to_side = normalize_rule_side(body.get("assignedToSide"))
    if not name:
        return response(400, {"error": "Rule name is required"})
    if assigned_to_type != 'none' and not can_assign_rules(user_context):
        return response(403, {"error": "You are not allowed to assign rules"})
    if assigned_to_type != 'none' and not assigned_to_id:
        return response(400, {"error": "assignedToId is required when assignedToType is set"})

    current_item = table_rules.get_item(Key={"id": rule_id}).get("Item")
    if not current_item:
        return response(404, {"error": "Rule not found"})
    if owner_id and str(current_item.get("ownerId") or "") != str(owner_id):
        return response(403, {"error": "Rule does not belong to this user"})

    response_data = table_rules.update_item(
        Key={"id": rule_id},
        UpdateExpression="SET #n = :n, #v = :v, #o = :o, #val = :val, #owner = :owner, #assignedType = :assignedType, #assignedId = :assignedId, #assignedSide = :assignedSide",
        ExpressionAttributeNames={
            "#n": "name",
            "#v": "variable",
            "#o": "operator",
            "#val": "value",
            "#owner": "ownerId",
            "#assignedType": "assignedToType",
            "#assignedId": "assignedToId",
            "#assignedSide": "assignedToSide",
        },
        ExpressionAttributeValues={
            ":n": name,
            ":v": body.get("variable", "hr"),
            ":o": body.get("operator", ">"),
            ":val": Decimal(str(value)),
            ":owner": owner_id or current_item.get("ownerId", ""),
            ":assignedType": assigned_to_type,
            ":assignedId": assigned_to_id,
            ":assignedSide": assigned_to_side,
        },
        ReturnValues="ALL_NEW",
    )

    return response(200, response_data.get("Attributes", {"id": rule_id}))


def delete_rule(event, context):
    user_context, auth_error = require_user_context(event, "rules:manage")
    if auth_error:
        return auth_error

    rule_id = (event.get("pathParameters") or {}).get("rule_id")
    if not rule_id:
        return response(400, {"error": "rule_id is required"})

    owner_id = get_scoped_owner_id(user_context)
    current_item = table_rules.get_item(Key={"id": rule_id}).get("Item")
    if not current_item:
        return response(404, {"error": "Rule not found"})
    if owner_id and str(current_item.get("ownerId") or "") != str(owner_id):
        return response(403, {"error": "Rule does not belong to this user"})

    table_rules.delete_item(Key={"id": rule_id})
    return response(200, {"status": "deleted", "id": rule_id})
