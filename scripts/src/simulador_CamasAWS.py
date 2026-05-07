import json
import os
import random
import time
from dataclasses import dataclass, field
from pathlib import Path

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import paho.mqtt.client as paho_mqtt


BASE_DIR = Path(__file__).resolve().parents[1]
CERTS_DIR = BASE_DIR / "config" / "certs"

# --- Configuracion MQTT. Por defecto usamos broker local para pruebas. ---
MQTT_TRANSPORT = os.getenv("MQTT_TRANSPORT", "broker").strip().lower()
AWS_IOT_ENDPOINT = os.getenv("AWS_IOT_ENDPOINT", "a3hfcqvqmb234v-ats.iot.eu-west-1.amazonaws.com")
AWS_IOT_PORT = int(os.getenv("AWS_IOT_PORT", "8883"))
AWS_IOT_CLIENT_ID = os.getenv("AWS_IOT_CLIENT_ID", "Prueba_Raul_Cama01")
PATH_TO_CERT = os.getenv("AWS_IOT_CERT", str(CERTS_DIR / "cama01-certificado.pem.crt"))
PATH_TO_KEY = os.getenv("AWS_IOT_PRIVATE_KEY", str(CERTS_DIR / "cama01-private.pem.key"))
PATH_TO_ROOT = os.getenv("AWS_IOT_ROOT_CA", str(CERTS_DIR / "cama01-AmazonRootCA1.pem"))

MQTT_TOPIC = os.getenv("MQTT_TOPIC", "residencia/camas/01/datos").strip()
MQTT_COMMAND_TOPIC = os.getenv("MQTT_COMMAND_TOPIC", "").strip()
MQTT_STATUS_TOPIC = os.getenv("MQTT_STATUS_TOPIC", "").strip()
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_USE_TLS = os.getenv("MQTT_USE_TLS", "false").strip().lower() == "true"
MQTT_QOS = int(os.getenv("MQTT_QOS", "1"))

DEVICE_ID = os.getenv("DEVICE_ID", "Bed-01").strip()
DEVICE_MAC = os.getenv("DEVICE_MAC", "52:54:00:ab:cd:da").strip().lower()
MQTT_BROKER_CLIENT_ID = os.getenv("MQTT_BROKER_CLIENT_ID", f"simulator_{DEVICE_MAC.replace(':', '')}")
DEVICE_TYPE = os.getenv("DEVICE_TYPE", "Double Bed").strip()
IS_DOUBLE_BED = "double" in DEVICE_TYPE.lower()

# --- Configuracion del simulador persistente. ---
SIMULATOR_RUN_MODE = os.getenv("SIMULATOR_RUN_MODE", "service").strip().lower()
NORMAL_CAPTURE_SECONDS = max(1, int(os.getenv("NORMAL_CAPTURE_SECONDS", "10")))
NORMAL_PUBLISH_SECONDS = max(5, int(os.getenv("NORMAL_PUBLISH_SECONDS", "300")))
INITIAL_NORMAL_PUBLISH_SECONDS = max(1, int(os.getenv("INITIAL_NORMAL_PUBLISH_SECONDS", "15")))
REALTIME_CAPTURE_SECONDS = max(1, int(os.getenv("REALTIME_CAPTURE_SECONDS", "1")))
REALTIME_DURATION_SECONDS = max(5, int(os.getenv("REALTIME_DURATION_SECONDS", "30")))
PRESENCE_HEARTBEAT_SECONDS = max(5, int(os.getenv("PRESENCE_HEARTBEAT_SECONDS", "15")))
MAX_BUFFER_READINGS = max(10, int(os.getenv("MAX_BUFFER_READINGS", "5000")))
SERVICE_LOOP_SLEEP_SECONDS = float(os.getenv("SERVICE_LOOP_SLEEP_SECONDS", "0.25"))

# --- Configuracion de escenarios y ocupacion. ---
SCENARIO = os.getenv("SCENARIO", "stable").strip().lower()
OCCUPANCY_MIN_DURATION_SECONDS = max(10, int(os.getenv("OCCUPANCY_MIN_DURATION_SECONDS", "120")))
OCCUPANCY_CHANGE_PROBABILITY = float(os.getenv("OCCUPANCY_CHANGE_PROBABILITY", "0.05"))


