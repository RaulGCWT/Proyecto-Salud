import json
import random
import time
from pathlib import Path

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

BASE_DIR = Path(__file__).resolve().parents[1]
CERTS_DIR = BASE_DIR / "config" / "certs"

# --- Configuracion de AWS (ajusta estos valores si cambias de entorno) ---
ENDPOINT = "a3hfcqvqmb234v-ats.iot.eu-west-1.amazonaws.com"
CLIENT_ID = "Prueba_Raul_Cama01"
PATH_TO_CERT = str(CERTS_DIR / "cama01-certificado.pem.crt")
PATH_TO_KEY = str(CERTS_DIR / "cama01-private.pem.key")
PATH_TO_ROOT = str(CERTS_DIR / "cama01-AmazonRootCA1.pem")
TOPIC = "residencia/camas/01/datos"
DEVICE_ID = "Bed-01"
DEVICE_MAC = "52:54:00:ab:cd:ab"
SAMPLING_SECONDS = 10


myMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
myMQTTClient.configureEndpoint(ENDPOINT, 8883)
myMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)


def generar_lectura(ts):
    return {
        "heartRate": random.randint(65, 120),
        "respiratoryRate": random.randint(12, 35),
        "hrv": random.randint(25, 75),
        "isOccupied": random.choice([True, False]),
        "ts": ts
    }


def generar_lote(cantidad=40):
    lecturas = []
    ahora = int(time.time())
    inicio_lote = ahora - ((cantidad - 1) * SAMPLING_SECONDS)

    for i in range(cantidad):
        ts = inicio_lote + (i * SAMPLING_SECONDS)
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
        print("Conectando a AWS IoT Core...")
        myMQTTClient.connect()

        print(f"Enviando lote de {cantidad} lecturas a {TOPIC}...")
        myMQTTClient.publish(TOPIC, json.dumps(payload), 1)

        time.sleep(1)

        myMQTTClient.disconnect()
        print("Envio completado con exito. Desconectado.")

    except Exception as e:
        print(f"Error en el envio: {e}")


if __name__ == "__main__":
    enviar_lote(40)
