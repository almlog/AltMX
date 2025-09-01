from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from altmx_agent import AltMXAgent
from typing import Optional, Dict, Any

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AltMX API",
    description="AI協働開発ライブデモンストレーションシステム - AltMX Backend API",
    version="1.0.0"
)

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite ports
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit methods including OPTIONS
    allow_headers=["*"],
)

# Initialize AltMX Agent
altmx = AltMXAgent()


class ChatRequest(BaseModel):
    message: str
    use_sapporo_dialect: bool = True


class ChatResponse(BaseModel):
    response: str
    dialect_applied: bool
    thinking_time_ms: int
    mood: str
    car_status: str


class CarAnimationResponse(BaseModel):
    lights_blinking: bool
    blink_color: str
    blink_speed: float
    car_emoji: str


@app.get("/")
async def root():
    return {"message": "AltMX API is running! なんまら元気っしょ！"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_altmx(request: ChatRequest):
    """AltMXエージェントとのチャット"""
    response_data = altmx.generate_response(
        user_message=request.message,
        use_dialect=request.use_sapporo_dialect
    )
    
    return ChatResponse(
        response=response_data["response"],
        dialect_applied=response_data["dialect_applied"],
        thinking_time_ms=response_data["thinking_time_ms"],
        mood=response_data["mood"],
        car_status=response_data["car_status"]
    )


@app.get("/api/car-animation", response_model=CarAnimationResponse)
async def get_car_animation():
    """スポーツカーアニメーション状態取得"""
    animation_data = altmx.get_car_animation_state()
    
    return CarAnimationResponse(
        lights_blinking=animation_data["lights_blinking"],
        blink_color=animation_data["blink_color"],
        blink_speed=animation_data["blink_speed"],
        car_emoji=animation_data["car_emoji"]
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )