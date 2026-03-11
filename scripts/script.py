from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import json
import paho.mqtt.client as mqtt
import os
import boto3
import uuid
import time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# --- CONFIGURACIÓN DYNAMODB ---
db_url = os.environ.get("DYNAMODB_URL", "http://dynamodb-local:8000")
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=db_url,
    region_name='us-east-1', 
    aws_access_key_id='local', 
    aws_secret_access_key='local'
)
table = dynamodb.Table('MonitoringRules')

# --- LÓGICA DE EVALUACIÓN DE REGLAS ---
def evaluar_reglas(datos_sensor):
    try:
        # Traemos todas las reglas de la base de datos
        response = table.scan()
        reglas = response.get('Items', [])
        
        for regla in reglas:
            # Mapeo de variables: 'hr' -> heartRate, 'resp' -> respiratoryRate, 'hrv' -> hrv
            valor_actual = 0
            if regla['variable'] == 'hr':
                valor_actual = datos_sensor.get('heartRate', 0)
            elif regla['variable'] == 'resp':
                valor_actual = datos_sensor.get('respiratoryRate', 0)
            elif regla['variable'] == 'hrv':
                valor_actual = datos_sensor.get('hrv', 0)
            
            # Comprobación de la condición
            disparada = False
            limite = int(regla['value'])
            
            if regla['operator'] == '>' and valor_actual > limite:
                disparada = True
            elif regla['operator'] == '<' and valor_actual < limite:
                disparada = True
            
            if disparada:
                msg_alerta = f"⚠️ [ALERTA] {regla['name']}: {valor_actual} {regla['operator']} {limite}"
                print(msg_alerta)
                socketio.emit('new_alert', {
                    "id": str(uuid.uuid4()),
                    "sensor": regla['name'],
                    "message": f"Valor crítico detectado: {valor_actual}",
                    "level": "Critical",
                    "timestamp": time.strftime("%H:%M:%S")
                })
    except Exception as e:
        print(f"❌ Error evaluando reglas: {e}")

# --- MQTT: ESCUCHAR A LA CAMA ---
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        # 1. Enviar datos brutos al Frontend para gráficas en tiempo real
        socketio.emit('sensor_update', data)
        # 2. Evaluar si cumplen alguna regla de la DB
        evaluar_reglas(data)
    except Exception as e:
        print(f"Error procesando mensaje MQTT: {e}")

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_message = on_message

def start_mqtt():
    try:
        mqtt_client.connect("mqtt-broker", 1883, 60)
        mqtt_client.subscribe("welltech/sensors")
        mqtt_client.loop_start()
        print("✅ [MQTT] Suscrito a topic: welltech/sensors")
    except Exception as e:
        print(f"❌ No se pudo conectar a MQTT: {e}")

# --- RUTAS API PARA EL FRONTEND ---
@app.route('/rules', methods=['POST'])
def add_rule():
    try:
        data = request.json
        item = {
            'id': str(uuid.uuid4()),
            'name': data.get('name'),
            'variable': data.get('variable'), 
            'operator': data.get('operator'), 
            'value': int(data.get('value'))
        }
        table.put_item(Item=item)
        return jsonify({"status": "success", "id": item['id']}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/rules', methods=['GET'])
def get_rules():
    response = table.scan()
    return jsonify(response.get('Items', []))

# --- ARRANQUE DEL SERVIDOR ---
if __name__ == '__main__':
    # Inicializar MQTT
    start_mqtt()
    
    # Crear tabla si no existe (con espera para evitar errores)
    try:
        existing_tables = dynamodb.meta.client.list_tables()['TableNames']
        if 'MonitoringRules' not in existing_tables:
            print("📦 Creando tabla 'MonitoringRules' en DynamoDB...")
            dynamodb.create_table(
                TableName='MonitoringRules',
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            )
            # Esperar a que la tabla esté activa antes de seguir
            waiter = dynamodb.meta.client.get_waiter('table_exists')
            waiter.wait(TableName='MonitoringRules')
            print("✅ Tabla lista para usar.")
        else:
            print("✅ La tabla ya existe.")
    except Exception as e:
        print(f"Aviso DynamoDB: {e}")

    # Ejecutar Flask
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)