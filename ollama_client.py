import aiohttp
import json
import logging
from config import settings

logger = logging.getLogger("OllamaEngine")

class OllamaEngine:
    def __init__(self):
        self.endpoint = f"{settings.OLLAMA_HOST}/api/chat"

    async def generate_response(self, user_input: str, user_name: str, context: str = "") -> tuple[str, list]:
        """
        Sends payload to local Ollama node. Parses structured responses & tool-use manifests.
        """
        tools_definition = [
            {
                "type": "function",
                "function": {
                    "name": "purge_messages",
                    "description": "Purges a specified amount of messages from the current text channel.",
                    "parameters": {
                        "type": "object",
                        "properties": {"amount": {"type": "integer", "description": "Number of messages"}},
                        "required": ["amount"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "kick_user",
                    "description": "Kicks a member from the Discord guild.",
                    "parameters": {
                        "type": "object",
                        "properties": {"username": {"type": "string", "description": "The target username or display name"}},
                        "required": ["username"]
                    }
                }
            }
        ]

        messages = [
            {"role": "system", "content": f"{settings.SYSTEM_PROMPT}\nContext from memory: {context}"},
            {"role": "user", "content": f"User {user_name} says: {user_input}"}
        ]

        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": messages,
            "tools": tools_definition,
            "stream": False
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.endpoint, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        message_data = data.get("message", {})
                        content = message_data.get("content", "")
                        tool_calls = message_data.get("tool_calls", [])
                        return content, tool_calls
                    else:
                        return "I am experiencing unexpected system connectivity latency with my local brain matrix.", []
        except Exception as e:
            logger.error(f"Ollama integration error: {e}")
            return "System Error: Unable to compute local LLM matrix response.", []
