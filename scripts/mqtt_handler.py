import paho.mqtt.client as mqtt
import json
from rules_engine import check_rules_and_save

def on_message(client, userdata, msg, socketio):
    try:
        data = json.loads(msg.payload.decode())
        # Enviamos al front por SocketIO
        socketio.emit('sensor_update', data)
        # Pasamos los datos al motor de reglas
        check_rules_and_save(data)
    except Exception as e:
        print(f"❌ Error procesando mensaje MQTT: {e}")

def start_mqtt(socketio):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    # Usamos una función lambda para pasar el objeto socketio al callback
    client.on_message = lambda c, u, m: on_message(c, u, m, socketio)
    
    try:
        client.connect("mqtt-broker", 1883, 60)
        client.subscribe("welltech/sensors")
        client.loop_start()
        print("🚀 MQTT conectado y escuchando...")
    except Exception as e:
        print(f"⚠️ No se pudo conectar a MQTT: {e}")