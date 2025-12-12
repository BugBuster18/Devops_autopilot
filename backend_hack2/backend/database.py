import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
import redis.asyncio as redis
from cryptography.fernet import Fernet

# MongoDB Config
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://your_user:your_password@cluster.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = "autopilot_db"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# --- Pydantic Models for MongoDB ---
# These represent the structure of your documents

class UserSchema(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    github_token: str
    github_username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

# Helper to get the users collection
def get_user_collection():
    return db["users"]

# --- Redis Config ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def cache_get(key: str):
    try:
        val = await redis_client.get(key)
        return json.loads(val) if val else None
    except Exception as e:
        print(f"Redis get error: {e}")
        return None

async def cache_set(key: str, value: dict, ttl: int = 3600):
    try:
        await redis_client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        print(f"Redis set error: {e}")

async def cache_delete(key: str):
    try:
        await redis_client.delete(key)
    except Exception as e:
        print(f"Redis delete error: {e}")

async def create_indexes():
    try:
        await db.users.create_index("email", unique=True)
        await db.runs.create_index("id", unique=True)
        await db.runs.create_index("user_email")
        print("✅ MongoDB Indexes Created")
    except Exception as e:
        print(f"❌ MongoDB Index Error: {e}")

async def ping_db():
    try:
        await client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas!")
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {e}")