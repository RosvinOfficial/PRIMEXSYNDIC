import discord
from discord.ext import commands
import logging
from config import settings
from ai.ollama_client import OllamaEngine
from memory.chroma_memory import JarvisMemory
from tools.server_tools import ToolExecutor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("logs/jarvis.log"), logging.StreamHandler()]
)
logger = logging.getLogger("JarvisBot")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

class JarvisBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=settings.COMMAND_PREFIX, intents=intents)
        self.ai = OllamaEngine()
        self.memory = JarvisMemory()
        self.tool_executor = ToolExecutor(self)

    async def setup_hook(self):
        logger.info("Initializing background engines...")
        # Placeholder for loading cogs dynamically if needed
        
    async def on_ready(self):
        logger.info(f"Jarvis is online and authenticated as {self.user}")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="commands"))

bot = JarvisBot()

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # Trigger explicit commands first
    if message.content.startswith(settings.COMMAND_PREFIX):
        await bot.process_commands(message)
        return

    # Natural conversation evaluation
    ctx = await bot.get_context(message)
    is_mentioned = bot.user.mentioned_in(message)
    
    if is_mentioned or "jarvis" in message.content.lower():
        async with message.channel.typing():
            # Retrieve memory
            context_memories = bot.memory.retrieve_memories(user_id=str(message.author.id), query=message.content)
            
            # Formulate response via Ollama
            response_text, tool_calls = await bot.ai.generate_response(
                user_input=message.content,
                user_name=message.author.name,
                context=context_memories
            )
            
            # Handle Function Calling if tools are identified
            if tool_calls:
                for tool in tool_calls:
                    tool_result = await bot.tool_executor.execute(tool, ctx)
                    response_text += f"\n*{tool_result}*"

            # Save the new interaction to ChromaDB
            bot.memory.store_memory(user_id=str(message.author.id), user_input=message.content, response=response_text)
            
            await message.reply(response_text)

if __name__ == "__main__":
    bot.run(settings.DISCORD_TOKEN)
