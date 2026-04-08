import json
import random
import time

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# --- CONFIGURACION DE AWS (Completa con tus datos) ---
ENDPOINT = "a3hfcqvqmb234v-ats.iot.eu-west-1.amazonaws.com"
CLIENT_ID = "Prueba_Raul_Cama01"
PATH_TO_CERT = "certs/cama01-certificado.pem.crt"
PATH_TO_KEY = "certs/cama01-private.pem.key"
PATH_TO_ROOT = "certs/cama01-AmazonRootCA1.pem"
TOPIC = "residencia/camas/01/datos"
DEVICE_ID = "Bed-01"
DEVICE_MAC = "52:54:00:ab:cd:ef"


myMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
myMQTTClient.configureEndpoint(ENDPOINT, 8883)
myMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)


def generar_lectura():
    return {
        "heartRate": random.randint(65, 85),
        "respiratoryRate": random.randint(12, 18),
        "hrv": random.randint(25, 75),
        "isOccupied": random.choice([True, False]),
        "ts": int(time.time())
    }


def generar_lote(cantidad=40):
    lecturas = []

    for _ in range(cantidad):
        lecturas.append(generar_lectura())

    return {
        "mac": DEVICE_MAC,
        "deviceId": DEVICE_ID,
        "samplingCount": cantidad,
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
