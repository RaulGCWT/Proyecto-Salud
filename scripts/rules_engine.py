import uuid
import time
from decimal import Decimal
from database import table_rules, table_events

def check_rules_and_save(data):
    try:
        rules = table_rules.scan().get('Items', [])
        for rule in rules:
            param = rule.get('parameter')
            condition = rule.get('condition')
            threshold = float(rule.get('value'))
            current_value = float(data.get(param, 0))

            triggered = False
            if condition == ">" and current_value > threshold: triggered = True
            elif condition == "<" and current_value < threshold: triggered = True
            elif condition == "==" and current_value == threshold: triggered = True

            if triggered:
                event_data = {
                    'id': str(uuid.uuid4()),
                    'mac': data['mac'],
                    'parameter': param,
                    'value': Decimal(str(current_value)),
                    'rule_id': rule['id'],
                    'timestamp': str(time.time())
                }
                table_events.put_item(Item=event_data)
                print(f"⚠️ REGLA ACTIVADA: {param} {condition} {threshold} para {data['mac']}")
    except Exception as e:
        print(f"❌ Error en rules_engine: {e}")