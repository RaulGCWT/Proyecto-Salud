import paho.mqtt.client as mqtt
import time
import json
import random
import sys

MQTT_BROKER = "mqtt-broker"
MQTT_TOPIC = "welltech/sensors"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

def generate_random_mac():
    return "52:54:00:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )

def run_simulation(mac_address=None):
    if not mac_address:
        mac_address = generate_random_mac()
    
    connected = False
    while not connected:
        try:
            client.connect(MQTT_BROKER, 1883, 60)
            connected = True
            print(f"✅ [Cama {mac_address}] Conectada")
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
        print(f"📤 [{mac_address}] Datos enviados")
        time.sleep(random.uniform(2.0, 5.0))

if __name__ == "__main__":
    target_mac = sys.argv[1] if len(sys.argv) > 1 else None
    run_simulation(target_mac)