# Usa una imagen base de Python
FROM python:3.12-alpine

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias necesarias: bash, crontab, busybox-suid
RUN apk add --no-cache \
    bash \
    busybox-suid \
    dcron  # Instala el daemon cron y utilidades

# Copia los archivos necesarios para la aplicación
COPY . .

# Instala las dependencias de la aplicación desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que correrá la aplicación
EXPOSE 8000

# Comando para correr el cron y la aplicación
CMD crond && python3 main.py
