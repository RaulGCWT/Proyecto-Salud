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

# --- CONFIGURACIÓN DYNAMODB ---
db_url = os.environ.get("DYNAMODB_URL", "http://dynamodb-local:8000")
dynamodb = boto3.resource('dynamodb', endpoint_url=db_url, region_name='us-east-1', aws_access_key_id='local', aws_secret_access_key='local')
table = dynamodb.Table('MonitoringRules')

# --- LÓGICA DE EVALUACIÓN ---
def evaluar_reglas(datos_sensor):
    try:
        response = table.scan()
        reglas = response.get('Items', [])
        
        for regla in reglas:
            # Mapeo de nombres: Lo que viene del Front vs Lo que viene del MQTT
            var_regla = regla.get('variable') # 'hr', 'hrv', 'resp'
            valor_actual = 0
            
            if var_regla == 'hr':
                valor_actual = datos_sensor.get('heartRate')
            elif var_regla == 'hrv':
                valor_actual = datos_sensor.get('hrv')
            elif var_regla == 'resp':
                valor_actual = datos_sensor.get('respiratoryRate')

            if valor_actual is None:
                continue

            limite = float(regla.get('value', 0))
            op = regla.get('operator')
            
            disparada = False
            if op == '>' and valor_actual > limite:
                disparada = True
            elif op == '<' and valor_actual < limite:
                disparada = True

            if disparada:
                msg = f"⚠️ [ALERTA] {regla['name']}: {valor_actual} {op} {limite}"
                print(msg)
                socketio.emit('new_alert', {
                    "id": str(uuid.uuid4()),
                    "sensor": regla['name'],
                    "message": f"Valor crítico: {valor_actual}",
                    "level": "Critical",
                    "timestamp": time.strftime("%H:%M:%S")
                })
    except Exception as e:
        print(f"Error evaluando reglas: {e}")

# --- MQTT ---
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        socketio.emit('sensor_update', data) # Datos para gráficas
        evaluar_reglas(data)                 # Chequear alertas
    except Exception as e:
        print(f"Error procesando MQTT: {e}")

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_message = on_message

def start_mqtt():
    try:
        mqtt_client.connect("mqtt-broker", 1883, 60)
        mqtt_client.subscribe("welltech/sensors")
        mqtt_client.loop_start()
    except: pass

# --- RUTAS API ---
@app.route('/rules', methods=['GET'])
def get_rules():
    response = table.scan()
    return jsonify(response.get('Items', []))

@app.route('/rules', methods=['POST'])
def add_rule():
    data = request.json
    item = {
        'id': str(uuid.uuid4()),
        'name': str(data.get('name')),
        'variable': str(data.get('variable')),
        'operator': str(data.get('operator')),
        'value': Decimal(str(data.get('value')))
    }
    table.put_item(Item=item)
    return jsonify(item), 201

@app.route('/rules/<id>', methods=['DELETE'])
def delete_rule(id):
    table.delete_item(Key={'id': id})
    return jsonify({"status": "deleted"}), 200

if __name__ == '__main__':
    start_mqtt()
    # Asegurar tabla
    try:
        dynamodb.create_table(
            TableName='MonitoringRules',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
    except: pass
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)