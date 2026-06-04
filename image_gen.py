import discord
from discord.ext import commands
import aiohttp
import io
import base64
from config import settings

class ImageGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="image")
    async def generate_image(self, ctx, *, prompt: str):
        """Generates imagery from localized Stable Diffusion / ComfyUI endpoints."""
        await ctx.send(f"🎨 Initializing diffusion computation for prompt: `{prompt}`...")

        payload = {
            "prompt": prompt,
            "steps": 20,
            "cfg_scale": 7,
            "width": 512,
            "height": 512
        }

        url = f"{settings.STABLE_DIFFUSION_URL}/sdapi/v1/txt2img"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=60) as response:
                    if response.status == 200:
                        res_json = await response.json()
                        image_data = res_json['images'][0]
                        image_bytes = base64.b64decode(image_data.split(",", 1)[-1])
                        
                        file = discord.File(io.BytesIO(image_bytes), filename="jarvis_output.png")
                        embed = discord.Embed(title="Local Diffusion Array Engine", description=f"Prompt: {prompt}", color=discord.Color.blue())
                        embed.set_image(url="attachment://jarvis_output.png")
                        
                        await ctx.send(embed=embed, file=file)
                    else:
                        await ctx.send("Error processing image generation against endpoint array matrix.")
        except Exception as e:
            await ctx.send(f"Critical localized diffusion hardware processing error: {e}")

async def setup(bot):
    await bot.add_cog(ImageGenerator(bot))
