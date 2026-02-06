import asyncio
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime
import json
import os

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class RawData(Base):
    __tablename__ = "raw_data"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow) # TODO - this is deprecated, update

# Redis MQ connection
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global redis_client
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = await redis.from_url(redis_url, decode_responses=True)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start background polling task
    task = asyncio.create_task(poll_api_periodically())

    yield

    # Shutdown
    task.cancel()
    await redis_client.close()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
API_ENDPOINT = os.getenv("API_ENDPOINT") # TODO - make env var for Spotify API
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))
REDIS_QUEUE = "data_ingestion_queue"

async def fetch_api_data():
    """Fetch data from external API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(API_ENDPOINT, timeout=30.0)
        response.raise_for_status()
        return response.json()

async def save_to_database(data: dict):
    """Save raw data to database"""
    async with AsyncSessionLocal() as session:
        raw_data = RawData(
            source=API_ENDPOINT,
            data=data
        )
        session.add(raw_data)
        await session.commit()
        await session.refresh(raw_data)
        return raw_data.id

async def push_to_queue(message: dict):
    """Push message to Redis queue"""
    await redis_client.lpush(REDIS_QUEUE, json.dumps(message))

async def check_and_process_data():
    """Main logic: check API, save to DB, push to queue"""
    try:
        # 1. Fetch data from API
        api_data = await fetch_api_data()

        # 2.Save to database
        record_id = await save_to_database(api_data)

        # 3. Push message to Redis queue
        message = {
            "record_id": record_id,
            "source": API_ENDPOINT,
            "timestamp": datetime.utcnow().isoformat(),
            "data_preview": str(api_data[:100]) # optional
        }
        await push_to_queue(message)

        print(f"Processed data: record_id={record_id}")
        return {"status": "success", "record_id": record_id}
    except Exception as e:
        print(f"Error processing data: {e}")
        return {"status": "error", "message": str(e)}

async def poll_api_periodically():
    """Background task to poll api periodically"""
    while True:
        try:
            await check_and_process_data()
            await asyncio.sleep(POLL_INTERVAL)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Polling error: {e}")
            await asyncio.sleep(POLL_INTERVAL)

# Routes
@app.get("/")
def read_root():
    return {"service": "data-ingestion", "status": "running"}

@app.post("/trigger-ingestion")
async def trigger_ingestion():
    """Manually trigger data ingestion"""
    result = await check_and_process_data()
    return result

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        await redis_client.ping()
        redis_status = "connected"
    except:
        redis_status = "disconnected"

    return {
        "status": "healthy",
        "redis_status": redis_status,
        "timestamp": datetime.utcnow().isoformat()
    }