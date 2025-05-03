#!/bin/bash
host="kafka"
port="9092"
shift 2
cmd="$@"

until nc -zv "$host" "$port"; do
  echo "Waiting for Kafka at $host:$port to be available..."
  sleep 1
done

echo "Kafka is available at $host:$port, running the command..."
exec $cmd
