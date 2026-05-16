import os
import re
import asyncio
import requests
import urllib.parse
import discord

from gtts import gTTS
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# =========================
# DISCORD SETUP
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)

# =========================
# AI CHAT FUNCTION
# =========================

def ask_ai(prompt):

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://discord.com",
        "X-Title": "Discord AI Assistant"
    }

    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a smart, friendly, funny, and helpful Discord AI assistant. "
                    "Keep replies conversational and not too long because they will be spoken in voice chat."
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
# FREE IMAGE GENERATION
# =========================

def generate_image(prompt):

    try:

        encoded_prompt = urllib.parse.quote(prompt)

        image_url = (
            f"https://image.pollinations.ai/prompt/"
            f"{encoded_prompt}"
            f"?width=1024"
            f"&height=1024"
            f"&model=flux"
        )

        return image_url

    except Exception as e:
        return f"Error: {e}"

# =========================
# TTS FUNCTION
# =========================

async def speak_in_vc(voice_client, text):

    try:

        # Clean markdown symbols
        clean_text = re.sub(r'[*_`~]', '', text)

        # Limit very long speech
        clean_text = clean_text[:500]

        filename = f"temp_{voice_client.guild.id}.mp3"

        # Generate TTS
        tts = gTTS(text=clean_text, lang='en')
        tts.save(filename)

        # Stop old audio if playing
        if voice_client.is_playing():
            voice_client.stop()

        # FFmpeg audio source
        source = discord.FFmpegPCMAudio(
            executable="ffmpeg",
            source=filename
        )

        voice_client.play(source)

        # Wait until audio finishes
        while voice_client.is_playing():
            await asyncio.sleep(1)

        # Small delay
        await asyncio.sleep(1)

        # Cleanup
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass

    except Exception as e:
        print(f"TTS Error: {e}")

# =========================
# READY EVENT
# =========================

@client.event
async def on_ready():

    print("=" * 50)
    print(f"✅ Logged in as: {client.user}")
    print("=" * 50)

# =========================
# MESSAGE EVENT
# =========================

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    # ====================================
    # !leave COMMAND
    # ====================================

    if message.content.startswith("!leave"):

        voice_client = discord.utils.get(
            client.voice_clients,
            guild=message.guild
        )

        if voice_client and voice_client.is_connected():

            await voice_client.disconnect()

            await message.channel.send(
                "👋 Left the voice channel."
            )

        else:

            await message.channel.send(
                "❌ I'm not in a voice channel."
            )

        return

    # ====================================
    # !join COMMAND
    # ====================================

    if message.content.startswith("!join"):

        if not message.author.voice:

            await message.channel.send(
                "❌ Join a voice channel first."
            )

            return

        channel = message.author.voice.channel

        voice_client = discord.utils.get(
            client.voice_clients,
            guild=message.guild
        )

        if voice_client:

            await voice_client.move_to(channel)

        else:

            await channel.connect()

        await message.channel.send(
            f"✅ Joined **{channel}**"
        )

        return

    # ====================================
    # !image COMMAND
    # ====================================

    if message.content.startswith("!image"):

        prompt = message.content[6:].strip()

        if not prompt:

            await message.channel.send(
                "❌ Please provide an image prompt."
            )

            return

        async with message.channel.typing():

            image_url = generate_image(prompt)

            embed = discord.Embed(
                title="🎨 AI Generated Image",
                description=f"**Prompt:** {prompt}",
                color=0x00ffcc
            )

            embed.set_image(url=image_url)

            embed.set_footer(
                text="Generated using Pollinations AI"
            )

            await message.channel.send(embed=embed)

        return

    # ====================================
    # !ai COMMAND
    # ====================================

    if message.content.startswith("!ai"):

        prompt = message.content[3:].strip()

        if not prompt:

            await message.channel.send(
                "❌ Please enter a prompt."
            )

            return

        async with message.channel.typing():

            # Get AI response
            ai_response = ask_ai(prompt)

            # Limit Discord text size
            if len(ai_response) > 1900:
                ai_response = ai_response[:1900] + "..."

            # Send response
            await message.channel.send(ai_response)

            # =========================
            # AUTO JOIN VC
            # =========================

            voice_client = discord.utils.get(
                client.voice_clients,
                guild=message.guild
            )

            if message.author.voice:

                channel = message.author.voice.channel

                # Connect if not connected
                if not voice_client:

                    voice_client = await channel.connect()

                # Move if different VC
                elif voice_client.channel != channel:

                    await voice_client.move_to(channel)

            # Speak response
            if voice_client and voice_client.is_connected():

                await speak_in_vc(
                    voice_client,
                    ai_response
                )

        return

    # ====================================
    # BOT MENTION REPLY
    # ====================================

    if client.user in message.mentions:

        prompt = message.content.replace(
            f"<@{client.user.id}>",
            ""
        ).strip()

        if not prompt:
            prompt = "Hello"

        async with message.channel.typing():

            ai_response = ask_ai(prompt)

            if len(ai_response) > 1900:
                ai_response = ai_response[:1900] + "..."

            await message.channel.send(ai_response)

            # Voice logic
            voice_client = discord.utils.get(
                client.voice_clients,
                guild=message.guild
            )

            if message.author.voice:

                channel = message.author.voice.channel

                if not voice_client:

                    voice_client = await channel.connect()

                elif voice_client.channel != channel:

                    await voice_client.move_to(channel)

            if voice_client and voice_client.is_connected():

                await speak_in_vc(
                    voice_client,
                    ai_response
                )

# =========================
# START BOT
# =========================

client.run(DISCORD_BOT_TOKEN)