SIDE_OFFSETS = {"left": -2, "right": 2}


@dataclass
class ScenarioProfile:
    hr_init: tuple
    hr_target: tuple
    rr_init: tuple
    rr_target: tuple
    hrv_init: tuple
    hrv_target: tuple
    occupied_default: bool = True
    hr_center: float = field(init=False)
    rr_center: float = field(init=False)
    hrv_center: float = field(init=False)

    def __post_init__(self):
        self.hr_center = (self.hr_target[0] + self.hr_target[1]) / 2.0
        self.rr_center = (self.rr_target[0] + self.rr_target[1]) / 2.0
        self.hrv_center = (self.hrv_target[0] + self.hrv_target[1]) / 2.0


SCENARIOS = {
    "stable":      ScenarioProfile(
        hr_init=(60, 80),   hr_target=(65, 75),
        rr_init=(14, 18),   rr_target=(14, 18),
        hrv_init=(40, 70),  hrv_target=(45, 65),
    ),
    "tachycardia": ScenarioProfile(
        hr_init=(105, 130), hr_target=(108, 128),
        rr_init=(18, 24),   rr_target=(18, 24),
        hrv_init=(15, 30),  hrv_target=(18, 28),
    ),
    "bradycardia": ScenarioProfile(
        hr_init=(40, 58),   hr_target=(42, 56),
        rr_init=(12, 16),   rr_target=(12, 16),
        hrv_init=(60, 90),  hrv_target=(65, 85),
    ),
    "tachypnea":   ScenarioProfile(
        hr_init=(65, 85),   hr_target=(65, 80),
        rr_init=(22, 30),   rr_target=(22, 30),
        hrv_init=(35, 60),  hrv_target=(38, 58),
    ),
    "bradypnea":   ScenarioProfile(
        hr_init=(62, 78),   hr_target=(62, 78),
        rr_init=(6, 11),    rr_target=(6, 11),
        hrv_init=(40, 65),  hrv_target=(42, 62),
    ),
    "alert_test":  ScenarioProfile(
        hr_init=(130, 145), hr_target=(128, 145),
        rr_init=(28, 32),   rr_target=(28, 32),
        hrv_init=(8, 12),   hrv_target=(8, 12),
    ),
}


@dataclass
class VitalsState:
    hr: float
    rr: float
    hrv: float
    is_occupied: bool
    next_occupancy_change_at: float = 0.0


@dataclass
class RuntimeState:
    mode: str = "normal"
    realtime_until: float = 0.0
    pending_batch: list = field(default_factory=list)
    next_capture_at: float = 0.0
    next_batch_publish_at: float = 0.0
    next_presence_at: float = 0.0
    vitals: dict = field(default_factory=dict)


def _is_local_broker_transport():
    return MQTT_TRANSPORT in {"broker", "local", "mosquitto", "paho"}


def _get_device_type_label():
    return "Double Bed" if IS_DOUBLE_BED else DEVICE_TYPE or "Standard"


def _get_layout_label():
    return "double" if IS_DOUBLE_BED else "single"


def _get_command_topic():
    if MQTT_COMMAND_TOPIC:
        return MQTT_COMMAND_TOPIC

    if MQTT_TOPIC.endswith("/datos"):
        return MQTT_TOPIC[:-6] + "/cmd"

    return f"{MQTT_TOPIC}/cmd"


def _get_status_topic():
    if MQTT_STATUS_TOPIC:
        return MQTT_STATUS_TOPIC

    if MQTT_TOPIC.endswith("/datos"):
        return MQTT_TOPIC[:-5] + "status"

    return f"{MQTT_TOPIC}/status"


def _build_local_client():
    client = paho_mqtt.Client(client_id=MQTT_BROKER_CLIENT_ID)

    if MQTT_USE_TLS:
        # El broker local del compose usa TCP plano; TLS solo se activa si lo pedimos explicitamente.
        client.tls_set()

    return client


