import os
import asyncio
import discord
import requests
import speech_recognition as sr
from dotenv import load_dotenv
from gtts import gTTS

# ======================================
# LOAD ENV
# ======================================

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ======================================
# DISCORD SETUP
# ======================================

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)

# ======================================
# AI FUNCTION
# ======================================

def ask_ai(prompt):

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://discord.com",
        "X-Title": "Jarvis Bot"
    }

    payload = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Jarvis, an advanced AI assistant."
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
            return "AI Error"

        return data["choices"][0]["message"]["content"]

    except Exception as e:

        print(e)
        return "Something went wrong"

# ======================================
# TEXT TO SPEECH
# ======================================

async def speak(vc, text):

    try:

        if vc.is_playing():
            vc.stop()

        tts = gTTS(text=text, lang="en")

        filename = "voice.mp3"

        tts.save(filename)

        audio_source = discord.FFmpegPCMAudio(
            executable="ffmpeg",
            source=filename
        )

        vc.play(audio_source)

        while vc.is_playing():
            await asyncio.sleep(1)

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:

        print(f"VOICE ERROR: {e}")

# ======================================
# SPEECH RECOGNITION
# ======================================

recognizer = sr.Recognizer()


def listen_from_mic():

    try:

        with sr.Microphone() as source:

            print("Listening...")

            recognizer.adjust_for_ambient_noise(source)

            audio = recognizer.listen(source)

            text = recognizer.recognize_google(audio)

            print(f"You said: {text}")

            return text

    except Exception as e:

        print(f"Speech Error: {e}")

        return None

# ======================================
# READY EVENT
# ======================================

@client.event
async def on_ready():

    print(f"Logged in as {client.user}")

# ======================================
# MESSAGE EVENT
# ======================================

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    try:

        # ==================================
        # SUMMON
        # ==================================

        if message.content == "!summon":

            if not message.author.voice:

                await message.channel.send(
                    "Join a VC first."
                )

                return

            channel = message.author.voice.channel

            if message.guild.voice_client:

                await message.guild.voice_client.move_to(channel)

            else:

                await channel.connect()

            await message.channel.send(
                f"Joined {channel.name}"
            )

        # ==================================
        # DISMISS
        # ==================================

        elif message.content == "!dismiss":

            if message.guild.voice_client:

                await message.guild.voice_client.disconnect()

                await message.channel.send(
                    "Disconnected"
                )

        # ==================================
        # TEXT AI
        # ==================================

        elif message.content.startswith("!ai"):

            prompt = message.content[3:].strip()

            if not prompt:

                await message.channel.send(
                    "Ask something"
                )

                return

            async with message.channel.typing():

                ai_response = ask_ai(prompt)

                if len(ai_response) > 2000:
                    ai_response = ai_response[:1990]

                await message.channel.send(ai_response)

        # ==================================
        # SPEAK
        # ==================================

        elif message.content.startswith("!speak"):

            text = message.content[6:].strip()

            vc = message.guild.voice_client

            if vc is None:

                await message.channel.send(
                    "Bot is not in VC"
                )

                return

            await speak(vc, text)

        # ==================================
        # JARVIS
        # ==================================

        elif message.content.startswith("!jarvis"):

            prompt = message.content[7:].strip()

            vc = message.guild.voice_client

            if vc is None:

                await message.channel.send(
                    "Use !summon first"
                )

                return

            ai_response = ask_ai(prompt)

            await message.channel.send(ai_response)

            await speak(vc, ai_response)

        # ==================================
        # MICROPHONE LISTENING
        # ==================================

        elif message.content == "!listen":

            vc = message.guild.voice_client

            if vc is None:

                await message.channel.send(
                    "Use !summon first"
                )

                return

            await message.channel.send(
                "Listening from microphone..."
            )

            heard_text = listen_from_mic()

            if heard_text is None:

                await message.channel.send(
                    "Could not understand voice"
                )

                return

            await message.channel.send(
                f"You said: {heard_text}"
            )

            ai_response = ask_ai(heard_text)

            await message.channel.send(ai_response)

            await speak(vc, ai_response)

    except Exception as e:

        print(f"BOT ERROR: {e}")

        await message.channel.send(
            "An error occurred"
        )

# ======================================
# RUN BOT
# ======================================

client.run(DISCORD_BOT_TOKEN)