from flask import Flask
from flask_socketio import SocketIO
import random
import json
import paho.mqtt.client as mqtt
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

MQTT_BROKER = "mqtt-broker"
MQTT_TOPIC = "welltech/sensors"

# Compatibilidad con Paho MQTT v2.0
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def generate_sensor_data():
    connected = False
    while not connected:
        try:
            print(f"Intentando conectar al broker en {MQTT_BROKER}...")
            mqtt_client.connect(MQTT_BROKER, 1883, 60)
            connected = True
            print("✅ [MQTT] ¡Conexión establecida con éxito!")
        except Exception as e:
            print(f"❌ [MQTT] Error: {e}. Reintentando en 3 segundos...")
            time.sleep(3)
    
    mqtt_client.loop_start()

    while True:
        data = {
            "heartRate": random.randint(45, 115),
            "respiratoryRate": random.randint(8, 25),
            "hrv": random.randint(15, 80),
            "isOccupied": random.choice([True, False])
        }
        
        # Emitir por WebSockets para el Frontend
        socketio.emit('sensor_update', data)
        
        # Publicar por MQTT para el ecosistema IoT
        mqtt_client.publish(MQTT_TOPIC, json.dumps(data))
        
        print(f"📡 Emitido: {data['heartRate']} BPM | Occupied: {data['isOccupied']}")
        socketio.sleep(2)

if __name__ == '__main__':
    socketio.start_background_task(generate_sensor_data)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)