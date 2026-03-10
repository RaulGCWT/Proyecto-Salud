FROM python:3.11-slim
WORKDIR /app
RUN pip install flask flask-cors flask-socketio paho-mqtt
COPY script.py .
EXPOSE 5000
CMD ["python", "script.py"]