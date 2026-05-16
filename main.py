# =========================================
# Discord AI Bot (FREE AI API)
# Using OpenRouter + DeepSeek
# =========================================

# Install packages:
# pip install discord.py requests python-dotenv

# =========================================
# FILES NEEDED
# =========================================
#
# bot.py
# requirements.txt
# Procfile
#
# =========================================
# requirements.txt
# =========================================
#
# discord.py
# requests
# python-dotenv
#
# =========================================
# Procfile
# =========================================
#
# worker: python bot.py
#
# =========================================
# Railway Environment Variables
# =========================================
#
# DISCORD_BOT_TOKEN=your_discord_bot_token
# OPENROUTER_API_KEY=your_openrouter_api_key
#
# =========================================

import os
import discord
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Discord Intents
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# =========================================
# AI Function
# =========================================

def ask_ai(prompt):

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-3-8b-instruct:free",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a smart Discord AI assistant."
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
            json=payload
        )

        data = response.json()

        print(data)

        if "choices" not in data:
            return f"API Error: {data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {e}"

# =========================================
# Bot Ready Event
# =========================================

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

# =========================================
# Message Event
# =========================================

@client.event
async def on_message(message):

    # Ignore bot's own messages
    if message.author == client.user:
        return

    # =====================================
    # PREFIX COMMAND
    # Example:
    # !ai hello
    # =====================================

    if message.content.startswith("!ai"):

        user_prompt = message.content[3:].strip()

        if not user_prompt:
            await message.channel.send(
                "Please enter a prompt."
            )
            return

        async with message.channel.typing():

            ai_response = ask_ai(user_prompt)

            # Discord message length limit
            if len(ai_response) > 2000:
                ai_response = ai_response[:1990] + "..."

            await message.channel.send(ai_response)

    # =====================================
    # BOT MENTION REPLY
    # Example:
    # @BotName hello
    # =====================================

    elif client.user in message.mentions:

        user_prompt = message.content.replace(
            f"<@{client.user.id}>",
            ""
        ).strip()

        if not user_prompt:
            user_prompt = "Hello"

        async with message.channel.typing():

            ai_response = ask_ai(user_prompt)

            if len(ai_response) > 2000:
                ai_response = ai_response[:1990] + "..."

            await message.channel.send(ai_response)

# =========================================
# Run Bot
# =========================================

client.run(DISCORD_BOT_TOKEN)