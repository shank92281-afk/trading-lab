import os, socket
from fastapi import FastAPI, Request
import httpx

app = FastAPI()
BACKEND_ORDER = os.getenv("BACKEND_ORDER_URL", "http://nginx/order")

@app.get("/whoami")
def whoami():
    return {"service":"api-gateway", "hostname": socket.gethostname()}

@app.post("/place_order")
async def place_order(payload: dict, request: Request):
    # forward the order to order-service via nginx order endpoint
    async with httpx.AsyncClient() as client:
        resp = await client.post(BACKEND_ORDER, json=payload, timeout=10.0)
        return resp.json()

@app.get("/health")
def health():
    return {"status":"ok"}
