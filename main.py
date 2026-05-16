import os
import discord
import requests
import asyncio
import re
from gtts import gTTS
from dotenv import load_dotenv

# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# =========================
# DISCORD SETUP
# =========================

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# =========================
# AI FUNCTION
# =========================

def ask_ai(prompt):

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://discord.com",
        "X-Title": "Discord AI Bot"
    }

    payload = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a smart and friendly Discord AI assistant. Keep responses conversational and relatively concise since they will be spoken out loud."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    try:

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        data = response.json()

        print(data)

        if "choices" not in data:
            return f"API Error:\n{data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {e}"

# =========================
# VOICE TTS FUNCTION
# =========================

async def speak_in_vc(voice_client, text):
    """Converts AI text to speech and plays it in the connected VC."""
    
    # Optional: Clean up markdown (like **bold** or *italics*) so the TTS doesn't read asterisks out loud.
    clean_text = re.sub(r'[*_`~]', '', text)

    # 1. Generate TTS audio
    tts = gTTS(text=clean_text, lang='en')
    filename = "temp_ai_response.mp3"
    tts.save(filename)

    # 2. Play audio
    try:
        source = discord.FFmpegPCMAudio(executable="ffmpeg", source=filename)
        
        if not voice_client.is_playing():
            voice_client.play(source)

            # Wait until audio finishes playing before allowing cleanup
            while voice_client.is_playing():
                await asyncio.sleep(1)

            # 3. Cleanup temp file
            if os.path.exists(filename):
                os.remove(filename)
    except Exception as e:
        print(f"Audio Error: {e}")

# =========================
# BOT READY
# =========================

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

# =========================
# MESSAGE EVENT
# =========================

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    # -------------------------
    # VOICE COMMANDS
    # -------------------------
    
    # !join command
    if message.content.startswith("!join"):
        if message.author.voice:
            channel = message.author.voice.channel
            # Check if bot is already in a VC in this server
            voice_client = discord.utils.get(client.voice_clients, guild=message.guild)
            if not voice_client:
                await channel.connect()
                await message.channel.send(f"Joined {channel.name}")
            else:
                await voice_client.move_to(channel)
        else:
            await message.channel.send("You need to be in a voice channel first!")
        return

    # !leave command
    if message.content.startswith("!leave"):
        voice_client = discord.utils.get(client.voice_clients, guild=message.guild)
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await message.channel.send("Left the voice channel.")
        else:
            await message.channel.send("I'm not in a voice channel.")
        return

    # -------------------------
    # AI COMMANDS
    # -------------------------

    # PREFIX COMMAND (!ai)
    if message.content.startswith("!ai"):

        user_prompt = message.content[3:].strip()

        if not user_prompt:
            await message.channel.send("Please enter a prompt.")
            return

        async with message.channel.typing():
            
            # Fetch AI Response
            ai_response = ask_ai(user_prompt)

            if len(ai_response) > 2000:
                ai_response = ai_response[:1990] + "..."

            # Send text to channel
            await message.channel.send(ai_response)

            # Speak if connected to a VC
            voice_client = discord.utils.get(client.voice_clients, guild=message.guild)
            if voice_client and voice_client.is_connected():
                await speak_in_vc(voice_client, ai_response)

    # MENTION REPLY
    elif client.user in message.mentions:

        user_prompt = message.content.replace(f"<@{client.user.id}>", "").strip()

        if not user_prompt:
            user_prompt = "Hello"

        async with message.channel.typing():

            # Fetch AI Response
            ai_response = ask_ai(user_prompt)

            if len(ai_response) > 2000:
                ai_response = ai_response[:1990] + "..."

            # Send text to channel
            await message.channel.send(ai_response)

            # Speak if connected to a VC
            voice_client = discord.utils.get(client.voice_clients, guild=message.guild)
            if voice_client and voice_client.is_connected():
                await speak_in_vc(voice_client, ai_response)

# =========================
# RUN BOT
# =========================

client.run(DISCORD_BOT_TOKEN)
