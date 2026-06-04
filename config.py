import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    # Discord Configuration
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "YOUR_BOT_TOKEN_HERE")
    COMMAND_PREFIX: str = "!"
    
    # Ollama Configuration
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = "llama3"  # Supports qwen3, gemma3, etc.
    SYSTEM_PROMPT: str = (
        "You are Jarvis, a highly intelligent, friendly, witty, and helpful local AI assistant. "
        "You love technology, anime, and science. Keep voice channel answers concise and punchy. "
        "You have access to moderation tools and server management actions; perform them when requested."
    )
    
    # Memory & Database Configuration
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "database" / "chroma")
    SQLITE_URL: str = f"sqlite:///{BASE_DIR}/database/jarvis.db"
    
    # Voice Configuration
    WHISPER_MODEL_SIZE: str = "base"  # options: tiny, base, small, medium
    PIPER_EXECUTABLE: str = os.getenv("PIPER_EXECUTABLE", "piper")
    PIPER_MODEL_PATH: str = os.getenv("PIPER_MODEL_PATH", "models/en_US-joe-medium.onnx")
    WAKE_WORD_DURATION: float = 30.0  # Seconds to stay active after wake word
    
    # Image Generation Configuration
    STABLE_DIFFUSION_URL: str = os.getenv("STABLE_DIFFUSION_URL", "http://127.0.0.1:7860")
    IMAGE_BACKEND: str = "AUTOMATIC1111"  # AUTOMATIC1111 or COMFYUI
    
    # Search Plugin
    SEARXNG_URL: str = os.getenv("SEARXNG_URL", "")

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure directories exist
os.makedirs(os.path.dirname(settings.SQLITE_URL.replace("sqlite:///", "")), exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs(BASE_DIR / "logs", exist_ok=True)
