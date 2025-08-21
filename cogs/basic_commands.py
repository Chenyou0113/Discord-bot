import discord
from discord import app_commands
from discord.ext import commands
import re
import langid

class BasicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.GREETING = "你好！我是AI助手 🤖"
        # 支援的語言和對應的回應
        self.language_responses = {
            'zh': '你好！我會用中文回答你的問題。',
            'en': 'Hello! I will answer your question in English.',
            'ja': 'こんにちは！日本語で質問に答えます。',
            'ko': '안녕하세요! 한국어로 질문에 답변하겠습니다.',
            'fr': 'Bonjour! Je répondrai à votre question en français.',
            'de': 'Hallo! Ich werde Ihre Frage auf Deutsch beantworten.',
            'es': '¡Hola! Responderé a tu pregunta en español.',
            'default': '你好！我會嘗試用你的語言回答問題。'
        }
        
    def detect_language(self, text):
        """檢測文本的語言"""
        # 預處理文本以移除網址、表情符號等
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        
        # 使用 langid 檢測語言
        lang, _ = langid.classify(text)
        return lang

    @app_commands.command(name="你好", description="跟機器人打招呼")
    async def hello(self, interaction: discord.Interaction):
        """簡單的打招呼指令"""
        await interaction.response.send_message(self.GREETING)

    @app_commands.command(name="延遲測試", description="檢查機器人的延遲時間")
    async def ping_chinese(self, interaction: discord.Interaction):
        """檢查機器人延遲"""
        await interaction.response.send_message(f'🏓 延遲時間: {round(self.bot.latency * 1000)}ms')
        
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Check bot latency (English version)"""
        await interaction.response.send_message(f'Pong!\n延遲\n{round(self.bot.latency * 1000)}ms\n狀態\n 正常運行')
        
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