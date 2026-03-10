from flask import Flask
from flask_socketio import SocketIO
import random

app = Flask(__name__)
# Permitimos CORS total para evitar bloqueos del navegador
socketio = SocketIO(app, cors_allowed_origins="*")

def generate_sensor_data():
    """Genera datos y los empuja a la web cada 2 segundos"""
    print("Iniciando envío de datos al sensor...")
    while True:
        data = {
            "heartRate": random.randint(60, 110),
            "respiratoryRate": random.randint(12, 22),
            "hrv": random.randint(20, 70),
            "isOccupied": random.choice([True, False])
        }
        socketio.emit('sensor_update', data)
        print(f"Emitido: {data}")
        socketio.sleep(2) # Pausa de 2 segundos sin bloquear el servidor

if __name__ == '__main__':
    # Arrancamos la tarea en segundo plano
    socketio.start_background_task(generate_sensor_data)
    
    # Arrancamos el servidor SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)