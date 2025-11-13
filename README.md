📈 Trading Lab — Distributed Microservices Trading Platform

A fully containerized, event-driven trading platform designed to simulate real-world high-frequency and low-latency architectures used by exchanges and fintech systems.

This lab is built using:

FastAPI microservices

Kafka (event streaming)

Redis (fast storage)

Nginx reverse proxy / API gateway

Docker & Docker Compose

Simple HTML frontend

The project demonstrates how real exchanges route, process, match, and confirm trades across distributed services.

🏗️ High-Level Architecture Diagram
                        ┌────────────────────┐
                        │    Frontend UI     │
                        │ (HTML + Fetch API) │
                        └─────────┬──────────┘
                                  │  HTTP
                                  ▼
                        ┌────────────────────┐
                        │        NGINX        │
                        │ (Reverse Proxy +    │
                        │   Load Balancer)    │
                        └─────────┬──────────┘
        HTTP Routing:  /place_order | /trade/<id> | /order etc
                                  │
 ┌────────────────────────────────┼──────────────────────────────────┐
 │                                │                                  │
 ▼                                ▼                                  ▼
┌────────────────────┐   ┌────────────────────┐            ┌────────────────────┐
│   API Gateway (2x) │   │ Order Service (2x) │            │  Matching Engine   │
│ FastAPI + LB pool  │   │ Receives order,    │            │ Kafka consumer     │
│ /place_order        │   │ publishes to Kafka │            │ produces trades    │
└─────────┬──────────┘   └─────────┬──────────┘            └─────────┬──────────┘
          │                        │ Kafka (orders)                  │ Redis
          │                        ▼                                 │ (trade store)
          │                ┌────────────────────┐                    │
          │                │       Kafka        │◄────────────────────┘
          │                │  (Event Broker)    │
          │                └────────────────────┘
          │                        │ Kafka (trades)
          │                        ▼
          │               ┌────────────────────┐
          │               │   Matching Engine  │
          │               │ Publishes trades   │
          │               └────────────────────┘
          │
          ▼
┌────────────────────┐
│      REDIS         │
│ Stores trade as    │
│ trade:<id> → {...} │
└────────────────────┘

🚀 Trade Flow Explained
1️⃣ User places order using HTML frontend

Frontend sends:

POST /place_order
{
  "id": "ui-123",
  "symbol": "ABC",
  "price": 100,
  "qty": 5
}

2️⃣ NGINX reverse proxy routes the request

/place_order → API Gateway load-balanced upstream (api-gw-1 / api-gw-2)

Why?

Because in a large org, API gateways buffer traffic, add auth, rate limit, routing, metrics.

3️⃣ API Gateway forwards to Order Service

API GW simply forwards JSON → Order Service.

Order Service:

accepts order

logs

publishes to Kafka topic: orders

returns response

✔️ THIS IS REAL WORLD — order entry modules always publish to message brokers (Kafka / Pulsar / RabbitMQ).

4️⃣ Kafka receives the order

Kafka acts as:

persistent log

highly-available message broker

buffering layer

decoupling between order intake and matching

This is how Zerodha, NSE, NYSE, Coinbase, Binance etc scale horizontally.

5️⃣ Matching Engine consumes order from Kafka

Matching Engine:

reads from orders topic

simulates “trade execution”

generates trade JSON

publishes to trades topic

stores trade in Redis using:

trade:<order_id>


This mimics real-time matching engines.

6️⃣ Trade confirmation lookup via Nginx

Frontend hits:

GET /trade/<order_id>


NGINX proxies to Matching Engine:

http://matching-engine:8003/trade/<id>


Matching Engine reads from Redis → returns trade.

🧩 Microservices Breakdown (Architect Perspective)
🔹 NGINX Reverse Proxy

Purpose in real companies:

public entrypoint

HTTP routing

load balancing

CORS policies

API versioning

SSL termination

What you learned:
How to map URL paths → internal microservices cleanly.

🔹 API Gateway

Used for:

request validation

auth

routing

request proxying

Here, it simply forwards /place_order → /order service.
In real orgs, it would also add:

logging

tracing

API tokens

WAF rules

🔹 Order Service

This is the Order Entry System — a core part of any trading platform.

Real companies use it to:

validate order

risk check

store order

publish to message broker

In our lab:

publishes to Kafka

returns “order received” immediately

fully stateless → scalable horizontally

🔹 Kafka

The backbone of all event-driven trading systems.

Purpose:

decouple services

high throughput (million events/sec)

persistent event log

horizontal scale

What you learned:

topics

producers

consumers

how microservices communicate in real systems

🔹 Matching Engine

This is where real trades get executed.

In actual exchanges:

order book matching

price-time priority

high-performance C++ engines

In our lab:

simple “echo trade generator”

stores trades in Redis

🔹 Redis

Ultra-fast key-value store.

Used here for:

storing trade confirmations

<1ms read time

scalable shared state across containers

Real systems use Redis for:

caching

session store

fast lookup

reference data

🔹 Frontend

HTML + JS making API calls.

Simulates:

broker terminal

web UI

OMS test UI

🛠️ How to Run
docker-compose up --build


Frontend → http://localhost:8080

API (via nginx) → http://localhost/…

⭐ Why This Project Makes You Architect-Ready

By building this, you learned:

✔️ Microservices design
✔️ Load balancing & reverse proxying
✔️ Event-driven architecture
✔️ Stateless horizontal scaling
✔️ Kafka-based asynchronous workflows
✔️ Containerization
✔️ Service isolation
✔️ Real-world trade flow

This is the kind of architecture fintechs and exchanges run in production.
You built a miniature version end-to-end.
