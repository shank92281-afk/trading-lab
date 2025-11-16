# services/auth-service/main.py
import os
import time
import socket
import json
from typing import Optional

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import redis
import bcrypt
import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "MY_SUPER_SECRET")
JWT_ALGO = "HS256"
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
TOKEN_TTL_SECONDS = int(os.getenv("TOKEN_TTL_SECONDS", 60 * 60 * 24))  # optional, used for token expiry claim

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

app = FastAPI(title="Auth Service")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)







class SignupReq(BaseModel):
    username: str
    password: str

class LoginReq(BaseModel):
    username: str
    password: str

@app.get("/whoami")
def whoami():
    return {"service": "auth-service", "users_count": r.dbsize()}

@app.post("/signup")
def signup(req: SignupReq):
    username = req.username.strip().lower()
    if not username or not req.password:
        raise HTTPException(status_code=400, detail="username/password required")

    key = f"user:{username}"
    if r.exists(key):
        raise HTTPException(status_code=400, detail="user already exists")

    # hash password
    hashed = bcrypt.hashpw(req.password.encode("utf-8"), bcrypt.gensalt())
    # store user record (simple user model)
    r.hset(key, mapping={
        "password": hashed.decode("utf-8"),
        "created": str(time.time())
    })
    return {"status": "created", "username": username}

@app.post("/login")
def login(req: LoginReq):
    username = req.username.strip().lower()
    key = f"user:{username}"
    if not r.exists(key):
        raise HTTPException(status_code=401, detail="invalid credentials")

    stored = r.hget(key, "password")
    if not stored:
        raise HTTPException(status_code=500, detail="user record invalid")

    if not bcrypt.checkpw(req.password.encode("utf-8"), stored.encode("utf-8")):
        raise HTTPException(status_code=401, detail="invalid credentials")

    now = int(time.time())
    payload = {
        "user_id": username,
        "iat": now,
        "exp": now + TOKEN_TTL_SECONDS
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    return {"access_token": token, "token_type": "bearer", "expires_in": TOKEN_TTL_SECONDS}

@app.get("/validate")
def validate(authorization: Optional[str] = Header(None)):
    # convenience endpoint to validate token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return {"ok": True, "decoded": decoded}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="expired")
    except Exception as e:
        raise HTTPException(status_code=401, detail="invalid token")

