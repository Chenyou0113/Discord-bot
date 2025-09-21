import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class VoiceSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.temp_channels = {}  # 儲存臨時語音頻道的資訊

    async def create_temp_channel(self, member: discord.Member, category: discord.CategoryChannel, base_name="🔊語音房"):
        """創建臨時語音頻道"""
        channel_name = f"{base_name} - {member.display_name}"
        try:
            new_channel = await category.create_voice_channel(
                name=channel_name,
                user_limit=5,  # 預設限制5人
                reason=f"由 {member.display_name} 創建的臨時語音房"
            )
            self.temp_channels[new_channel.id] = member.id
            return new_channel
        except discord.Forbidden:
            return None

    async def cleanup_empty_channels(self):
        """清理空的臨時語音頻道"""
        for channel_id, creator_id in list(self.temp_channels.items()):
            channel = self.bot.get_channel(channel_id)
            if channel and len(channel.members) == 0:
                try:
                    await channel.delete(reason="空的臨時語音房")
                    del self.temp_channels[channel_id]
                except (discord.NotFound, discord.Forbidden):
                    pass

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """處理語音狀態更新"""
        # 如果用戶加入了創建語音房的頻道
        if after.channel and after.channel.name == "➕創建語音房":
            category = after.channel.category
            new_channel = await self.create_temp_channel(member, category)
            if new_channel:
                try:
                    await member.move_to(new_channel)
                except discord.Forbidden:
                    pass
        
        # 清理空的臨時語音房
        await self.cleanup_empty_channels()

    @app_commands.command(name="setup_voice", description="設置自動語音房系統")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_voice(self, interaction: discord.Interaction):
        """設置自動語音房系統"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 此指令僅限管理員使用！", ephemeral=True)
            return
        
        try:
            # 創建語音房類別
            category = await interaction.guild.create_category("🎤 語音頻道")
            # 創建初始頻道
            await category.create_voice_channel(
                name="➕創建語音房",
                user_limit=1,
                reason="自動語音房系統"
            )
            
            await interaction.response.send_message(
                "✅ 自動語音房系統已設置完成！\n"
                "使用者加入「➕創建語音房」後會自動創建新的語音頻道。\n"
                "當頻道空無一人時會自動刪除。",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ 設置失敗！請確認機器人有足夠的權限。\n"
                "需要的權限：管理頻道、移動成員",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"設置語音房時發生錯誤: {str(e)}")
            await interaction.response.send_message("❌ 設置過程發生錯誤！", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceSystem(bot))