import discord
from discord import app_commands
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("AdminCommands cog 已初始化")

    @app_commands.command(name="開發者工具", description="開發者工具（僅限管理員）")
    async def dev_tools(self, interaction: discord.Interaction):
        """簡化版的開發者工具指令"""
        # 從環境變數讀取開發者ID
        developer_id = os.getenv('BOT_DEVELOPER_ID')
        
        if not developer_id:
            await interaction.response.send_message("❌ 系統錯誤：開發者ID未設定！", ephemeral=True)
            return
        
        # 檢查是否為開發者
        if str(interaction.user.id) != developer_id:
            await interaction.response.send_message("❌ 此指令僅限機器人開發者使用！", ephemeral=True)
            return
        
        await interaction.response.send_message("✅ 開發者工具測試成功！這是一個簡化版的指令。", ephemeral=True)

async def setup(bot):
    try:
        logger.info("正在載入新的 AdminCommands cog...")
        await bot.add_cog(AdminCommands(bot))
        logger.info("成功載入 AdminCommands cog!")
    except Exception as e:
        logger.error(f"載入 AdminCommands cog 時發生錯誤: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
