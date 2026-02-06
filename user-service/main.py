from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, JSON, DateTime
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Database Setup
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class RawData(Base):
    __tablename__ = "user_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables verified/created successfully")

    yield

    # Shutdown: Clean up resources if needed
    await engine.dispose()


# Service Setup with lifespan
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SPOTIFY_CLIENT_ID = os.getenv("spotify_app_client_id")
SPOTIFY_CLIENT_SECRET = os.getenv("spotify_app_client_secret")
REDIRECT_URI = "http://127.0.0.1:8001/auth/spotify/callback"

@app.get("/auth/spotify/login")
async def spotify_login():
    # Redirect to Spotify
    print(REDIRECT_URI)

    spotify_auth_url = (
        f"https://accounts.spotify.com/authorize?"
        f"client_id={SPOTIFY_CLIENT_ID}&"
        f"response_type=code&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope=user-read-email%20user-read-private"
    )

    print(spotify_auth_url)

    return RedirectResponse(spotify_auth_url)

async def save_to_database(
        user_id: str,
        data: dict
):
    """Save raw data to database"""
    async with AsyncSessionLocal() as session:
        raw_data = RawData(
            user_id=user_id,
            data=data
        )
        session.add(raw_data)
        await session.commit()
        await session.refresh(raw_data)
        return raw_data.id


@app.get("/auth/spotify/callback")
async def spotify_callback(code: str):
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": SPOTIFY_CLIENT_ID,
                "client_secret": SPOTIFY_CLIENT_SECRET,
            }
        )

    token_data = response.json()
    print(token_data)
    access_token = token_data.get("access_token")

    # Get Spotify user profile
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "https://api.spotify.com/v1/me",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

    user_profile = user_response.json()
    spotify_user_id = user_profile.get("id")

    # Store in Database as a json value for user
    record_id = await save_to_database(str(spotify_user_id), token_data)

    print("Record id: {}".format(record_id))

    # Store token in session/database, then redirect back to frontend
    return RedirectResponse("http://localhost:8080/index.html?success=true")