import uuid
from decimal import Decimal

from src.database import table_rules
from src.lambda_handlers.common import get_owner_id, get_role, parse_body, response


ALLOWED_ASSIGNMENT_ROLES = {'admin', 'technician', 'members'}


def normalize_assignment_type(value):
    raw = str(value or '').strip().lower()
    if raw in {'device', 'user'}:
        return raw
    return 'none'


def can_assign_rules(role):
    return str(role or '').strip().lower() in ALLOWED_ASSIGNMENT_ROLES


def get_rules(event, context):
    items = table_rules.scan().get("Items", [])
    owner_id = get_owner_id(event)
    if owner_id:
        items = [item for item in items if str(item.get("ownerId") or "") == str(owner_id)]
    for item in items:
        item["assignedToType"] = normalize_assignment_type(item.get("assignedToType"))
        item["assignedToId"] = str(item.get("assignedToId") or "")
    return response(200, items)


def create_rule(event, context):
    body = parse_body(event)
    owner_id = get_owner_id(event, body)
    role = get_role(event, body)
    value = body.get("value", 0)
    assigned_to_type = normalize_assignment_type(body.get("assignedToType"))
    assigned_to_id = str(body.get("assignedToId") or "").strip()

    if assigned_to_type != 'none' and not can_assign_rules(role):
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
    }

    if not rule["name"]:
        return response(400, {"error": "Rule name is required"})
    if not rule["ownerId"]:
        return response(400, {"error": "ownerId is required"})

    table_rules.put_item(Item=rule)
    return response(201, rule)


def update_rule(event, context):
    rule_id = (event.get("pathParameters") or {}).get("rule_id")
    if not rule_id:
        return response(400, {"error": "rule_id is required"})

    body = parse_body(event)
    owner_id = get_owner_id(event, body)
    role = get_role(event, body)
    value = body.get("value", 0)
    name = body.get("name", "").strip()
    assigned_to_type = normalize_assignment_type(body.get("assignedToType"))
    assigned_to_id = str(body.get("assignedToId") or "").strip()
    if not name:
        return response(400, {"error": "Rule name is required"})
    if assigned_to_type != 'none' and not can_assign_rules(role):
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
        UpdateExpression="SET #n = :n, #v = :v, #o = :o, #val = :val, #owner = :owner, #assignedType = :assignedType, #assignedId = :assignedId",
        ExpressionAttributeNames={
            "#n": "name",
            "#v": "variable",
            "#o": "operator",
            "#val": "value",
            "#owner": "ownerId",
            "#assignedType": "assignedToType",
            "#assignedId": "assignedToId",
        },
        ExpressionAttributeValues={
            ":n": name,
            ":v": body.get("variable", "hr"),
            ":o": body.get("operator", ">"),
            ":val": Decimal(str(value)),
            ":owner": owner_id or current_item.get("ownerId", ""),
            ":assignedType": assigned_to_type,
            ":assignedId": assigned_to_id,
        },
        ReturnValues="ALL_NEW",
    )

    return response(200, response_data.get("Attributes", {"id": rule_id}))


def delete_rule(event, context):
    rule_id = (event.get("pathParameters") or {}).get("rule_id")
    if not rule_id:
        return response(400, {"error": "rule_id is required"})

    owner_id = get_owner_id(event)
    current_item = table_rules.get_item(Key={"id": rule_id}).get("Item")
    if not current_item:
        return response(404, {"error": "Rule not found"})
    if owner_id and str(current_item.get("ownerId") or "") != str(owner_id):
        return response(403, {"error": "Rule does not belong to this user"})

    table_rules.delete_item(Key={"id": rule_id})
    return response(200, {"status": "deleted", "id": rule_id})
