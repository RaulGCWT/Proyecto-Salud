from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import json
import paho.mqtt.client as mqtt
import os
import boto3
import uuid
import time
from decimal import Decimal

# Helper para manejar Decimals de DynamoDB
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

app = Flask(__name__)
app.json_provider_class.default = staticmethod(decimal_default)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuración DynamoDB
db_url = os.environ.get("DYNAMODB_URL", "http://dynamodb-local:8000")
dynamodb = boto3.resource('dynamodb', endpoint_url=db_url, region_name='us-east-1', aws_access_key_id='local', aws_secret_access_key='local')

table_rules = dynamodb.Table('MonitoringRules')
table_events = dynamodb.Table('DeviceEvents')

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
                event_id = str(uuid.uuid4())
                event_data = {
                    'id': event_id,
                    'mac': data['mac'],
                    'parameter': param,
                    'value': Decimal(str(current_value)),
                    'rule_id': rule['id'],
                    'timestamp': str(time.time())
                }
                table_events.put_item(Item=event_data)
                print(f"⚠️ REGLA ACTIVADA: {param} {condition} {threshold} para {data['mac']}")
    except Exception as e:
        print(f"Error procesando reglas: {e}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        socketio.emit('sensor_update', data)
        check_rules_and_save(data)
    except Exception as e:
        print(f"Error MQTT: {e}")

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_message = on_message

def start_mqtt():
    try:
        mqtt_client.connect("mqtt-broker", 1883, 60)
        mqtt_client.subscribe("welltech/sensors")
        mqtt_client.loop_start()
    except:
        print("Esperando a MQTT...")

# --- RUTAS API ---

@app.route('/rules', methods=['GET', 'POST'])
def handle_rules():
    if request.method == 'POST':
        rule = request.json
        rule['id'] = str(uuid.uuid4())
        table_rules.put_item(Item=rule)
        return jsonify(rule), 201
    return jsonify(table_rules.scan().get('Items', []))

# NUEVA RUTA: EDITAR REGLA
@app.route('/rules/<rule_id>', methods=['PUT'])
def update_rule(rule_id):
    try:
        new_data = request.json
        new_data['id'] = rule_id # Aseguramos que el ID sea el de la URL
        table_rules.put_item(Item=new_data) # Reemplaza el item con el mismo ID
        return jsonify(new_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    start_mqtt()
    for t_name in ['MonitoringRules', 'DeviceEvents']:
        try:
            dynamodb.create_table(
                TableName=t_name,
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            )
        except: pass
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)