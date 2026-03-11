import paho.mqtt.client as mqtt
import time
import json
import random

MQTT_BROKER = "mqtt-broker" # Nombre del servicio en docker-compose
MQTT_TOPIC = "welltech/sensors"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def run_simulation():
    # Intentar conectar al broker
    connected = False
    while not connected:
        try:
            client.connect(MQTT_BROKER, 1883, 60)
            connected = True
            print("✅ [Cama] Conectada al Broker MQTT")
        except:
            print("❌ [Cama] Esperando al Broker...")
            time.sleep(2)

    while True:
        # Generar datos simulados
        data = {
            "heartRate": random.randint(45, 115),
            "respiratoryRate": random.randint(8, 25),
            "hrv": random.randint(15, 80),
            "isOccupied": random.choice([True, False])
        }
        
        # Publicar en el topic
        client.publish(MQTT_TOPIC, json.dumps(data))
        print(f"📤 [Cama] Datos enviados: {data['heartRate']} BPM")
        
        time.sleep(2)

if __name__ == "__main__":
    run_simulation()