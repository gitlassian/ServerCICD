import json
import os
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict
import redis.asyncio as aioredis
from redis_manager import get_redis

app = FastAPI()

# Data storage path
DATA_FILE = "messages.json"

# In-memory backup (dict)
messages_db: Dict[int, Dict] = {}

class Message(BaseModel):
    user: str
    content: str

def load_data():
    global messages_db
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    messages_db = {i: msg for i, msg in enumerate(data)}
                else:
                    messages_db = {int(k): v for k, v in data.items()}
        except (json.JSONDecodeError, ValueError):
            messages_db = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(messages_db, f, indent=4)

@app.on_event("startup")
async def startup_event():
    load_data()

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.post("/api/messages")
async def create_message(msg: Message, db: aioredis.Redis = Depends(get_redis)):
    new_id = max(messages_db.keys(), default=0) + 1
    message_data = {
        "user": msg.user,
        "content": msg.content,
        "id": new_id
    }
    
    # Store in local dict/JSON
    messages_db[new_id] = message_data
    save_data()
    
    # Store in Redis (using a Hash for the message and a List for tracking IDs)
    try:
        await db.hset(f"message:{new_id}", mapping=message_data)
        await db.rpush("message_ids", new_id)
    except Exception as e:
        print(f"Redis Error: {e}") # Fallback to JSON-only if Redis fails
        
    return message_data

@app.get("/api/messages", response_model=List[Dict])
async def get_messages(db: aioredis.Redis = Depends(get_redis)):
    # Try to get from Redis first
    try:
        message_ids = await db.lrange("message_ids", 0, -1)
        if message_ids:
            messages = []
            for m_id in message_ids:
                msg = await db.hgetall(f"message:{m_id}")
                if msg:
                    messages.append(msg)
            return messages
    except Exception as e:
        print(f"Redis Error: {e}")

    # Fallback to local dict
    return list(messages_db.values())

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
