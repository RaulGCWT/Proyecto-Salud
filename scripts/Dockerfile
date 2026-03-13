FROM python:3.11-slim

WORKDIR /app

# Instalamos las librerías necesarias para el backend y los simuladores
RUN pip install --no-cache-dir flask flask-cors flask-socketio paho-mqtt boto3

# Copiamos todo el contenido (app.py, database.py, mqtt_handler.py, etc.)
COPY . .

# Exponemos el puerto del backend
EXPOSE 5000

# Por defecto el contenedor ejecutará el nuevo punto de entrada app.py
CMD ["python", "app.py"]