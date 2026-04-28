import json
import os
import time
import uuid
from pathlib import Path

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import paho.mqtt.client as paho_mqtt

from src.database import table_devices, table_telemetry
from src.rules_engine import check_rules_and_save


BASE_DIR = Path(__file__).resolve().parents[1]
CERTS_DIR = BASE_DIR / "config" / "certs"


MQTT_TRANSPORT = os.getenv("MQTT_TRANSPORT", "aws_iot").strip().lower()
AWS_IOT_ENDPOINT = os.getenv("AWS_IOT_ENDPOINT", "a3hfcqvqmb234v-ats.iot.eu-west-1.amazonaws.com")
AWS_IOT_PORT = int(os.getenv("AWS_IOT_PORT", "8883"))
AWS_IOT_CLIENT_ID = os.getenv("AWS_IOT_CLIENT_ID", "backend_listener_welltech")
AWS_IOT_TOPIC = os.getenv("AWS_IOT_TOPIC", "residencia/camas/+/datos")
AWS_IOT_ROOT_CA = os.getenv("AWS_IOT_ROOT_CA", str(CERTS_DIR / "cama01-AmazonRootCA1.pem"))
AWS_IOT_CERT = os.getenv("AWS_IOT_CERT", str(CERTS_DIR / "cama01-certificado.pem.crt"))
AWS_IOT_PRIVATE_KEY = os.getenv("AWS_IOT_PRIVATE_KEY", str(CERTS_DIR / "cama01-private.pem.key"))
AWS_IOT_QOS = int(os.getenv("AWS_IOT_QOS", "1"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", AWS_IOT_TOPIC)
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_BROKER_CLIENT_ID = os.getenv("MQTT_BROKER_CLIENT_ID", "backend_listener_welltech_local")
MQTT_USE_TLS = os.getenv("MQTT_USE_TLS", "false").strip().lower() == "true"

latest_telemetry = None


def _is_local_broker_transport():
    return MQTT_TRANSPORT in {"broker", "local", "mosquitto", "paho"}


def _normalizar_mac(mac):
    if not mac:
        return ""
    return str(mac).strip().lower()


def registrar_dispositivo_si_no_existe(data):
    mac = _normalizar_mac(data.get("mac"))
    if not mac:
        return

    try:
        existing = table_devices.get_item(Key={"id": mac}).get("Item")
        if existing:
            return

        device_id = str(data.get("deviceId") or mac)
        table_devices.put_item(
            Item={
                "id": mac,
                "mac": mac,
                "deviceId": device_id,
                "type": "Standard",
            }
        )
        print(f"Dispositivo registrado automaticamente: {mac}")
    except Exception as error:
        # Si la tabla no esta disponible, no bloqueamos la actualizacion en tiempo real.
        print(f"No se pudo registrar el dispositivo {mac}: {error}")


def _parse_reading_timestamp(reading):
    raw_timestamp = reading.get("ts")
    try:
        timestamp = int(float(raw_timestamp))
        if timestamp > 0:
            return timestamp
    except (TypeError, ValueError):
        pass

    return int(time.time())


def guardar_lectura_historial(normalized, reading, index):
    mac = _normalizar_mac(normalized.get("mac"))
    device_id = str(normalized.get("deviceId") or mac or "unknown").strip()
    timestamp = _parse_reading_timestamp(reading)

    metadata = {
        "ownerId": "",
        "tenantKey": "",
        "residenceId": "",
        "area": "",
        "residentId": "",
    }

    try:
        if mac:
            device_item = table_devices.get_item(Key={"id": mac}).get("Item") or {}
            metadata.update({
                "ownerId": str(device_item.get("ownerId") or "").strip(),
                "tenantKey": str(device_item.get("tenantKey") or "").strip(),
                "residenceId": str(device_item.get("residenceId") or "").strip(),
                "area": str(device_item.get("area") or "").strip(),
                "residentId": str(device_item.get("residentId") or "").strip(),
            })
    except Exception as error:
        print(f"No se pudo leer la metadata del dispositivo {mac}: {error}")

    try:
        table_telemetry.put_item(
            Item={
                "id": str(uuid.uuid4()),
                "mac": mac or "unknown",
                "deviceId": device_id,
                "timestamp": timestamp,
                "heartRate": reading.get("heartRate"),
                "respiratoryRate": reading.get("respiratoryRate"),
                "hrv": reading.get("hrv"),
                "isOccupied": reading.get("isOccupied"),
                "batchIndex": int(index),
                **metadata,
            }
        )
    except Exception as error:
        # El histórico no debe bloquear la actualización en vivo ni las alertas.
        print(f"No se pudo guardar la lectura histórica para {mac}: {error}")


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
        "ts": last_reading.get("ts"),
    }

    return {
        "mac": payload.get("mac", "unknown"),
        "deviceId": payload.get("deviceId", "unknown"),
        "lastReading": normalized_last_reading,
        "readings": readings,
    }


def on_message(client, userdata, message, socketio):
    global latest_telemetry

    try:
        raw_payload = message.payload.decode() if isinstance(message.payload, bytes) else message.payload
        payload = json.loads(raw_payload)
        normalized = normalizar_payload(payload)

        if not normalized:
            print("Payload recibido sin lecturas validas. Se ignora el mensaje.")
            return

        latest_telemetry = normalized
        socketio.emit("sensor_update", normalized)

        # Emitimos primero para no perder la actualizacion en la UI si falla DynamoDB.
        registrar_dispositivo_si_no_existe(normalized)

        # Guardamos cada lectura para que luego la gráfica y el histórico tengan base real.
        for index, reading in enumerate(normalized["readings"]):
            guardar_lectura_historial(normalized, reading, index)

        # Evaluamos reglas con cada lectura del lote para no perder alertas.
        for reading in normalized["readings"]:
            data_for_rules = {
                "mac": normalized["mac"],
                "deviceId": normalized["deviceId"],
                "heartRate": reading.get("heartRate"),
                "respiratoryRate": reading.get("respiratoryRate"),
                "hrv": reading.get("hrv"),
                "isOccupied": reading.get("isOccupied"),
                "ts": reading.get("ts"),
            }
            check_rules_and_save(data_for_rules)

    except Exception as error:
        print(f"Error procesando mensaje MQTT desde AWS IoT Core: {error}")


def get_latest_telemetry():
    return latest_telemetry or {}


def _on_paho_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Conectado al broker MQTT local en {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        client.subscribe(MQTT_TOPIC, AWS_IOT_QOS)
        print(f"Suscrito al topic MQTT: {MQTT_TOPIC}")
        return

    print(f"No se pudo conectar al broker MQTT local. Código: {rc}")


def _on_paho_message(socketio):
    def handle_message(client, userdata, message):
        on_message(client, userdata, message, socketio)

    return handle_message


def _start_local_broker(socketio):
    client = paho_mqtt.Client(client_id=MQTT_BROKER_CLIENT_ID)

    if MQTT_USE_TLS:
        # Solo activamos TLS si se pide explícitamente; el broker local del compose usa TCP plano.
        client.tls_set()

    client.on_connect = _on_paho_connect
    client.on_message = _on_paho_message(socketio)

    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
        client.loop_start()
        return client
    except Exception as error:
        print(f"No se pudo conectar al broker MQTT local: {error}")
        return None


def _start_aws_iot(socketio):
    client = AWSIoTMQTTClient(AWS_IOT_CLIENT_ID)
    client.configureEndpoint(AWS_IOT_ENDPOINT, AWS_IOT_PORT)
    client.configureCredentials(AWS_IOT_ROOT_CA, AWS_IOT_PRIVATE_KEY, AWS_IOT_CERT)

    try:
        client.connect()
        client.subscribe(
            AWS_IOT_TOPIC,
            AWS_IOT_QOS,
            lambda c, u, m: on_message(c, u, m, socketio),
        )
        return client
    except Exception as error:
        print(f"No se pudo conectar a AWS IoT Core: {error}")
        return None


def start_mqtt(socketio):
    if _is_local_broker_transport():
        print("Arrancando telemetría con broker MQTT local.")
        return _start_local_broker(socketio)

    print("Arrancando telemetría con AWS IoT Core.")
    return _start_aws_iot(socketio)
