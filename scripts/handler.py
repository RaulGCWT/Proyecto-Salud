import base64
import json
import uuid
from decimal import Decimal

from database import table_rules


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


def get_rules(event, context):
    items = table_rules.scan().get("Items", [])
    return _response(200, items)


def create_rule(event, context):
    body = _parse_body(event)
    value = body.get("value", 0)

    rule = {
        "id": str(uuid.uuid4()),
        "name": body.get("name", "").strip(),
        "variable": body.get("variable", "hr"),
        "operator": body.get("operator", ">"),
        "value": Decimal(str(value)),
    }

    if not rule["name"]:
        return _response(400, {"error": "Rule name is required"})

    table_rules.put_item(Item=rule)
    return _response(201, rule)


def update_rule(event, context):
    rule_id = (event.get("pathParameters") or {}).get("rule_id")
    if not rule_id:
        return _response(400, {"error": "rule_id is required"})

    body = _parse_body(event)
    value = body.get("value", 0)
    name = body.get("name", "").strip()
    if not name:
        return _response(400, {"error": "Rule name is required"})

    response = table_rules.update_item(
        Key={"id": rule_id},
        UpdateExpression="SET #n = :n, #v = :v, #o = :o, #val = :val",
        ExpressionAttributeNames={
            "#n": "name",
            "#v": "variable",
            "#o": "operator",
            "#val": "value",
        },
        ExpressionAttributeValues={
            ":n": name,
            ":v": body.get("variable", "hr"),
            ":o": body.get("operator", ">"),
            ":val": Decimal(str(value)),
        },
        ReturnValues="ALL_NEW",
    )

    return _response(200, response.get("Attributes", {"id": rule_id}))


def delete_rule(event, context):
    rule_id = (event.get("pathParameters") or {}).get("rule_id")
    if not rule_id:
        return _response(400, {"error": "rule_id is required"})

    table_rules.delete_item(Key={"id": rule_id})
    return _response(200, {"status": "deleted", "id": rule_id})
