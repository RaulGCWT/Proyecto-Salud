import base64
import json
from decimal import Decimal

from src.auth import (
    AuthError,
    build_user_context,
    decode_verified_token,
    get_record_owner_id,
    has_permission,
    is_staff_role,
)


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


def get_bearer_token(event):
    headers = event.get("headers") or {}
    auth_header = str(headers.get("Authorization") or headers.get("authorization") or "").strip()
    if not auth_header.lower().startswith("bearer "):
        raise AuthError("Authorization header is required")

    token = auth_header.split(" ", 1)[1].strip()
    if not token:
        raise AuthError("Bearer token is required")
    return token


def require_user_context(event, required_permission=None):
    try:
        token = get_bearer_token(event)
        claims = decode_verified_token(token)
        user_context = build_user_context(claims)

        if required_permission and not has_permission(user_context, required_permission):
            return None, response(403, {"error": "Insufficient permissions"})

        return user_context, None
    except AuthError as error:
        return None, response(401, {"error": str(error)})


def is_device_visible_for_user(device=None, user_context=None):
    device = device or {}
    user_context = user_context or {}

    if is_staff_role(user_context):
        return True

    record_owner_id = get_record_owner_id(user_context)
    if record_owner_id and str(device.get("ownerId") or "") == record_owner_id:
        return True

    user_tenant_key = str(user_context.get("tenantKey") or "").strip()
    if user_tenant_key and str(device.get("tenantKey") or "") == user_tenant_key:
        return True

    user_residence_id = str(user_context.get("residenceId") or "").strip()
    if user_residence_id and str(device.get("residenceId") or "") == user_residence_id:
        return True

    user_area = str(user_context.get("area") or "").strip().lower()
    if user_area and str(device.get("area") or "").strip().lower() == user_area:
        return True

    user_resident_id = str(user_context.get("residentId") or "").strip()
    if user_resident_id and str(device.get("residentId") or "") == user_resident_id:
        return True

    allowed_device_ids = {
        str(device_id).strip().lower()
        for device_id in (user_context.get("deviceIds") or [])
        if str(device_id).strip()
    }
    if allowed_device_ids:
        candidate_values = {
            str(device.get("deviceId") or "").strip().lower(),
            str(device.get("id") or "").strip().lower(),
            str(device.get("mac") or "").strip().lower(),
        }
        if candidate_values & allowed_device_ids:
            return True

    return False


def normalize_alert_status(value):
    raw = str(value or "").strip().upper()
    mapping = {
        "PENDIENTE": "PENDING",
        "LEIDA": "READ",
        "PENDING": "PENDING",
        "READ": "READ",
    }
    return mapping.get(raw, "PENDING")
