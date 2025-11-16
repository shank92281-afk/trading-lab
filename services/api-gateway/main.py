import os, socket
from fastapi import FastAPI, Header, HTTPException
import httpx
import jwt
from pydantic import BaseModel

app = FastAPI()

# Correct backend internal URL
ORDER_URL = os.getenv("ORDER_URL", "http://order-svc-1:8001/order")

SECRET = os.getenv("JWT_SECRET", "MY_SUPER_SECRET")

class PlaceOrderReq(BaseModel):
    id: str
    price: float
    qty: int
    symbol: str

@app.get("/whoami")
def whoami():
    return {"service": "api-gateway", "hostname": socket.gethostname()}

def verify_token(auth_header: str):
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = auth_header.split(" ", 1)[1]

    try:
        decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
        return decoded
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.post("/place_order")
def place_order(req: PlaceOrderReq, authorization: str = Header(None)):

    user = verify_token(authorization)

    order = {
        "id": req.id,
        "price": req.price,
        "qty": req.qty,
        "symbol": req.symbol,
        "user": user["user_id"]
    }

    # Send to internal order-service
    resp = httpx.post(ORDER_URL, json=order, timeout=5)
    return resp.json()

