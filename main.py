# ==========================================================
# STABLE DISCORD AI + VC BOT
# TEXT CHAT + VOICE CHANNEL SPEAKING
# ==========================================================

# ==========================================================
# INSTALL
# ==========================================================
#
# pip install -U discord.py[voice]
# pip install requests python-dotenv gtts PyNaCl
#
# ==========================================================
# requirements.txt
# ==========================================================
#
# discord.py[voice]
# requests
# python-dotenv
# gtts
# PyNaCl
#
# ==========================================================
# Procfile
# ==========================================================
#
# worker: python bot.py
#
# ==========================================================
# ENV VARIABLES
# ==========================================================
#
# DISCORD_BOT_TOKEN=YOUR_TOKEN
# OPENROUTER_API_KEY=YOUR_KEY
#
# ==========================================================

import os
import discord
import requests
import asyncio
from dotenv import load_dotenv
from gtts import gTTS

# ==========================================================
# LOAD ENV
# ==========================================================

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ==========================================================
# DISCORD SETUP
# ==========================================================

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)

# ==========================================================
# AI FUNCTION
# ==========================================================

def ask_ai(prompt):

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://discord.com",
        "X-Title": "Discord Jarvis Bot"
    }

    payload = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Jarvis, a smart "
                    "Discord voice assistant."
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
            return "AI API Error."

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print(e)
        return "Something went wrong."

# ==========================================================
# SAFE AUDIO PLAY FUNCTION
# ==========================================================

async def play_tts(vc, text):

    try:

        if vc.is_playing():
            vc.stop()

        tts = gTTS(text=text, lang="en")

        filename = "voice.mp3"

        tts.save(filename)

        source = discord.FFmpegPCMAudio(
            executable="ffmpeg",
            source=filename
        )

        vc.play(source)

        while vc.is_playing():
            await asyncio.sleep(1)

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:

        print(f"TTS ERROR: {e}")
# ==========================================================
# READY EVENT
# ==========================================================

@client.event
async def on_ready():

    print(f"Logged in as {client.user}")

# ==========================================================
# MESSAGE EVENT
# ==========================================================

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    try:

        # ==================================================
        # SUMMON BOT
        # ==================================================

        if message.content == "!summon":

            if not message.author.voice:

                await message.channel.send(
                    "Join a VC first."
                )

                return

            channel = message.author.voice.channel

            # Move if already connected
            if message.guild.voice_client:

                await message.guild.voice_client.move_to(
                    channel
                )

            else:

                await channel.connect()

            await message.channel.send(
                f"Joined {channel.name}"
            )

        # ==================================================
        # DISMISS BOT
        # ==================================================

        elif message.content == "!dismiss":

            if message.guild.voice_client:

                await message.guild.voice_client.disconnect()

                await message.channel.send(
                    "Disconnected."
                )

            else:

                await message.channel.send(
                    "I am not in VC."
                )

        # ==================================================
        # TEXT AI CHAT
        # ==================================================

        elif message.content.startswith("!ai"):

            prompt = message.content[3:].strip()

            if not prompt:

                await message.channel.send(
                    "Please ask something."
                )

                return

            async with message.channel.typing():

                ai_response = ask_ai(prompt)

                if len(ai_response) > 2000:
                    ai_response = ai_response[:1990]

                await message.channel.send(
                    ai_response
                )

        # ==================================================
        # SPEAK TEXT
        # ==================================================

        elif message.content.startswith("!speak"):

            text = message.content[6:].strip()

            if not text:

                await message.channel.send(
                    "Provide text."
                )

                return

            vc = message.guild.voice_client

            if vc is None:

                await message.channel.send(
                    "Bot is not in VC."
                )

                return

            await message.channel.send(
                "Speaking..."
            )

            await play_tts(vc, text)

        # ==================================================
        # JARVIS MODE
        # ==================================================

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
                    "Use !summon first."
                )

                return

            async with message.channel.typing():

                ai_response = ask_ai(prompt)

                if len(ai_response) > 2000:
                    ai_response = ai_response[:1990]

                # Send text
                await message.channel.send(
                    ai_response
                )

                # Speak
                await play_tts(
                    vc,
                    ai_response
                )

    except Exception as e:

        print(f"BOT ERROR: {e}")

        await message.channel.send(
            "An error occurred."
        )

# ==========================================================
# RUN BOT
# ==========================================================

client.run(DISCORD_BOT_TOKEN)