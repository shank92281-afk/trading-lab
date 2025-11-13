import os, json, time, threading
from kafka import KafkaConsumer, KafkaProducer, KafkaAdminClient
import redis
from fastapi import FastAPI
import uvicorn
from prometheus_client import start_http_server, Counter

KAFKA = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

# ---- WAIT FOR KAFKA ----
def wait_for_kafka():
    while True:
        try:
            KafkaAdminClient(bootstrap_servers=KAFKA)
            print("matching-engine: Kafka is ready")
            return
        except:
            print("waiting for Kafka...")
            time.sleep(3)

# ---- WAIT FOR REDIS ----
def wait_for_redis():
    client = redis.Redis(host=REDIS_HOST, port=6379)
    while True:
        try:
            client.ping()
            print("matching-engine: Redis is ready")
            return
        except:
            print("waiting for Redis...")
            time.sleep(3)

wait_for_kafka()
wait_for_redis()

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
TRADES = Counter("trades_total", "Number of trades")
start_http_server(8007)

consumer = KafkaConsumer(
    "orders",
    bootstrap_servers=KAFKA,
    auto_offset_reset="earliest",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    group_id="matching-group"
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA,
    value_serializer=lambda v: json.dumps(v).encode()
)

api = FastAPI()

@api.get("/trade/{order_id}")
def get_trade(order_id: str):
    data = r.get(f"trade:{order_id}")
    if not data:
        return {"found": False, "order_id": order_id}
    return {"found": True, "order_id": order_id, "trade": json.loads(data)}

# ---- WORKER THREAD ----
def worker():
    print("matching-engine: consumer started")
    for msg in consumer:
        order = msg.value
        print("matching-engine: received", order)

        trade = {
            "order_id": order["id"],
            "price": order["price"],
            "qty": order["qty"],
            "ts": time.time()
        }

        producer.send("trades", trade)
        r.set(f"trade:{order['id']}", json.dumps(trade))
        TRADES.inc()

        print("matching-engine: produced", trade)

threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8003)
