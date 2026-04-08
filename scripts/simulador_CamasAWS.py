import time
import json
import random
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# --- CONFIGURACIÓN DE AWS (Completa con tus datos) ---
ENDPOINT = "a3hfcqvqmb234v-ats.iot.eu-west-1.amazonaws.com" 
CLIENT_ID = "Prueba_Raul_Cama01"
PATH_TO_CERT = "certs/cama01-certificado.pem.crt"
PATH_TO_KEY = "certs/cama01-private.pem.key"
PATH_TO_ROOT = "certs/cama01-AmazonRootCA1.pem"
TOPIC = "residencia/camas/01/datos"


# Inicializar cliente MQTT
myMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
myMQTTClient.configureEndpoint(ENDPOINT, 8883)
myMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)

def enviar_una_rafaga(cantidad=60):
    # 1. Generamos el array de 60 datos en memoria
    lecturas = []
    ahora = int(time.time())
    
    print(f"Generando {cantidad} lecturas simuladas...")
    for i in range(cantidad):
        lectura = {
            "heartRate": random.randint(65, 85),
            "breathRate": random.randint(12, 18),
            "ts": ahora - (cantidad - i)  # Simulamos los últimos 60 segundos
        }
        lecturas.append(lectura)

    # 2. Creamos el mensaje final (Batch)
    payload = {
        "deviceId": "Bed-01",
        "type": "REPORT_60_SEC",
        "data": lecturas
    }

    # 3. Protocolo de envío único
    try:
        print("Conectando a AWS IoT Core...")
        myMQTTClient.connect()
        
        print(f"Enviando paquete completo a {TOPIC}...")
        myMQTTClient.publish(TOPIC, json.dumps(payload), 1)
        
        # Esperamos un segundo para asegurar que el buffer se vacíe
        time.sleep(1) 
        
        myMQTTClient.disconnect()
        print("✅ Envío completado con éxito. Desconectado.")
        
    except Exception as e:
        print(f"❌ Error en el envío: {e}")

# Ejecución única
if __name__ == "__main__":
    enviar_una_rafaga(60)