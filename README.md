📨 News to Kafka Feeder
A simple Python demo that fetches real-time news from NewsData.io and publishes each article to a Kafka topic. Perfect for testing Kafka-based pipelines with live, realistic data.

🔧 Features
Fetches current news via the NewsData.io API

Publishes each article to a Kafka topic in JSON format

Runs in Docker using ```docker compose up --build```

Connects to Kafka via the default ```localhost:9092``` port

Easily configurable with environment variables
