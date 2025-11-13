import os, json
from fastapi import FastAPI
from kafka import KafkaProducer
import uvicorn

WHOAMI_ID = os.getenv("WHOAMI_ID", "order-svc-x")
KAFKA = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

app = FastAPI()

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA,
    value_serializer=lambda v: json.dumps(v).encode()
)

@app.post("/order")
async def create_order(order: dict):
    print("order-service:", WHOAMI_ID, "received order", order)

    # Publish to Kafka
    producer.send("orders", order)
    producer.flush()

    print("order-service:", WHOAMI_ID, "published to Kafka:", order)

    return {
        "status": "received",
        "handled_by": WHOAMI_ID,
        "order": order
    }

@app.get("/whoami")
def whoami():
    return {"id": WHOAMI_ID}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

