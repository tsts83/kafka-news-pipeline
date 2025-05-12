FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y netcat-openbsd && \
    chmod +x start-producer.sh

RUN pip install --no-cache-dir -r requirements.txt

CMD ["./start-producer.sh"]
