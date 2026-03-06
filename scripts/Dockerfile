# Usa una imagen ligera de Python
FROM python:3.11-slim

# Directorio de trabajo en el contenedor
WORKDIR /app

# Instalamos las librerías necesarias
RUN pip install flask flask-cors

# Copiamos el script (que ahora está en la misma carpeta que este Dockerfile)
COPY script.py .

# Exponemos el puerto para Flask
EXPOSE 5000

# Ejecutamos
CMD ["python", "script.py"]