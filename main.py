from fastapi import FastAPI, HTTPException
import bcrypt
from pymongo import MongoClient

app = FastAPI()

# ---- MongoDB Connection ----
MONGO_URL = "mongodb://mongo:27017"
client = MongoClient(MONGO_URL)
db = client["authdb"]
users = db["users"]

@app.post("/signup")
def signup(payload: dict):
    username = payload.get("username")
    password = payload.get("password")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing username or password")

    # Check if user exists
    if users.find_one({"username": username}):
        raise HTTPException(status_code=409, detail="User already exists")

    # Hash password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Store user
    users.insert_one({
        "username": username,
        "password": hashed
    })

    return {"status": "success", "message": "User created"}

