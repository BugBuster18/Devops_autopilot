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

async def ping_db():
    try:
        await client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas!")
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {e}")