FROM python:3.11-slim

WORKDIR /app

# Instalamos las librerías necesarias
# Flask y SocketIO para el backend, paho-mqtt para las camas
RUN pip install flask flask-cors flask-socketio paho-mqtt boto3

# Copiamos todos los scripts a la vez
COPY . .

# Exponemos el puerto del backend (5000)
EXPOSE 5000

# Por defecto el contenedor ejecutará el script del backend, 
# pero el docker-compose lo sobrescribirá para el simulador.
CMD ["python", "script.py"]