import time
import uuid
from decimal import Decimal

from src.database import table_devices, table_events, table_rules


last_triggered = {}


def normalize_scope_value(value):
    return str(value or "").strip().lower()


def normalize_assignment_type(value):
    raw = normalize_scope_value(value)
    if raw in {"device", "user"}:
        return raw
    return "none"


def load_device_context(data):
    mac = normalize_scope_value(data.get("mac"))
    device_id = normalize_scope_value(data.get("deviceId") or mac)
    side = normalize_scope_value(data.get("side") or "center")
    device_item = {}

    try:
        if mac:
            device_item = table_devices.get_item(Key={"id": mac}).get("Item") or {}
        if not device_item and device_id and device_id != mac:
            device_item = table_devices.get_item(Key={"id": device_id}).get("Item") or {}
    except Exception as error:
        print(f"[ERROR] rules_engine could not load device metadata for {mac}: {error}")

    return {
        "mac": mac,
        "deviceId": device_id,
        "side": side,
        "ownerId": normalize_scope_value(device_item.get("ownerId")),
        "tenantKey": normalize_scope_value(device_item.get("tenantKey")),
        "residenceId": normalize_scope_value(device_item.get("residenceId")),
        "area": normalize_scope_value(device_item.get("area")),
        "residentId": normalize_scope_value(device_item.get("residentId")),
    }


def rule_matches_device_scope(rule, device_context):
    assignment_type = normalize_assignment_type(rule.get("assignedToType"))
    assigned_to_id = normalize_scope_value(rule.get("assignedToId"))

    # Las reglas sin asignación no deben disparar alertas sobre ningún dispositivo.
    if assignment_type == "none":
        return False

    if not assigned_to_id:
        return False

    if assignment_type == "device":
        return assigned_to_id in {
            device_context.get("mac", ""),
            device_context.get("deviceId", ""),
        }

    if assignment_type == "user":
        return assigned_to_id in {
            device_context.get("ownerId", ""),
            device_context.get("tenantKey", ""),
            device_context.get("residenceId", ""),
            device_context.get("area", ""),
            device_context.get("residentId", ""),
        }

    return False


def check_rules_and_save(data):
    try:
        rules = table_rules.scan().get("Items", [])
        print(f"[DEBUG] Rules loaded: {len(rules)}")
        now = time.time()
        device_context = load_device_context(data)

        for rule in rules:
            param = rule.get("parameter") or rule.get("variable")
            condition = rule.get("condition") or rule.get("operator")
            rule_id = rule.get("id")
            mac = device_context.get("mac", "unknown")

            if not rule_matches_device_scope(rule, device_context):
                continue

            if not param or not condition:
                continue

            mapping = {
                "hr": "heartRate",
                "heartRate": "heartRate",
                "resp": "respiratoryRate",
                "respiratoryRate": "respiratoryRate",
                "hrv": "hrv",
            }

            sensor_key = mapping.get(param)
            if not sensor_key or sensor_key not in data:
                continue

            current_value = float(data[sensor_key])
            threshold = float(rule.get("value", 0))

            triggered = False
            if condition == ">" and current_value > threshold:
                triggered = True
            elif condition == "<" and current_value < threshold:
                triggered = True
            elif condition == "==" and current_value == threshold:
                triggered = True

            print(
                "[DEBUG] Rule check -> "
                f"param={param} condition={condition} threshold={threshold} "
                f"value={current_value} triggered={triggered}"
            )

            if triggered:
                key = (mac, device_context.get("side", "center"), rule_id)
                event_data = {
                    "id": str(uuid.uuid4()),
                    "ownerId": rule.get("ownerId", ""),
                    "mac": mac,
                    "deviceId": device_context.get("deviceId", mac),
                    "side": device_context.get("side", "center"),
                    "parameter": param,
                    "value": Decimal(str(current_value)),
                    "rule_id": rule_id,
                    "assignedToType": normalize_assignment_type(rule.get("assignedToType")),
                    "assignedToId": normalize_scope_value(rule.get("assignedToId")),
                    "timestamp": str(now),
                    "message": f"Alert: {param} at {current_value}",
                    "status": "PENDING",
                }
                table_events.put_item(Item=event_data)
                print(f"[DEBUG] Saved alert id={event_data['id']} status={event_data['status']}")
                last_triggered[key] = now
                print(f"[INFO] Alert saved: {param} for {mac}")

    except Exception as e:
        print(f"[ERROR] rules_engine failed: {e}")
