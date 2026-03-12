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

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError

app = Flask(__name__)
app.json_provider_class.default = staticmethod(decimal_default)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# DynamoDB
db_url = os.environ.get("DYNAMODB_URL", "http://dynamodb-local:8000")
dynamodb = boto3.resource('dynamodb', endpoint_url=db_url, region_name='us-east-1', aws_access_key_id='local', aws_secret_access_key='local')
table = dynamodb.Table('MonitoringRules')

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        # Emitimos el JSON completo (incluyendo la MAC)
        socketio.emit('sensor_update', data)
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

@app.route('/rules', methods=['GET'])
def get_rules():
    return jsonify(table.scan().get('Items', []))

if __name__ == '__main__':
    start_mqtt()
    # Crear tabla si no existe
    try:
        dynamodb.create_table(
            TableName='MonitoringRules',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
    except: pass
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)