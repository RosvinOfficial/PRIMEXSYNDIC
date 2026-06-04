import discord
import logging

logger = logging.getLogger("ToolExecutor")

class ToolExecutor:
    def __init__(self, bot):
        self.bot = bot

    async def execute(self, tool_call: dict, ctx) -> str:
        function_info = tool_call.get("function", {})
        name = function_info.get("name")
        args = json.loads(function_info.get("arguments", "{}")) if isinstance(function_info.get("arguments"), str) else function_info.get("arguments", {})

        if not ctx.guild:
            return "Tool deployment rejected: Execution limited exclusively to Guild environments."

        # Audit permission layer
        if name == "purge_messages":
            if not ctx.author.guild_permissions.manage_messages:
                return "Operation failed: User lacks Manage Messages privileges."
            amount = int(args.get("amount", 10))
            deleted = await ctx.channel.purge(limit=amount)
            return f"System Matrix Action Success: Purged {len(deleted)} messages successfully."

        if name == "kick_user":
            if not ctx.author.guild_permissions.kick_members:
                return "Operation failed: User lacks Kick Members privileges."
            username = args.get("username")
            member = discord.utils.get(ctx.guild.members, name=username)
            if member:
                await member.kick(reason="Jarvis tool system command orchestration.")
                return f"System Matrix Action Success: Terminated presence of {username} from this server."
            return f"Action Failure: User matching {username} could not be located."

        return f"Tool signature {name} acknowledged but unimplemented."
