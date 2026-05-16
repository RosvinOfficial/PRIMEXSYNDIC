import os
import discord
import requests
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
                    "You are a smart and friendly Discord AI assistant."
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

    # PREFIX COMMAND
    if message.content.startswith("!ai"):

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

    # MENTION REPLY
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

# =========================
# RUN BOT
# =========================

client.run(DISCORD_BOT_TOKEN)