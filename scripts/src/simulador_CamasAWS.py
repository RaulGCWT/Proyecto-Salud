import json
import os
import random
import time
from pathlib import Path

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import paho.mqtt.client as paho_mqtt

BASE_DIR = Path(__file__).resolve().parents[1]
CERTS_DIR = BASE_DIR / "config" / "certs"

# --- Configuracion MQTT. Por defecto usa AWS IoT y, si lo activas, puede apuntar a un broker local. ---
MQTT_TRANSPORT = os.getenv("MQTT_TRANSPORT", "broker").strip().lower()
AWS_IOT_ENDPOINT = os.getenv("AWS_IOT_ENDPOINT", "a3hfcqvqmb234v-ats.iot.eu-west-1.amazonaws.com")
AWS_IOT_PORT = int(os.getenv("AWS_IOT_PORT", "8883"))
AWS_IOT_CLIENT_ID = os.getenv("AWS_IOT_CLIENT_ID", "Prueba_Raul_Cama01")
PATH_TO_CERT = os.getenv("AWS_IOT_CERT", str(CERTS_DIR / "cama01-certificado.pem.crt"))
PATH_TO_KEY = os.getenv("AWS_IOT_PRIVATE_KEY", str(CERTS_DIR / "cama01-private.pem.key"))
PATH_TO_ROOT = os.getenv("AWS_IOT_ROOT_CA", str(CERTS_DIR / "cama01-AmazonRootCA1.pem"))
TOPIC = os.getenv("MQTT_TOPIC", "residencia/camas/01/datos")
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_BROKER_CLIENT_ID = os.getenv("MQTT_BROKER_CLIENT_ID", "cama_simulator_local")
MQTT_USE_TLS = os.getenv("MQTT_USE_TLS", "false").strip().lower() == "true"
DEVICE_ID = os.getenv("DEVICE_ID", "Bed-01")
DEVICE_MAC = os.getenv("DEVICE_MAC", "52:54:00:ab:cd:ju")
SAMPLING_SECONDS = int(os.getenv("SAMPLING_SECONDS", "10"))
SIMULATION_TIMESTAMP_MODE = os.getenv("SIMULATION_TIMESTAMP_MODE", "burst").strip().lower()
SIMULATION_BURST_SIZE = int(os.getenv("SIMULATION_BURST_SIZE", "10"))
SIMULATION_GAP_SECONDS = int(os.getenv("SIMULATION_GAP_SECONDS", "180"))


def _is_local_broker_transport():
    return MQTT_TRANSPORT in {"broker", "local", "mosquitto", "paho"}


def _build_local_client():
    client = paho_mqtt.Client(client_id=MQTT_BROKER_CLIENT_ID)

    if MQTT_USE_TLS:
        # El broker local del compose usa TCP plano; TLS solo se activa si lo pedimos explícitamente.
        client.tls_set()

    return client


def _build_aws_client():
    client = AWSIoTMQTTClient(AWS_IOT_CLIENT_ID)
    client.configureEndpoint(AWS_IOT_ENDPOINT, AWS_IOT_PORT)
    client.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)
    return client


def generar_lectura(ts):
    return {
        "heartRate": random.randint(65, 120),
        "respiratoryRate": random.randint(12, 35),
        "hrv": random.randint(25, 75),
        "isOccupied": random.choice([True, False]),
        "ts": ts
    }


def _build_lot_timestamps(cantidad):
    ahora = int(time.time())

    # El modo "exact" sirve para reproducir el instante real de envío.
    # El modo "spread" reparte el lote para que la gráfica se vea de forma más clara en demo.
    if SIMULATION_TIMESTAMP_MODE in {"exact", "same"}:
        return [ahora] * cantidad

    if SIMULATION_TIMESTAMP_MODE == "exact":
        timestamps = []
        burst_size = max(1, SIMULATION_BURST_SIZE)
        gap_seconds = max(1, SIMULATION_GAP_SECONDS)
        burst_count = max(1, (cantidad + burst_size - 1) // burst_size)
        current_ts = ahora - ((burst_count - 1) * gap_seconds)

        for index in range(cantidad):
            timestamps.append(current_ts)

            if (index + 1) % burst_size == 0:
                current_ts += gap_seconds

        return timestamps

    return [ahora - ((cantidad - 1 - i) * SAMPLING_SECONDS) for i in range(cantidad)]


def generar_lote(cantidad=40):
    lecturas = []
    timestamps = _build_lot_timestamps(cantidad)

    for ts in timestamps:
        lecturas.append(generar_lectura(ts))

    return {
        "mac": DEVICE_MAC,
        "deviceId": DEVICE_ID,
        "samplingCount": cantidad,
        "samplingSeconds": SAMPLING_SECONDS,
        "data": lecturas
    }


def enviar_lote(cantidad=40):
    payload = generar_lote(cantidad)

    try:
        if _is_local_broker_transport():
            print(f"Conectando al broker MQTT local en {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
            client = _build_local_client()
            client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
            client.loop_start()

            print(f"Enviando lote de {cantidad} lecturas a {TOPIC}...")
            client.publish(TOPIC, json.dumps(payload), 1)

            time.sleep(1)

            client.loop_stop()
            client.disconnect()
            print("Envio completado con exito. Desconectado del broker local.")
            return

        print("Conectando a AWS IoT Core...")
        client = _build_aws_client()
        client.connect()

        print(f"Enviando lote de {cantidad} lecturas a {TOPIC}...")
        client.publish(TOPIC, json.dumps(payload), 1)

        time.sleep(1)

        client.disconnect()
        print("Envio completado con exito. Desconectado.")

    except Exception as e:
        print(f"Error en el envio: {e}")


if __name__ == "__main__":
    enviar_lote(40)
