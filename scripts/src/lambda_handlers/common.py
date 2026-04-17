import base64
import json
from decimal import Decimal


def json_default(value):
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        },
        "body": json.dumps(body, default=json_default),
    }


def parse_body(event):
    raw_body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        raw_body = base64.b64decode(raw_body)
    if isinstance(raw_body, bytes):
        raw_body = raw_body.decode("utf-8")
    return json.loads(raw_body)


def get_owner_id(event, body=None):
    body = body or {}
    headers = event.get("headers") or {}
    return (
        body.get("ownerId")
        or (event.get("queryStringParameters") or {}).get("ownerId")
        or headers.get("x-owner-id")
        or headers.get("X-Owner-Id")
        or ""
    )


def normalize_alert_status(value):
    raw = str(value or "").strip().upper()
    mapping = {
        "PENDIENTE": "PENDING",
        "LEIDA": "READ",
        "PENDING": "PENDING",
        "READ": "READ",
    }
    return mapping.get(raw, "PENDING")
