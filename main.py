# ================================
# Discord AI Bot using Grok API
# ================================
# Install:
# pip install discord.py requests python-dotenv
#
# Create a .env file:
# DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN
# GROK_API_KEY=YOUR_GROK_API_KEY
#
# Run:
# python bot.py

import os
import discord
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GROK_API_KEY = os.getenv("GROK_API_KEY")

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Grok API endpoint
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# Function to get AI response
def ask_grok(prompt):
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "grok-3",
        "messages": [
            {
                "role": "system",
                "content": "You are a smart Discord AI assistant."
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
            GROK_API_URL,
            headers=headers,
            json=payload
        )

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {e}"

# Bot ready event
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

# Message event
@client.event
async def on_message(message):

    # Ignore bot's own messages
    if message.author == client.user:
        return

    # Command prefix
    if message.content.startswith("!ai"):

        user_prompt = message.content[3:].strip()

        if not user_prompt:
            await message.channel.send("Please enter a prompt.")
            return

        # Typing indicator
        async with message.channel.typing():

            ai_response = ask_grok(user_prompt)

            # Discord message limit protection
            if len(ai_response) > 2000:
                ai_response = ai_response[:1990] + "..."

            await message.channel.send(ai_response)

# Run bot
client.run(DISCORD_TOKEN)