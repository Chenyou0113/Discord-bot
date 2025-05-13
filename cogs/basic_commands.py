import discord
from discord import app_commands
from discord.ext import commands

class BasicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.GREETING = "你好！我是AI助手 🤖"

    @app_commands.command(name="hello", description="跟機器人打招呼")
    async def hello(self, interaction: discord.Interaction):
        """簡單的打招呼指令"""
        await interaction.response.send_message(self.GREETING)

    @app_commands.command(name="ping", description="檢查機器人的延遲時間")
    async def ping(self, interaction: discord.Interaction):
        """檢查機器人延遲"""
        await interaction.response.send_message(f'🏓 延遲時間: {round(self.bot.latency * 1000)}ms')

async def setup(bot: commands.Bot):
    await bot.add_cog(BasicCommands(bot))