def _build_aws_client():
    client = AWSIoTMQTTClient(AWS_IOT_CLIENT_ID)
    client.configureEndpoint(AWS_IOT_ENDPOINT, AWS_IOT_PORT)
    client.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)
    return client


def load_scenario():
    profile = SCENARIOS.get(SCENARIO)
    if profile is None:
        print(f"[scenario] Escenario desconocido '{SCENARIO}'. Usando 'stable' por defecto.")
        return SCENARIOS["stable"]

    print(f"[scenario] Escenario activo: {SCENARIO}")
    return profile


def init_vitals(scenario, sides):
    now = time.time()
    vitals = {}

    for side in sides:
        side_offset = SIDE_OFFSETS.get(side, 0)
        vitals[side] = VitalsState(
            hr=float(random.randint(*scenario.hr_init) + side_offset),
            rr=float(random.randint(*scenario.rr_init)),
            hrv=float(random.randint(*scenario.hrv_init)),
            is_occupied=scenario.occupied_default,
            next_occupancy_change_at=now + OCCUPANCY_MIN_DURATION_SECONDS,
        )

    return vitals


def step_vitals(vitals_state, side, scenario, ts):
    now = time.time()
    drift = 0.05

    vitals_state.hr += random.uniform(-1.5, 1.5) + drift * (scenario.hr_center - vitals_state.hr)
    vitals_state.rr += random.uniform(-0.5, 0.5) + drift * (scenario.rr_center - vitals_state.rr)
    vitals_state.hrv += random.uniform(-2.0, 2.0) + drift * (scenario.hrv_center - vitals_state.hrv)

    vitals_state.hr = max(20.0, min(250.0, vitals_state.hr))
    vitals_state.rr = max(4.0, min(60.0, vitals_state.rr))
    vitals_state.hrv = max(1.0, min(150.0, vitals_state.hrv))

    if now >= vitals_state.next_occupancy_change_at:
        if random.random() < OCCUPANCY_CHANGE_PROBABILITY:
            vitals_state.is_occupied = not vitals_state.is_occupied
            vitals_state.next_occupancy_change_at = now + OCCUPANCY_MIN_DURATION_SECONDS

    return {
        "heartRate": round(vitals_state.hr),
        "respiratoryRate": round(vitals_state.rr),
        "hrv": round(vitals_state.hrv),
        "isOccupied": vitals_state.is_occupied,
        "side": side or "center",
        "ts": int(ts),
    }


def capture_readings(state, scenario, timestamp):
    if IS_DOUBLE_BED:
        return [
            step_vitals(state.vitals["left"], "left", scenario, timestamp),
            step_vitals(state.vitals["right"], "right", scenario, timestamp),
        ]

    return [step_vitals(state.vitals["center"], "center", scenario, timestamp)]


def build_payload(readings, sampling_seconds, source_mode):
    return {
        "mac": DEVICE_MAC,
        "deviceId": DEVICE_ID,
        "deviceType": _get_device_type_label(),
        "layout": _get_layout_label(),
        "telemetryTopic": MQTT_TOPIC,
        "commandTopic": _get_command_topic(),
        "statusTopic": _get_status_topic(),
        "sourceMode": source_mode,
        "samplingCount": len(readings),
        "samplingSeconds": int(sampling_seconds),
        "data": readings
    }


def build_presence_payload(status="online"):
    return {
        "type": "presence",
        "status": str(status or "online").strip().lower() or "online",
        "mac": DEVICE_MAC,
        "deviceId": DEVICE_ID,
        "deviceName": DEVICE_ID,
        "deviceType": _get_device_type_label(),
        "telemetryTopic": MQTT_TOPIC,
        "commandTopic": _get_command_topic(),
        "statusTopic": _get_status_topic(),
        "ts": int(time.time())
    }


def publish_payload(client, payload):
    serialized_payload = json.dumps(payload)
    client.publish(MQTT_TOPIC, serialized_payload, MQTT_QOS)


