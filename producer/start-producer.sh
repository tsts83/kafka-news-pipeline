#!/bin/bash

KAFKA_HOST=${KAFKA_HOST:-kafka}
KAFKA_PORT=${KAFKA_PORT:-9092}
TIMEOUT=120

echo "🕒 Waiting for Kafka at $KAFKA_HOST:$KAFKA_PORT (timeout: ${TIMEOUT}s)..."

start_time=$(date +%s)

while true; do
  if nc -zv "$KAFKA_HOST" "$KAFKA_PORT" 2>/dev/null; then
    echo "✅ Kafka is available at $KAFKA_HOST:$KAFKA_PORT"
    break
  fi

  current_time=$(date +%s)
  elapsed=$((current_time - start_time))

  if [ "$elapsed" -ge "$TIMEOUT" ]; then
    echo "❌ Timeout: Kafka not available after $TIMEOUT seconds."
    exit 1
  fi

  echo "⏳ Still waiting... (${elapsed}s elapsed)"
  sleep 2
done

echo "🚀 Starting producer..."
exec python producer.py
