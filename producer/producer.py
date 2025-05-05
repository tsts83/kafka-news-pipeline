import requests
from confluent_kafka import Producer
import json
import time
import os
from dotenv import load_dotenv
from confluent_kafka.admin import AdminClient
import sys
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

def wait_for_kafka_ready(bootstrap_servers, timeout=180):
    print(f"⏳ Waiting for Kafka at {bootstrap_servers} to become ready...")
    start_time = time.time()
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
    
    while time.time() - start_time < timeout:
        try:
            cluster_metadata = admin_client.list_topics(timeout=5)
            if cluster_metadata.topics:
                print(f"✅ Kafka is ready! Found {len(cluster_metadata.topics)} topics.")
                return
        except Exception as e:
            print(f"Kafka not ready yet: {e}")
        time.sleep(2)

    raise TimeoutError(f"Kafka not ready after {timeout} seconds")

# Wait for Kafka to be ready
# wait_for_kafka_ready(KAFKA_BOOTSTRAP_SERVERS)

print("🚀 Starting Kafka producer...")

# Set up Kafka producer
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

# Main loop to produce messages
while True:
    print("📡 Starting new fetch/produce cycle...")
    try:
        print("➡️ Calling get_news()...")
        headlines = get_news()
        print(f"✅ get_news() returned {len(headlines)} articles.")
        for idx, article in enumerate(headlines):
            payload = json.dumps({
                "title": article.get("title"),
                "link": article.get("link"),
                "pubDate": article.get("pubDate")
                "description": article.get("description"),
                "image_url": article.get("image_url")
            })
            print(f"➡️ Sending article {idx+1}/{len(headlines)}: {article.get('title')}")
            producer.produce(TOPIC, payload.encode('utf-8'), callback=delivery_report)
        producer.flush()
        print("✅ Finished producing all articles.")
    except Exception as e:
        print(f"⚠️ Error during production: {e}")
    
    print("⏲️ Sleeping for 60 seconds...\n")
    time.sleep(60)  # Fetch news every 60 seconds
