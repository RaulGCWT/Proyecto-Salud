FROM python:3.11-slim
WORKDIR /app
# Añadimos boto3
RUN pip install flask flask-cors flask-socketio paho-mqtt boto3
COPY script.py .
EXPOSE 5000
CMD ["python", "script.py"]