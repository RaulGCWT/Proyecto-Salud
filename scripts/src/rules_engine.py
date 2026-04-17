import time
import uuid
from decimal import Decimal

from src.database import table_events, table_rules


last_triggered = {}


def check_rules_and_save(data):
    try:
        rules = table_rules.scan().get("Items", [])
        print(f"[DEBUG] Rules loaded: {len(rules)}")
        now = time.time()

        for rule in rules:
            param = rule.get("parameter") or rule.get("variable")
            condition = rule.get("condition") or rule.get("operator")
            rule_id = rule.get("id")
            mac = data.get("mac", "unknown")

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
                key = (mac, rule_id)
                event_data = {
                    "id": str(uuid.uuid4()),
                    "ownerId": rule.get("ownerId", ""),
                    "mac": mac,
                    "parameter": param,
                    "value": Decimal(str(current_value)),
                    "rule_id": rule_id,
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
