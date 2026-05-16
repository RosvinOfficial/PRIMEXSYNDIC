import os
import re
import time
import asyncio
import requests
import discord

from gtts import gTTS
from dotenv import load_dotenv

# ==========================================
# LOAD ENV
# ==========================================

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ==========================================
# DISCORD SETUP
# ==========================================

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)

# ==========================================
# AI CHAT FUNCTION
# ==========================================

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
                    "You are a smart, funny, friendly AI Discord assistant. "
                    "Keep responses conversational and not too long because "
                    "they will also be spoken in voice chat."
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

# ==========================================
# Z-IMAGE-TURBO IMAGE GENERATOR
# ==========================================

def generate_image(prompt):

    try:

        api_url = (
            "https://mrfakename-z-image-turbo.hf.space/"
            "gradio_api/call/infer"
        )

        payload = {
            "data": [
                prompt,     # Prompt
                "",         # Negative Prompt
                1024,       # Width
                1024,       # Height
                8,          # Steps
                0.0         # CFG Scale
            ]
        }

        # Start generation
        response = requests.post(
            api_url,
            json=payload,
            timeout=60
        )

        data = response.json()

        print(data)

        event_id = data["event_id"]

        result_url = (
            f"https://mrfakename-z-image-turbo.hf.space/"
            f"gradio_api/call/infer/{event_id}"
        )

        # Poll until completed
        while True:

            result = requests.get(
                result_url,
                timeout=60
            )

            if result.status_code == 200:

                text = result.text

                print(text)

                # Extract image path
                match = re.search(
                    r'"url":"(.*?)"',
                    text
                )

                if match:

                    image_path = (
                        match.group(1)
                        .replace("\\/", "/")
                    )

                    full_url = (
                        "https://mrfakename-z-image-turbo.hf.space"
                        + image_path
                    )

                    return full_url

            time.sleep(1)

    except Exception as e:

        print(f"Image Error: {e}")

        return None

# ==========================================
# TTS FUNCTION
# ==========================================

async def speak_in_vc(voice_client, text):

    try:

        # Remove markdown symbols
        clean_text = re.sub(
            r'[*_`~]',
            '',
            text
        )

        # Limit speech length
        clean_text = clean_text[:500]

        filename = (
            f"temp_{voice_client.guild.id}.mp3"
        )

        # Generate TTS
        tts = gTTS(
            text=clean_text,
            lang='en'
        )

        tts.save(filename)

        # Stop current audio
        if voice_client.is_playing():
            voice_client.stop()

        # Play audio
        source = discord.FFmpegPCMAudio(
            executable="ffmpeg",
            source=filename
        )

        voice_client.play(source)

        while voice_client.is_playing():
            await asyncio.sleep(1)

        await asyncio.sleep(1)

        # Cleanup
        try:

            if os.path.exists(filename):
                os.remove(filename)

        except:
            pass

    except Exception as e:

        print(f"TTS Error: {e}")

# ==========================================
# READY EVENT
# ==========================================

@client.event
async def on_ready():

    print("=" * 50)
    print(f"✅ Logged in as {client.user}")
    print("=" * 50)

# ==========================================
# MESSAGE EVENT
# ==========================================

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    # ======================================
    # !join
    # ======================================

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
            f"✅ Joined {channel}"
        )

        return

    # ======================================
    # !leave
    # ======================================

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
                "❌ I'm not in a VC."
            )

        return

    # ======================================
    # !image
    # ======================================

    if message.content.startswith("!image"):

        prompt = message.content[6:].strip()

        if not prompt:

            await message.channel.send(
                "❌ Please enter an image prompt."
            )

            return

        loading = await message.channel.send(
            "🎨 Generating image..."
        )

        try:

            image_url = generate_image(prompt)

            if not image_url:

                await loading.edit(
                    content="❌ Failed to generate image."
                )

                return

            embed = discord.Embed(
                title="⚡ Z-Image-Turbo",
                description=f"**Prompt:** {prompt}",
                color=0x00ffcc
            )

            embed.set_image(url=image_url)

            embed.set_footer(
                text="Powered by HuggingFace"
            )

            await loading.delete()

            await message.channel.send(
                embed=embed
            )

        except Exception as e:

            await loading.edit(
                content=f"❌ Error: {e}"
            )

        return

    # ======================================
    # !ai
    # ======================================

    if message.content.startswith("!ai"):

        prompt = message.content[3:].strip()

        if not prompt:

            await message.channel.send(
                "❌ Please enter a prompt."
            )

            return

        async with message.channel.typing():

            ai_response = ask_ai(prompt)

            # Limit Discord size
            if len(ai_response) > 1900:
                ai_response = ai_response[:1900] + "..."

            await message.channel.send(
                ai_response
            )

            # Voice auto join
            voice_client = discord.utils.get(
                client.voice_clients,
                guild=message.guild
            )

            if message.author.voice:

                channel = (
                    message.author.voice.channel
                )

                if not voice_client:

                    voice_client = (
                        await channel.connect()
                    )

                elif voice_client.channel != channel:

                    await voice_client.move_to(
                        channel
                    )

            # Speak
            if (
                voice_client
                and voice_client.is_connected()
            ):

                await speak_in_vc(
                    voice_client,
                    ai_response
                )

        return

    # ======================================
    # BOT MENTION REPLY
    # ======================================

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

            await message.channel.send(
                ai_response
            )

            voice_client = discord.utils.get(
                client.voice_clients,
                guild=message.guild
            )

            if message.author.voice:

                channel = (
                    message.author.voice.channel
                )

                if not voice_client:

                    voice_client = (
                        await channel.connect()
                    )

                elif voice_client.channel != channel:

                    await voice_client.move_to(
                        channel
                    )

            if (
                voice_client
                and voice_client.is_connected()
            ):

                await speak_in_vc(
                    voice_client,
                    ai_response
                )

# ==========================================
# START BOT
# ==========================================

client.run(DISCORD_BOT_TOKEN)