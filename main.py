# =====================================================
# DISCORD AI + VOICE BOT
# Text Chat + Voice Channel Speaking
# =====================================================

# INSTALL:
#
# pip install -U discord.py[voice]
# pip install requests python-dotenv gtts PyNaCl
#
# IMPORTANT:
# Install FFmpeg on your system
#
# Windows:
# https://ffmpeg.org/download.html
#
# Railway/Replit:
# Add ffmpeg package
#
# =====================================================
# FILES:
#
# bot.py
# requirements.txt
# Procfile
#
# =====================================================
# requirements.txt
#
# discord.py[voice]
# requests
# python-dotenv
# gtts
# PyNaCl
#
# =====================================================
# Procfile
#
# worker: python bot.py
#
# =====================================================
# ENV VARIABLES
#
# DISCORD_BOT_TOKEN=your_token
# OPENROUTER_API_KEY=your_api_key
#
# =====================================================

import os
import discord
import requests
from dotenv import load_dotenv
from gtts import gTTS

# =====================================================
# LOAD ENV
# =====================================================

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# =====================================================
# DISCORD SETUP
# =====================================================

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)

# =====================================================
# AI FUNCTION
# =====================================================

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
                    "You are Jarvis-like AI assistant "
                    "inside Discord voice chat."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
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
            return f"API Error: {data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {e}"

# =====================================================
# BOT READY
# =====================================================

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

# =====================================================
# MESSAGE HANDLER
# =====================================================

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    # =================================================
    # JOIN VOICE CHANNEL
    # =================================================

    if message.content == "!join":

        if message.author.voice:

            channel = message.author.voice.channel

            await channel.connect()

            await message.channel.send(
                "Joined voice channel."
            )

        else:

            await message.channel.send(
                "Join a voice channel first."
            )

    # =================================================
    # LEAVE VOICE CHANNEL
    # =================================================

    elif message.content == "!leave":

        if message.guild.voice_client:

            await message.guild.voice_client.disconnect()

            await message.channel.send(
                "Disconnected from VC."
            )

    # =================================================
    # TEXT AI CHAT
    # =================================================

    elif message.content.startswith("!ai"):

        user_prompt = message.content[3:].strip()

        if not user_prompt:

            await message.channel.send(
                "Please enter a prompt."
            )

            return

        async with message.channel.typing():

            ai_response = ask_ai(user_prompt)

            if len(ai_response) > 2000:
                ai_response = ai_response[:1990] + "..."

            await message.channel.send(ai_response)

    # =================================================
    # AI SPEAK COMMAND
    # Example:
    # !speak hello humans
    # =================================================

    elif message.content.startswith("!speak"):

        text = message.content[6:].strip()

        if not text:

            await message.channel.send(
                "Please provide text."
            )

            return

        vc = message.guild.voice_client

        if vc is None:

            await message.channel.send(
                "Bot is not in VC."
            )

            return

        # Create voice audio
        tts = gTTS(text=text, lang="en")

        tts.save("voice.mp3")

        # Play audio
        vc.play(
            discord.FFmpegPCMAudio("voice.mp3")
        )

        await message.channel.send(
            "Speaking..."
        )

    # =================================================
    # ASK AI + SPEAK RESPONSE
    # Example:
    # !jarvis what is black hole
    # =================================================

    elif message.content.startswith("!jarvis"):

        prompt = message.content[7:].strip()

        if not prompt:

            await message.channel.send(
                "Ask something."
            )

            return

        vc = message.guild.voice_client

        if vc is None:

            await message.channel.send(
                "Bot is not connected to VC."
            )

            return

        async with message.channel.typing():

            ai_response = ask_ai(prompt)

            # Send text response
            if len(ai_response) > 2000:
                ai_response = ai_response[:1990] + "..."

            await message.channel.send(ai_response)

            # Convert AI response to speech
            tts = gTTS(
                text=ai_response,
                lang="en"
            )

            tts.save("jarvis.mp3")

            # Play in VC
            vc.play(
                discord.FFmpegPCMAudio("jarvis.mp3")
            )

# =====================================================
# RUN BOT
# =====================================================

client.run(DISCORD_BOT_TOKEN)