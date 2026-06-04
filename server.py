from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psutil
from config import settings

app = FastAPI(title="Jarvis Telemetry Center", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/telemetry")
async def get_telemetry():
    """
    Exposes raw infrastructure hardware consumption metrics.
    """
    return {
        "status": "ONLINE",
        "cpu_usage_pct": psutil.cpu_percent(interval=None),
        "memory_usage_pct": psutil.virtual_memory().percent,
        "active_model": settings.OLLAMA_MODEL,
        "voice_active": True
    }