def publish_presence(client, status="online"):
    payload = build_presence_payload(status=status)
    client.publish(_get_status_topic(), json.dumps(payload), MQTT_QOS)
    print(f"[presence] Estado enviado: {payload['status']} en {_get_status_topic()}")


def flush_pending_batch(client, state):
    if not state.pending_batch:
        return

    payload = build_payload(
        readings=list(state.pending_batch),
        sampling_seconds=NORMAL_CAPTURE_SECONDS,
        source_mode="normal"
    )
    publish_payload(client, payload)
    print(
        f"[normal] Lote enviado con {payload['samplingCount']} lecturas "
        f"({len(state.pending_batch)} registros en buffer)."
    )
    state.pending_batch.clear()


def publish_realtime_readings(client, readings):
    payload = build_payload(
        readings=readings,
        sampling_seconds=REALTIME_CAPTURE_SECONDS,
        source_mode="realtime"
    )
    publish_payload(client, payload)
    print(f"[realtime] Lectura en vivo enviada con {payload['samplingCount']} muestras.")


def trim_pending_batch(state):
    if len(state.pending_batch) <= MAX_BUFFER_READINGS:
        return

    # Mantenemos solo lo mas reciente para evitar que el simulador crezca sin control si falla la red.
    overflow = len(state.pending_batch) - MAX_BUFFER_READINGS
    del state.pending_batch[:overflow]


def switch_to_normal_mode(state, now=None, use_initial_publish_delay=False):
    current_time = float(now or time.time())
    state.mode = "normal"
    state.realtime_until = 0.0
    state.next_capture_at = current_time
    publish_delay_seconds = INITIAL_NORMAL_PUBLISH_SECONDS if use_initial_publish_delay else NORMAL_PUBLISH_SECONDS
    state.next_batch_publish_at = current_time + publish_delay_seconds
    state.next_presence_at = current_time
    print(
        f"Modo normal activo. Captura cada {NORMAL_CAPTURE_SECONDS}s "
        f"y envio por lotes cada {NORMAL_PUBLISH_SECONDS}s."
    )


def switch_to_realtime_mode(state, duration_seconds=None, now=None):
    current_time = float(now or time.time())
    realtime_duration = max(1, int(duration_seconds or REALTIME_DURATION_SECONDS))
    state.mode = "realtime"
    state.realtime_until = current_time + realtime_duration
    state.next_capture_at = current_time
    state.next_presence_at = current_time
    print(
        f"Modo realtime activo durante {realtime_duration}s. "
        f"Se publicara una lectura cada {REALTIME_CAPTURE_SECONDS}s."
    )


def ensure_mode_expiration(state):
    if state.mode != "realtime":
        return

    if time.time() < state.realtime_until:
        return

    print("Ventana realtime finalizada. Volviendo a modo normal.")
    switch_to_normal_mode(state)


def _parse_message_payload(message):
    raw_payload = message.payload.decode() if isinstance(message.payload, bytes) else message.payload
    return json.loads(raw_payload or "{}")


def apply_command(state, payload):
    command_type = str(payload.get("type") or "").strip().lower()
    mode = str(payload.get("mode") or "").strip().lower()

    if command_type != "set_stream_mode":
        print(f"Comando ignorado. Tipo no soportado: {command_type or 'empty'}")
        return

    if mode == "realtime":
        requested_duration = payload.get("durationSeconds") or payload.get("duration")
        switch_to_realtime_mode(state, duration_seconds=requested_duration)
        return

    if mode == "normal":
        switch_to_normal_mode(state)
        return

    print(f"Comando ignorado. Modo no soportado: {mode or 'empty'}")


def build_command_handler(state):
    def handle_message(client, userdata, message):
        try:
            payload = _parse_message_payload(message)
            print(f"Comando recibido en {_get_command_topic()}: {payload}")
            apply_command(state, payload)
        except Exception as error:
            print(f"No se pudo procesar el comando MQTT: {error}")

    return handle_message


def connect_client(state, subscribe_commands=True):
    command_topic = _get_command_topic()

    if _is_local_broker_transport():
        client = _build_local_client()

        def on_connect(local_client, userdata, flags, rc):
            if rc != 0:
                print(f"No se pudo conectar al broker MQTT local. Codigo: {rc}")
                return

            print(f"Conectado al broker MQTT local en {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")

            if subscribe_commands:
                local_client.subscribe(command_topic, MQTT_QOS)
                print(f"Suscrito al topic de comandos: {command_topic}")

        client.on_connect = on_connect
        if subscribe_commands:
            client.on_message = build_command_handler(state)
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
        client.loop_start()
        return client

    client = _build_aws_client()
    client.connect()
    if subscribe_commands:
        client.subscribe(command_topic, MQTT_QOS, lambda c, u, m: build_command_handler(state)(c, u, m))
        print(f"Conectado a AWS IoT Core y suscrito al topic de comandos: {command_topic}")
    else:
        print("Conectado a AWS IoT Core (sin suscripcion a comandos).")
    return client


def disconnect_client(client):
    if not client:
        return

    try:
        if _is_local_broker_transport():
            client.loop_stop()
            client.disconnect()
            return

        client.disconnect()
    except Exception as error:
        print(f"Error cerrando la conexion MQTT: {error}")


def _init_runtime_state():
    scenario = load_scenario()
    sides = ["left", "right"] if IS_DOUBLE_BED else ["center"]
    return scenario, RuntimeState(vitals=init_vitals(scenario, sides))


def run_once(batch_size=40):
    scenario, state = _init_runtime_state()

    readings = []
    current_timestamp = int(time.time())

    for _ in range(batch_size):
        readings.extend(capture_readings(state, scenario, current_timestamp))
        current_timestamp += NORMAL_CAPTURE_SECONDS

    client = None
    try:
        client = connect_client(state, subscribe_commands=False)
        payload = build_payload(readings, NORMAL_CAPTURE_SECONDS, "manual")
        publish_payload(client, payload)
        print(f"Envio manual completado. Se han publicado {payload['samplingCount']} muestras.")
        time.sleep(1)
    except Exception as error:
        print(f"Error en el envio manual: {error}")
    finally:
        disconnect_client(client)


def run_service():
    scenario, state = _init_runtime_state()
    switch_to_normal_mode(state, use_initial_publish_delay=True)
    client = None

    try:
        client = connect_client(state)
        print(f"Publicando telemetria en: {MQTT_TOPIC}")
        print(f"Escuchando comandos en: {_get_command_topic()}")
        print(f"Publicando presencia en: {_get_status_topic()}")
        publish_presence(client, status="online")

        while True:
            now = time.time()
            ensure_mode_expiration(state)

            current_capture_interval = (
                REALTIME_CAPTURE_SECONDS if state.mode == "realtime" else NORMAL_CAPTURE_SECONDS
            )

            if now >= state.next_capture_at:
                readings = capture_readings(state, scenario, int(now))
                state.next_capture_at = now + current_capture_interval

                if state.mode == "realtime":
                    publish_realtime_readings(client, readings)
                else:
                    state.pending_batch.extend(readings)
                    trim_pending_batch(state)
                    print(
                        f"[normal] Captura almacenada. "
                        f"Buffer pendiente: {len(state.pending_batch)} lecturas."
                    )

            if state.mode == "normal" and state.pending_batch and now >= state.next_batch_publish_at:
                flush_pending_batch(client, state)
                state.next_batch_publish_at = now + NORMAL_PUBLISH_SECONDS

            if now >= state.next_presence_at:
                publish_presence(client, status="online")
                state.next_presence_at = now + PRESENCE_HEARTBEAT_SECONDS

            time.sleep(SERVICE_LOOP_SLEEP_SECONDS)

    except KeyboardInterrupt:
        print("Simulador detenido manualmente.")
    except Exception as error:
        print(f"Error en el simulador: {error}")
    finally:
        if client:
            try:
                publish_presence(client, status="offline")
            except Exception:
                pass
        disconnect_client(client)


if __name__ == "__main__":
    if SIMULATOR_RUN_MODE == "once":
        run_once()
    else:
        run_service()
