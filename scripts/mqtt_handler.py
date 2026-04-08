import json
import os

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

from rules_engine import check_rules_and_save


AWS_IOT_ENDPOINT = os.getenv("AWS_IOT_ENDPOINT", "a3hfcqvqmb234v-ats.iot.eu-west-1.amazonaws.com")
AWS_IOT_PORT = int(os.getenv("AWS_IOT_PORT", "8883"))
AWS_IOT_CLIENT_ID = os.getenv("AWS_IOT_CLIENT_ID", "backend_listener_welltech")
AWS_IOT_TOPIC = os.getenv("AWS_IOT_TOPIC", "residencia/camas/+/datos")
AWS_IOT_ROOT_CA = os.getenv("AWS_IOT_ROOT_CA", "certs/cama01-AmazonRootCA1.pem")
AWS_IOT_CERT = os.getenv("AWS_IOT_CERT", "certs/cama01-certificado.pem.crt")
AWS_IOT_PRIVATE_KEY = os.getenv("AWS_IOT_PRIVATE_KEY", "certs/cama01-private.pem.key")
AWS_IOT_QOS = int(os.getenv("AWS_IOT_QOS", "1"))


def normalizar_payload(payload):
    readings = payload.get("data", [])
    if not isinstance(readings, list) or not readings:
        return None

    last_reading = readings[-1]

    normalized_last_reading = {
        "heartRate": last_reading.get("heartRate"),
        "respiratoryRate": last_reading.get("respiratoryRate"),
        "hrv": last_reading.get("hrv"),
        "isOccupied": last_reading.get("isOccupied"),
        "ts": last_reading.get("ts")
    }

    return {
        "mac": payload.get("mac", "unknown"),
        "deviceId": payload.get("deviceId", "unknown"),
        "lastReading": normalized_last_reading,
        "readings": readings
    }


def on_message(client, userdata, message, socketio):
    try:
        raw_payload = message.payload.decode() if isinstance(message.payload, bytes) else message.payload
        payload = json.loads(raw_payload)
        normalized = normalizar_payload(payload)


        if not normalized:
            print("Payload recibido sin lecturas validas. Se ignora el mensaje.")
            return

        socketio.emit("sensor_update", normalized)

        data_for_rules = {
            "mac": normalized["mac"],
            "deviceId": normalized["deviceId"],
            **normalized["lastReading"]
        }
        check_rules_and_save(data_for_rules)

    except Exception as e:
        print(f"Error procesando mensaje MQTT desde AWS IoT Core: {e}")


def start_mqtt(socketio):
    client = AWSIoTMQTTClient(AWS_IOT_CLIENT_ID)
    client.configureEndpoint(AWS_IOT_ENDPOINT, AWS_IOT_PORT)
    client.configureCredentials(AWS_IOT_ROOT_CA, AWS_IOT_PRIVATE_KEY, AWS_IOT_CERT)

    try:
        client.connect()
        client.subscribe(
            AWS_IOT_TOPIC,
            AWS_IOT_QOS,
            lambda c, u, m: on_message(c, u, m, socketio)
        )
        print(f"MQTT AWS conectado y escuchando en {AWS_IOT_TOPIC}")
        return client
    except Exception as e:
        print(f"No se pudo conectar a AWS IoT Core: {e}")
        return None
