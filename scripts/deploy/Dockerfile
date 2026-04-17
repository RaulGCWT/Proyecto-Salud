FROM python:3.11-slim

WORKDIR /app

# Instalamos todas las librerías necesarias, incluyendo 'requests' para el registro en DB
RUN pip install --no-cache-dir flask flask-cors flask-socketio paho-mqtt boto3 requests AWSIoTPythonSDK


# Copiamos el código fuente al contenedor
COPY . .

# Exponemos el puerto del backend (solo relevante para el servicio backend)
EXPOSE 5000

# Ejecutamos la aplicación real directamente desde el paquete `src`.
CMD ["python", "-m", "src.app"]
