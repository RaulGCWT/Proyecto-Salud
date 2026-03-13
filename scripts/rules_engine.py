import uuid
import time
from decimal import Decimal
from database import table_rules, table_events

# Diccionario para recordar cuándo saltó cada regla por última vez
last_triggered = {}

def check_rules_and_save(data):
    try:
        rules = table_rules.scan().get('Items', [])
        now = time.time()
        
        for rule in rules:
            param = rule.get('parameter') or rule.get('variable')
            condition = rule.get('condition') or rule.get('operator')
            rule_id = rule.get('id')
            mac = data.get('mac', 'unknown')
            
            if not param or not condition: continue

            mapping = {
                'hr': 'heartRate', 'heartRate': 'heartRate',
                'resp': 'respiratoryRate', 'respiratoryRate': 'respiratoryRate',
                'hrv': 'hrv'
            }
            
            sensor_key = mapping.get(param)
            if not sensor_key or sensor_key not in data: continue

            current_value = float(data[sensor_key])
            threshold = float(rule.get('value', 0))

            triggered = False
            if condition == ">" and current_value > threshold: triggered = True
            elif condition == "<" and current_value < threshold: triggered = True
            elif condition == "==" and current_value == threshold: triggered = True

            if triggered:
                key = (mac, rule_id)
                
                event_data = {
                    'id': str(uuid.uuid4()),
                    'mac': mac,
                    'parameter': param,
                    'value': Decimal(str(current_value)),
                    'rule_id': rule_id,
                    'timestamp': str(now),
                    'message': f"Alerta: {param} en {current_value}"
                }
                
                table_events.put_item(Item=event_data)
                last_triggered[key] = now
                print(f"💾 ALERTA ÚNICA GUARDADA: {param} para {mac}")
                
    except Exception as e:
        print(f"❌ Error en rules_engine: {e}")