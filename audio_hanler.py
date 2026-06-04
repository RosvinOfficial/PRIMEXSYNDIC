import discord
from discord.ext import commands, voice_recv
import asyncio
import subprocess
import os
import logging
from faster_whisper import WhisperModel
from config import settings

logger = logging.getLogger("JarvisVoice")

class VoiceController(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Lazy initialization for standard CUDA/CPU execution execution 
        self.stt_model = WhisperModel(settings.WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")

    @commands.command(name="join")
    async def join_voice(self, ctx):
        """Connects Jarvis to the author's active voice channel."""
        if not ctx.author.voice:
            await ctx.send("You must be actively connected to a voice channel to summon me.")
            return
        channel = ctx.author.voice.channel
        await channel.connect(cls=voice_recv.VoiceRecvClient)
        await ctx.send(f"Connected to system matrix channel: **{channel.name}**")

    @commands.command(name="leave")
    async def leave_voice(self, ctx):
        """Disconnects Jarvis from the voice sub-matrix."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Voice connection terminated clean.")
        else:
            await ctx.send("I am not current deployed to a voice node channel.")

    async def speak(self, vc: discord.VoiceClient, text: str):
        """
        Invokes local Piper TTS compilation pipeline to pipe live speech straight to Discord.
        """
        output_wav = "voice/output.wav"
        # CLI execution pipeline design avoids raw library binding crashes
        cmd = f"echo '{text}' | {settings.PIPER_EXECUTABLE} --model {settings.PIPER_MODEL_PATH} --output_file {output_wav}"
        
        process = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await process.communicate()

        if os.path.exists(output_wav):
            if vc.is_playing():
                vc.stop()
            vc.play(discord.FFmpegPCMAudio(output_wav))
            while vc.is_playing():
                await asyncio.sleep(0.2)
            os.remove(output_wav)

async def setup(bot):
    await bot.add_cog(VoiceController(bot))
