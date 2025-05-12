import requests
from confluent_kafka import Producer
import json
import time
import os
import sys
import argparse
from dotenv import load_dotenv

sys.stdout.reconfigure(line_buffering=True)

# Load environment variables
load_dotenv()

KAFKA_HOST = os.getenv("KAFKA_HOST", "kafka")
KAFKA_PORT = int(os.getenv("KAFKA_PORT", "9092"))
KAFKA_BOOTSTRAP_SERVERS = f"{KAFKA_HOST}:{KAFKA_PORT}"
TOPIC = "news_headlines"
API_KEY = os.getenv("NEWSDATA_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Did you set NEWSDATA_API_KEY in the .env file?")

# Kafka Producer setup (lazy init for lambda)
producer = None

def init_producer():
    global producer
    if producer is None:
        print(f"🚀 Initializing Kafka Producer to {KAFKA_BOOTSTRAP_SERVERS}")
        producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})

def get_news():
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&language=en&q=Economy%20AND%20World%20News"
    print(f"🌐 Fetching news from API: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get("results", [])
        print(f"📰 Retrieved {len(results)} news articles.")
        return results
    except Exception as e:
        print(f"❌ Failed to fetch news: {e}")
        return []

def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Delivered message to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def produce_news():
    init_producer()
    print("📡 Starting fetch & produce cycle...")
    try:
        headlines = get_news()
        print(f"✅ Fetched {len(headlines)} articles.")
        for idx, article in enumerate(headlines):
            payload = json.dumps({
                "title": article.get("title"),
                "link": article.get("link"),
                "pubDate": article.get("pubDate"),
                "description": article.get("description"),
                "image_url": article.get("image_url")
            })
            print(f"➡️ Sending article {idx+1}/{len(headlines)}: {article.get('title')}")
            producer.produce(TOPIC, payload.encode('utf-8'), callback=delivery_report)
        producer.flush()
        print("✅ All articles produced.")
    except Exception as e:
        print(f"⚠️ Error during production: {e}")

# Lambda entrypoint
def lambda_handler(event, context):
    print("🟢 Lambda invocation received.")
    produce_news()
    return {"status": "success", "message": "News produced to Kafka"}

# CLI entrypoint
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kafka News Producer")
    parser.add_argument('--mode', choices=['local', 'lambda'], default='local', help='Run mode: local or lambda')
    args = parser.parse_args()

    if args.mode == "local":
        print("🔁 Running in LOCAL mode (infinite loop)")
        while True:
            produce_news()
            print("⏲️ Sleeping for 60 seconds...\n")
            time.sleep(60)
    else:
        print("⚡ Running in LAMBDA mode (single execution)")
        lambda_handler({}, {})
