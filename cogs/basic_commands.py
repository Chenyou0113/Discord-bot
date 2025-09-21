import discord
from discord import app_commands
from discord.ext import commands

class BasicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.GREETING = "你好！我是AI助手 🤖"

    @app_commands.command(name="hello", description="跟機器人打招呼")
    async def hello(self, interaction: discord.Interaction):
        """簡單的打招呼指令，固定使用中文回應"""
        # 由於這是中文指令「你好」，直接使用中文回應
        response = "你好！我是AI助手 🤖\n很高興為你服務！"
        await interaction.response.send_message(response)

    @app_commands.command(name="latency", description="檢查機器人的延遲時間")
    async def ping_chinese(self, interaction: discord.Interaction):
        """檢查機器人延遲"""
        await interaction.response.send_message(f'🏓 延遲時間: {round(self.bot.latency * 1000)}ms')
        
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Check bot latency (with language detection)"""
        from utils.language_utils import get_response_in_language
        
        # 使用用戶的訊息內容或使用者名稱進行語言檢測
        user_content = interaction.user.display_name
        if hasattr(interaction, 'message') and hasattr(interaction.message, 'content'):
            user_content = interaction.message.content
            
        latency = round(self.bot.latency * 1000)
        response = get_response_in_language(user_content, 'ping', latency)
        await interaction.response.send_message(response)
        
    # 這個方法將被其他cog和機器人核心使用
    def get_response_in_language(self, message_content):
        """根據消息內容提供適合的語言回應"""
        # 檢測語言
        detected_lang = self.detect_language(message_content)
        
        # 獲取對應語言的回應
        if detected_lang in self.language_responses:
            return detected_lang, self.language_responses[detected_lang]
        else:
            return 'default', self.language_responses['default']

async def setup(bot: commands.Bot):
    await bot.add_cog(BasicCommands(bot))