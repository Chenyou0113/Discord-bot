import discord
from discord import app_commands
from discord.ext import commands
import google.generativeai as genai
import logging
import asyncio
from typing import Optional, Dict, Any, Tuple
import time
import os
from dotenv import load_dotenv
import sys

# 確保路徑正確
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 直接在此文件中定義必要的函數，避免導入問題
from utils.gemini_pool import generate_content, create_chat, get_pool_stats, reset_api_pool, get_api_key_stats, reset_api_stats

load_dotenv()
logger = logging.getLogger(__name__)

class ChatSystemCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.chat_history = {}
        self.retry_delays = [1, 2, 4]
        
        # 使用固定的模型
        self.available_models = [
            'gemini-2.0-flash-exp',
            'gemini-pro',
            'gemini-pro-vision'
        ]
            
        # 使用 API 池 - 不需要在此處初始化 model
        self.current_model_name = 'gemini-2.0-flash-exp'
        self.model_instances: Dict[str, Dict[int, Any]] = {}  # 用戶ID -> {實例ID -> 聊天實例}
        
        logger.info(f"聊天系統已初始化，使用 API 連接池和模型: {self.current_model_name}")
            
        # 添加回應控制狀態
        self.responses_paused = False
        
        # 添加速率限制功能
        self.quota_exceeded = False
        self.quota_reset_time = 0
        self.request_times = []
        self.max_requests_per_minute = 8  # 保守設置，避免達到API限制

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """處理訊息事件，包括機器人被提及時的回應"""
        # 忽略機器人自己的訊息
        if message.author == self.bot.user:
            return
        
        # 檢查機器人是否被提及
        if self.bot.user in message.mentions:
            # 檢查是否暫停回應
            if self.responses_paused:
                return
                
            try:
                # 移除提及標籤，獲取純粹的訊息內容
                content = message.content
                for mention in message.mentions:
                    content = content.replace(f'<@{mention.id}>', '').replace(f'<@!{mention.id}>', '')
                content = content.strip()
                
                # 如果沒有內容，提供預設回應
                if not content:
                    await message.channel.send(f"{message.author.mention} 你好！有什麼我可以幫助你的嗎？你可以使用 `/聊天` 指令與我對話，或直接標記我並說出你的問題！")
                    return
                
                # 使用聊天功能回應
                user_id = message.author.id
                
                # 獲取或創建聊天會話
                if user_id not in self.chat_history:
                    self.chat_history[user_id] = create_chat()
                
                # 生成回應
                response = await generate_content(content, chat=self.chat_history[user_id])
                
                if response:
                    # 如果回應太長，分割發送
                    if len(response) > 2000:
                        chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
                        await message.channel.send(f"{message.author.mention} {chunks[0]}")
                        for chunk in chunks[1:]:
                            await message.channel.send(chunk)
                    else:
                        await message.channel.send(f"{message.author.mention} {response}")
                else:
                    await message.channel.send(f"{message.author.mention} 抱歉，我無法處理你的請求，請稍後再試。")
                    
            except Exception as e:
                logger.error(f"處理提及訊息時發生錯誤: {str(e)}")
                await message.channel.send(f"{message.author.mention} 抱歉，處理你的訊息時發生錯誤。請稍後再試或使用 `/聊天` 指令。")
        self.cooldown_users = {}  # 用戶冷卻時間追蹤
        
        # 開發者權限設置
        self.developer_ids = [
            # 在這裡添加開發者的 Discord ID (數字)
            # 例如: 123456789012345678,
        ]

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"ChatSystemCommands cog 已準備就緒!")

    @app_commands.command(
        name="聊天",
        description="與 AI 聊天 (使用 Google Gemini)"
    )
    async def chat(self, interaction: discord.Interaction, 問題: str):
        """與 AI 聊天，支援上下文記憶"""
        user_id = interaction.user.id
        
        # 檢查配額和冷卻時間
        if self.quota_exceeded:
            current_time = time.time()
            if current_time < self.quota_reset_time:
                minutes_left = int((self.quota_reset_time - current_time) / 60) + 1
                await interaction.response.send_message(
                    f"😓 API 配額已達上限，請等待約 {minutes_left} 分鐘後再試。", 
                    ephemeral=True
                )
                return
            else:
                self.quota_exceeded = False
        
        # 用戶冷卻檢查
        if user_id in self.cooldown_users:
            cooldown_end = self.cooldown_users[user_id]
            current_time = time.time()
            if current_time < cooldown_end:
                seconds_left = int(cooldown_end - current_time) + 1
                await interaction.response.send_message(
                    f"⏳ 請稍等 {seconds_left} 秒後再發送新訊息。", 
                    ephemeral=True
                )
                return
            else:
                # 冷卻時間結束，移除冷卻狀態
                del self.cooldown_users[user_id]
        
        # 速率限制檢查
        current_time = time.time()
        # 清除超過1分鐘的請求記錄
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        if len(self.request_times) >= self.max_requests_per_minute:
            self.quota_exceeded = True
            self.quota_reset_time = current_time + 60  # 1分鐘後重置
            await interaction.response.send_message(
                "🚦 請求頻率過高，請稍後再試。", 
                ephemeral=True
            )
            return
        
        # 記錄新的請求時間
        self.request_times.append(current_time)
        
        # 設置用戶冷卻時間 (3秒)
        self.cooldown_users[user_id] = current_time + 3
        
        await interaction.response.defer(thinking=True)
        
        # 檢查用戶是否有聊天歷史記錄
        if user_id not in self.chat_history:
            self.chat_history[user_id] = []
        
        try:
            # 使用 API 池生成內容
            content = await generate_content(
                model=self.current_model_name,
                user_input=問題,
                chat_history=self.chat_history.get(user_id, []),
                temperature=0.7
            )
            
            # 處理回應
            if content:
                # 更新聊天歷史
                self.chat_history[user_id].append({"role": "user", "parts": [問題]})
                self.chat_history[user_id].append({"role": "model", "parts": [content]})
                
                # 限制聊天歷史長度，避免記憶體用量過高
                if len(self.chat_history[user_id]) > 20:  # 保留最近的10輪對話
                    self.chat_history[user_id] = self.chat_history[user_id][-20:]
                
                # 處理過長的回應
                if len(content) > 1900:
                    chunks = [content[i:i+1900] for i in range(0, len(content), 1900)]
                    await interaction.followup.send(chunks[0])
                    for chunk in chunks[1:]:
                        await interaction.channel.send(chunk)
                else:
                    await interaction.followup.send(content)
            else:
                await interaction.followup.send("🤔 AI 未能生成回應，請稍後再試或換一種提問方式。")
        
        except Exception as e:
            logger.error(f"聊天命令發生錯誤: {str(e)}")
            # 嘗試回復錯誤給用戶
            try:
                await interaction.followup.send(f"❌ 處理您的請求時發生錯誤: {str(e)[:1500]}")
            except:
                pass
    
    @app_commands.command(
        name="清除聊天",
        description="清除與 AI 的聊天記錄"
    )
    async def clear_chat(self, interaction: discord.Interaction):
        """清除與 AI 的聊天歷史記錄"""
        user_id = interaction.user.id
        
        if user_id in self.chat_history:
            del self.chat_history[user_id]
            await interaction.response.send_message("✅ 您的聊天記錄已清除！", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ 您沒有聊天記錄需要清除。", ephemeral=True)
    
    @app_commands.command(
        name="切換模型",
        description="切換 AI 聊天使用的模型"
    )
    @app_commands.choices(模型=[
        app_commands.Choice(name="Gemini 2.0 Flash (預設，最快)", value="gemini-2.0-flash-exp"),
        app_commands.Choice(name="Gemini Pro (原始)", value="gemini-pro"),
        app_commands.Choice(name="Gemini Pro Vision (支援圖片)", value="gemini-pro-vision")
    ])
    async def switch_model(self, interaction: discord.Interaction, 模型: app_commands.Choice[str]):
        """切換聊天使用的 AI 模型"""
        # 檢查權限
        if interaction.user.id not in self.developer_ids and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ 只有管理員和開發者可以切換模型。", ephemeral=True)
            return
        
        model_name = 模型.value
        
        if model_name not in self.available_models:
            await interaction.response.send_message(f"❌ 無效的模型名稱: {model_name}", ephemeral=True)
            return
        
        # 更新當前模型
        old_model = self.current_model_name
        self.current_model_name = model_name
        
        # 清空所有用戶的聊天歷史，因為不同模型之間的歷史可能不相容
        self.chat_history.clear()
        
        await interaction.response.send_message(f"✅ 已將聊天模型從 `{old_model}` 切換為 `{model_name}`，並清空所有聊天歷史。", ephemeral=True)
    
    @app_commands.command(
        name="聊天狀態",
        description="檢查 AI 聊天系統狀態"
    )
    async def chat_status(self, interaction: discord.Interaction):
        """檢查 AI 聊天系統的狀態"""
        # 檢查權限
        if interaction.user.id not in self.developer_ids and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("⛔ 只有管理員和開發者可以查看狀態。", ephemeral=True)
            return
        
        # 獲取 API 連接池統計
        pool_stats = get_pool_stats()
        api_key_stats = get_api_key_stats()
        
        # 創建嵌入消息
        embed = discord.Embed(
            title="🤖 AI 聊天系統狀態",
            color=discord.Color.blue()
        )
        
        # 添加基本信息
        embed.add_field(
            name="當前模型", 
            value=f"`{self.current_model_name}`", 
            inline=False
        )
        
        embed.add_field(
            name="活躍聊天", 
            value=f"{len(self.chat_history)} 位用戶", 
            inline=True
        )
        
        embed.add_field(
            name="速率限制", 
            value=f"每分鐘 {self.max_requests_per_minute} 次請求", 
            inline=True
        )
        
        embed.add_field(
            name="限流狀態", 
            value=f"{'⛔ 已啟動' if self.quota_exceeded else '✅ 正常'}", 
            inline=True
        )
        
        # 添加 API 連接池統計
        if pool_stats:
            pool_status = ""
            for model, stats in pool_stats.items():
                pool_status += f"**{model}**: "
                pool_status += f"總請求數: {stats.get('total_requests', 0)}, "
                pool_status += f"成功率: {stats.get('success_rate', 0):.1%}, "
                pool_status += f"平均響應時間: {stats.get('avg_response_time', 0):.2f}秒\n"
            
            embed.add_field(
                name="API 連接池統計", 
                value=pool_status or "無數據", 
                inline=False
            )
        
        # 添加 API 金鑰統計
        if api_key_stats:
            key_status = ""
            for i, (key_id, stats) in enumerate(api_key_stats.items()):
                # 只顯示金鑰 ID 的最後 4 位
                masked_key_id = f"****{key_id[-4:]}" if len(key_id) > 4 else key_id
                key_status += f"**金鑰 {i+1} ({masked_key_id})**: "
                key_status += f"請求: {stats.get('requests', 0)}, "
                key_status += f"錯誤: {stats.get('errors', 0)}, "
                key_status += f"使用率: {stats.get('usage_ratio', 0):.1%}\n"
            
            embed.add_field(
                name="API 金鑰統計", 
                value=key_status or "無數據", 
                inline=False
            )
        
        # 發送嵌入消息
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(
        name="重置聊天api",
        description="重置 AI 聊天 API 連接池 (僅限開發者)"
    )
    async def reset_api(self, interaction: discord.Interaction):
        """重置 AI 聊天系統的 API 連接池 (僅限開發者)"""
        # 檢查是否為開發者
        if interaction.user.id not in self.developer_ids:
            await interaction.response.send_message("⛔ 此命令僅限開發者使用。", ephemeral=True)
            return
        
        # 重置 API 連接池
        reset_api_pool()
        # 重置 API 金鑰統計
        reset_api_stats()
        # 清空所有用戶的聊天歷史
        self.chat_history.clear()
        # 重置配額狀態
        self.quota_exceeded = False
        self.quota_reset_time = 0
        self.request_times.clear()
        self.cooldown_users.clear()
        
        await interaction.response.send_message("✅ AI 聊天 API 連接池已重置，所有統計和聊天歷史已清空。", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ChatSystemCommands(bot))
