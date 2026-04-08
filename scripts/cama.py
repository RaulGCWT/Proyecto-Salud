import paho.mqtt.client as mqtt
import time
import json
import random
import sys
import requests # <--- Nueva importación

MQTT_BROKER = "mqtt-broker"
MQTT_TOPIC = "welltech/sensors"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def generate_random_mac():
    return "52:54:00:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )

def register_device(mac):
    """Registra el dispositivo intentando varias rutas de red"""
    for host in ['backend', 'localhost']:
        try:
            url = f'http://{host}:5000/devices'
            requests.post(url, json={
                "id": mac,
                "name": f"Bed {mac[-5:]}",
                "type": "Smart Mattress"
            }, timeout=1)
            print(f"📦 [Cama {mac}] Registrada vía {host}")
            return
        except:
            continue
    print(f"⚠️ No se pudo registrar en DB (Backend inaccesible)")

def run_simulation(mac_address=None):
    if not mac_address:
        mac_address = generate_random_mac()
    
    # Registro en base de datos antes de empezar
    register_device(mac_address)
    
    connected = False
    while not connected:
        try:
            client.connect(MQTT_BROKER, 1883, 60)
            connected = True
            print(f"✅ [Cama {mac_address}] Conectada a MQTT")
        except:
            time.sleep(2)

    while True:
        data = {
            "mac": mac_address,
            "heartRate": random.randint(45, 115),
            "respiratoryRate": random.randint(8, 25),
            "hrv": random.randint(15, 80),
            "isOccupied": random.choice([True, False])
        }
        client.publish(MQTT_TOPIC, json.dumps(data))
        time.sleep(3)


if __name__ == "__main__":
    run_simulation()
