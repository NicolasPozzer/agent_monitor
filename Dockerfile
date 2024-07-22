FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache \
    bash \
    busybox-suid \
    dcron  # Instala el daemon cron y utilidades

COPY . .

# Istall dependeces from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Port
EXPOSE 8000
CMD crond && python3 main.py
