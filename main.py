"""
bot.py - Jarvis AI Discord Assistant
Main entry point. Initializes all subsystems and starts the bot.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

import discord
from discord.ext import commands

from config import Config
from database.db import Database
from memory.chroma_memory import MemorySystem
from ai.ollama_client import OllamaClient
from ai.tool_router import ToolRouter
from dashboard.backend.app import start_dashboard

# ─── Logging Setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/jarvis.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("jarvis.bot")


# ─── Bot Setup ────────────────────────────────────────────────────────────────
def create_bot() -> commands.Bot:
    """Create and configure the Discord bot with all required intents."""
    intents = discord.Intents.all()
    bot = commands.Bot(
        command_prefix=Config.PREFIX,
        intents=intents,
        help_command=None,
        description="Jarvis — Your local AI Discord assistant",
    )
    return bot


# ─── Cog Loader ───────────────────────────────────────────────────────────────
COGS = [
    "cogs.chat",
    "cogs.voice",
    "cogs.moderation",
    "cogs.image_gen",
    "cogs.web_search",
    "cogs.admin",
]


async def load_cogs(bot: commands.Bot) -> None:
    """Load all cog extensions."""
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            log.info(f"✅ Loaded cog: {cog}")
        except Exception as e:
            log.error(f"❌ Failed to load cog {cog}: {e}")


# ─── Main ─────────────────────────────────────────────────────────────────────
async def main():
    """Main async entry point. Boots all subsystems."""
    log.info("🚀 Starting Jarvis AI Discord Assistant...")

    # Ensure log directory exists
    Path("logs").mkdir(exist_ok=True)

    # Load configuration
    cfg = Config()
    cfg.validate()

    # Initialize database
    db = Database(cfg.DB_PATH)
    await db.initialize()
    log.info("✅ Database initialized")

    # Initialize memory system
    memory = MemorySystem(cfg.CHROMA_PATH)
    log.info("✅ Memory system initialized")

    # Initialize Ollama client
    ollama = OllamaClient(cfg.OLLAMA_HOST, cfg.OLLAMA_MODEL)
    await ollama.check_connection()
    log.info(f"✅ Ollama connected ({cfg.OLLAMA_MODEL})")

    # Initialize tool router
    tool_router = ToolRouter()

    # Create bot
    bot = create_bot()

    # Attach shared services to bot for cog access
    bot.db = db
    bot.memory = memory
    bot.ollama = ollama
    bot.tool_router = tool_router
    bot.cfg = cfg

    # ── Bot Events ────────────────────────────────────────────────────────────
    @bot.event
    async def on_ready():
        log.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
        log.info(f"   Serving {len(bot.guilds)} guild(s)")
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening, name="Hey Jarvis"
            )
        )
        log.info("🎙️ Wake word listening active")

    @bot.event
    async def on_guild_join(guild: discord.Guild):
        log.info(f"📥 Joined guild: {guild.name} ({guild.id})")
        await db.register_guild(guild.id, guild.name)

    @bot.event
    async def on_command_error(ctx: commands.Context, error):
        """Global error handler for commands."""
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⛔ You don't have permission to use that command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("⛔ I don't have permission to do that.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"⚠️ Missing argument: `{error.param.name}`")
        else:
            log.error(f"Unhandled command error: {error}", exc_info=error)
            await ctx.send("💥 Something went wrong. Check the logs.")

    # Load cogs
    await load_cogs(bot)

    # Graceful shutdown
    loop = asyncio.get_event_loop()

    def handle_shutdown(*_):
        log.info("🛑 Shutdown signal received. Stopping Jarvis...")
        asyncio.create_task(bot.close())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, handle_shutdown)

    # Start dashboard in background (non-blocking)
    if cfg.DASHBOARD_ENABLED:
        asyncio.create_task(start_dashboard(bot))
        log.info(f"🌐 Dashboard starting on http://0.0.0.0:{cfg.DASHBOARD_PORT}")

    # Start bot
    try:
        await bot.start(cfg.DISCORD_TOKEN)
    finally:
        await db.close()
        log.info("👋 Jarvis offline.")


if __name__ == "__main__":
    asyncio.run(main())
