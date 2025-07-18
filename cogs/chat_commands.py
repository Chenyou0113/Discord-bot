import discord
from discord import app_commands
from discord.ext import commands
import google.generativeai as genai
import logging
import asyncio
from typing import Optional
import time
import os
from dotenv import load_dotenv
import sys

load_dotenv()
logger = logging.getLogger(__name__)

# 配置 Gemini API
API_KEY = os.getenv('GOOGLE_API_KEY')
if not API_KEY:
    logger.error('錯誤: 找不到 GOOGLE_API_KEY')
    exit(1)

# 初始化 Gemini
genai.configure(api_key=API_KEY)

class ChatCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.chat_history = {}
        self.retry_delays = [1, 2, 4]
        
        # 使用固定的模型
        self.available_models = [
            'gemini-2.0-flash-exp',
            'gemini-pro'
        ]
            
        # 初始化模型
        try:
            self.current_model_name = 'gemini-2.0-flash-exp'
            self.model = genai.GenerativeModel(self.current_model_name)
            logger.info(f"成功初始化聊天系統，使用模型: {self.current_model_name}")
        except Exception as e:
            logger.error(f"初始化聊天系統時發生錯誤: {str(e)}")
            raise
            
        # 添加回應控制狀態
        self.responses_paused = False
        
        # 添加速率限制功能
        self.quota_exceeded = False
        self.quota_reset_time = 0
        self.request_times = []
        self.max_requests_per_minute = 8  # 保守設置，避免達到API限制
        self.cooldown_users = {}  # 用戶冷卻時間追蹤
        
        # 開發者權限設置
        self.developer_ids = [
            # 在這裡添加開發者的 Discord ID (數字)
            # 例如: 123456789012345678,
        ]
        self.dev_mode_enabled = True  # 預設啟用開發者模式
        self.dev_mode_guilds = set()  # 啟用開發者模式的伺服器ID

    async def _check_admin(self, interaction: discord.Interaction) -> bool:
        """檢查使用者是否為機器人開發者"""
        developer_id = os.getenv('BOT_DEVELOPER_ID')
        if developer_id and str(interaction.user.id) == developer_id:
            return True
        
        await interaction.response.send_message("❌ 此指令僅限機器人開發者使用！", ephemeral=True)
        logger.warning(f"用戶 {interaction.user.name} ({interaction.user.id}) 嘗試使用管理員指令")
        return False

    async def _check_rate_limit(self):
        """檢查API使用頻率，避免達到配額限制"""
        current_time = time.time()
        
        # 如果已經超出配額，檢查是否可以重置
        if self.quota_exceeded:
            if current_time >= self.quota_reset_time:
                logger.info("API配額重置時間已到，恢復請求")
                self.quota_exceeded = False
                self.request_times = []
            else:
                remaining = int(self.quota_reset_time - current_time)
                return False, f"API配額已達上限，請等待 {remaining} 秒後再試"
        
        # 清理過期的請求記錄 (超過60秒的)
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        # 檢查是否達到每分鐘請求上限
        if len(self.request_times) >= self.max_requests_per_minute:
            # 設置配額重置時間 (從第一個請求開始算起的60秒後)
            self.quota_reset_time = self.request_times[0] + 60
            self.quota_exceeded = True
            remaining = int(self.quota_reset_time - current_time)
            logger.warning(f"已達到自定義速率限制，暫停請求 {remaining} 秒")
            return False, f"為避免達到API配額限制，請等待 {remaining} 秒後再試"
        
        # 記錄這次請求
        self.request_times.append(current_time)
        return True, ""
    
    async def _check_user_cooldown(self, user_id: str):
        """檢查用戶是否處於冷卻時間中"""
        current_time = time.time()
        if user_id in self.cooldown_users:
            reset_time = self.cooldown_users[user_id]
            if current_time < reset_time:
                remaining = int(reset_time - current_time)
                return False, f"請稍等 {remaining} 秒後再發送新的請求"
            else:
                del self.cooldown_users[user_id]
        return True, ""
        
    def _set_user_cooldown(self, user_id: str, seconds: int = 5):
        """設置用戶冷卻時間"""
        self.cooldown_users[user_id] = time.time() + seconds
        
    def _is_developer(self, user_id: int) -> bool:
        """檢查用戶是否為開發者"""
        return str(user_id) in map(str, self.developer_ids)
    
    def _check_dev_permission(self, user_id: int, guild_id: int = None) -> bool:
        """檢查用戶是否擁有開發者權限
        
        返回True如果：
        1. 用戶是開發者
        2. 機器人處於開發者模式，且該用戶為管理員
        """
        # 直接檢查是否為開發者
        if self._is_developer(user_id):
            return True
            
        # 檢查是否為啟用開發者模式的伺服器中的管理員
        if self.dev_mode_enabled and guild_id is not None:
            if guild_id in self.dev_mode_guilds:
                # 獲取伺服器和成員物件
                guild = self.bot.get_guild(guild_id)
                if guild:
                    member = guild.get_member(user_id)
                    if member and member.guild_permissions.administrator:
                        return True
        
        # 默認情況下，不具有開發者權限
        return False

    async def generate_response(self, user_id: str, message: str) -> str:
        """生成 AI 回應"""
        # 檢查是否暫停回應
        if self.responses_paused:
            return "⚠️ 機器人回應功能目前已暫停。請聯繫管理員了解更多資訊。"
            
        # 檢查用戶冷卻時間
        can_proceed, cooldown_msg = await self._check_user_cooldown(user_id)
        if not can_proceed:
            return f"⏱️ {cooldown_msg}"
        
        # 檢查API速率限制
        can_proceed, rate_limit_msg = await self._check_rate_limit()
        if not can_proceed:
            return f"⚠️ {rate_limit_msg}"
        
        try:
            # 為用戶設置冷卻時間 (防止洪水請求)
            self._set_user_cooldown(user_id, 3)
            
            if user_id not in self.chat_history:
                # 建立新的對話
                self.chat_history[user_id] = []
            
            # 添加用戶訊息到歷史
            self.chat_history[user_id].append(message)
            
            # 建立對話內容
            conversation = ""
            if len(self.chat_history[user_id]) <= 1:
                # 如果是第一條訊息，加入系統提示
                conversation = "請直接回覆問題內容，不要自我介紹或問候。\n\n"
            
            # 添加歷史對話
            for msg in self.chat_history[user_id][-3:]:  # 只保留最近3條訊息
                conversation += f"用戶: {msg}\n"
            
                response = await asyncio.to_thread(
                lambda: self.model.generate_content(conversation).text
            )

            # 添加回應到歷史
            self.chat_history[user_id].append(response)
            
            # 如果歷史訊息太多，保留最後 6 條（3輪對話）
            if len(self.chat_history[user_id]) > 6:
                self.chat_history[user_id] = self.chat_history[user_id][-6:]

            return response
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"生成回應時發生錯誤: {error_msg}")
            
            # 處理不同類型的錯誤
            if "safety" in error_msg.lower():
                return "抱歉，您的請求可能包含不適當的內容，我無法回應。請調整您的問題。"
            elif "rate limit" in error_msg.lower() or "quota" in error_msg.lower() or "429" in error_msg:
                # 解析重試時間 (如果有)
                retry_seconds = 60  # 默認60秒
                import re
                retry_match = re.search(r'retry_delay\s*{\s*seconds:\s*(\d+)', error_msg)
                if retry_match:
                    try:
                        retry_seconds = int(retry_match.group(1))
                    except ValueError:
                        pass
                
                # 設置全局配額限制標記
                self.quota_exceeded = True
                self.quota_reset_time = time.time() + retry_seconds
                
                logger.warning(f"API配額限制，將等待 {retry_seconds} 秒後才能使用")
                return f"⚠️ 抱歉，目前API使用量已達到配額限制，請在約 {retry_seconds} 秒後再試。\n\n如果這個問題持續發生，請聯繫管理員檢查API配額設置。"
            else:
                logger.error(f"未知錯誤: {error_msg}")
                return "抱歉，處理您的請求時遇到技術問題。請稍後再試。"

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """處理訊息回覆"""
        # 忽略機器人自己的訊息
        if message.author == self.bot.user:
            return
            
        # 處理回覆機器人訊息的情況
        if message.reference and message.reference.resolved:
            referenced_message = message.reference.resolved
            
            if referenced_message.author == self.bot.user:
                user_id = str(message.author.id)
                
                try:
                    async with message.channel.typing():
                        # 生成回應
                        response = await self.generate_response(user_id, message.content)
                        
                        # 分段發送過長訊息
                        if len(response) <= 2000:
                            await message.reply(response)
                        else:
                            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                            await message.reply(chunks[0])
                            for chunk in chunks[1:]:
                                await asyncio.sleep(1)
                                await message.channel.send(chunk)
                            
                except Exception as e:
                    logger.error(f"回覆訊息時發生錯誤: {str(e)}")
                    await message.reply("❌ 抱歉，處理您的訊息時發生錯誤。請稍後再試或使用 `/chat` 指令開始新對話。")
        
        # 處理標記機器人的情況
        elif self.bot.user in message.mentions:
            user_id = str(message.author.id)
            message_content = message.content.lower()
            
            # 去除標記部分，獲取真正的訊息內容
            clean_content = message.content.replace(f'<@{self.bot.user.id}>', '').strip()
            
            # 處理「繼續」指令
            if clean_content == '繼續' or clean_content == 'continue':
                # 檢查使用者是否有對話歷史
                if user_id not in self.chat_history or len(self.chat_history[user_id]) < 2:
                    await message.reply("❓ 抱歉，找不到需要繼續的對話。請先開始一個新對話。")
                    return
                    
                try:
                    async with message.channel.typing():
                        # 獲取最近的AI回應
                        last_response = self.chat_history[user_id][-1]
                        
                        # 創建「繼續」提示
                        continuation_prompt = f"請繼續你剛才的回應。你剛才說到：\n{last_response}\n\n請繼續。"
                        
                        # 生成回應
                        response = await self.generate_response(user_id, continuation_prompt)
                        
                        # 分段發送過長訊息
                        if len(response) <= 2000:
                            await message.reply(response)
                        else:
                            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                            await message.reply(chunks[0])
                            for chunk in chunks[1:]:
                                await asyncio.sleep(1)
                                await message.channel.send(chunk)
                                
                except Exception as e:
                    logger.error(f"處理「繼續」指令時發生錯誤: {str(e)}")
                    await message.reply("❌ 抱歉，處理您的請求時發生錯誤。請稍後再試。")
            else:
                # 處理其他標記機器人的一般訊息
                try:
                    async with message.channel.typing():
                        # 生成回應
                        response = await self.generate_response(user_id, clean_content)
                        
                        # 分段發送過長訊息
                        if len(response) <= 2000:
                            await message.reply(response)
                        else:
                            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                            await message.reply(chunks[0])
                            for chunk in chunks[1:]:
                                await asyncio.sleep(1)
                                await message.channel.send(chunk)
                                
                except Exception as e:
                    logger.error(f"回覆標記訊息時發生錯誤: {str(e)}")
                    await message.reply("❌ 抱歉，處理您的訊息時發生錯誤。請稍後再試或使用 `/chat` 指令開始新對話。")

    @app_commands.command(name="clear_chat", description="清除與 AI 助手的對話歷史")
    async def clear_chat(self, interaction: discord.Interaction):
        """清除對話歷史"""
        user_id = str(interaction.user.id)
        
        # 系統通知使用嵌入消息
        embed = discord.Embed(
            title="🔄 清除對話歷史",
            color=discord.Color.green() if user_id in self.chat_history else discord.Color.blue()
        )
        
        if user_id in self.chat_history:
            del self.chat_history[user_id]
            embed.description = "✅ 已清除對話歷史！現在可以開始新的對話。"
        else:
            embed.description = "ℹ️ 您目前沒有進行中的對話。"
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="current_model",
        description="查看目前使用的 AI 模型"
    )
    async def current_model(self, interaction: discord.Interaction):
        """顯示當前使用的模型"""
        embed = discord.Embed(
            title="🤖 當前 AI 模型",
            description=f"目前使用的模型是: **{self.current_model_name}**",
            color=discord.Color.blue()
        )
        
        # 如果是管理員，顯示所有可用的模型
        developer_id = os.getenv('BOT_DEVELOPER_ID')
        if developer_id and str(interaction.user.id) == developer_id:
            embed.add_field(
                name="可用模型",
                value="\n".join([f"・{model}" for model in self.available_models]),
                inline=False
            )
            embed.add_field(
                name="💡 提示",
                value="管理員可以使用 `/set_model` 指令來更換模型",
                inline=False
            )
            
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="chat",
        description="與 AI 助手對話"
    )
    @app_commands.describe(
        message="您想說的話",
        private="是否為私人回應(預設為否)"
    )
    async def chat(
        self,
        interaction: discord.Interaction,
        message: str,
        private: Optional[bool] = False
    ):
        """與 AI 助手對話"""
        # 增加日誌記錄
        logger.info(f"用戶 {interaction.user} 使用了 /chat 指令")
        
        await interaction.response.defer(ephemeral=private)
        
        user_id = str(interaction.user.id)
        
        for attempt in range(len(self.retry_delays) + 1):
            try:
                # 生成回應
                response = await self.generate_response(user_id, message)
                
                # 分段發送過長訊息 (使用純文字)
                if len(response) <= 2000:
                    await interaction.followup.send(response, ephemeral=private)
                else:
                    chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                    for i, chunk in enumerate(chunks):
                        if i == 0:
                            await interaction.followup.send(chunk, ephemeral=private)
                        else:
                            await asyncio.sleep(1)
                            await interaction.followup.send(chunk, ephemeral=private)
                
                return
                
            except Exception as e:
                logger.error(f"聊天過程中發生錯誤: {str(e)}")
                if attempt < len(self.retry_delays):
                    await asyncio.sleep(self.retry_delays[attempt])
                    continue
                else:
                    await interaction.followup.send("❌ 抱歉，我現在似乎無法正常回應。請稍後再試或使用 `/clear_chat` 重新開始對話。", ephemeral=True)

    @app_commands.command(
        name="set_model",
        description="更換 AI 模型 (僅限管理員使用)"
    )
    @app_commands.describe(
        model_name="模型名稱 (輸入任何文字查看可用模型列表)"
    )
    async def set_model(
        self,
        interaction: discord.Interaction,
        model_name: str
    ):
        """更換 AI 模型"""
        if not await self._check_admin(interaction):
            return

        # 如果模型名稱不在可用列表中，顯示可用模型列表
        if model_name not in self.available_models:
            embed = discord.Embed(
                title="⚠️ 無效的模型名稱",
                description="請從以下可用模型中選擇：",
                color=discord.Color.yellow()
            )
            
            for i, model in enumerate(self.available_models):
                embed.add_field(
                    name=f"模型 {i+1}",
                    value=f"`{model}`",
                    inline=True
                )
                
            embed.add_field(
                name="使用方法",
                value=f"請複製上方任一模型名稱，並執行指令：\n`/set_model 模型名稱`",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            # 嘗試初始化新模型
            new_model = genai.GenerativeModel(model_name)
            
            # 更新模型
            self.model = new_model
            self.current_model_name = model_name
            self.chat_history.clear()  # 清除所有對話歷史
            
            embed = discord.Embed(
                title="✅ 模型更新成功",
                description=f"已切換到 `{model_name}` 模型",
                color=discord.Color.green()
            )
            embed.add_field(
                name="注意",
                value="所有用戶的對話歷史已被清除",
                inline=False
            )
            await interaction.response.send_message(embed=embed)
            logger.info(f"已更換模型至: {model_name}")
                
        except Exception as e:
            error_msg = f"更換模型時發生錯誤: {str(e)}"
            logger.error(error_msg)
            await interaction.response.send_message(
                f"❌ {error_msg}",
                ephemeral=True
            )
            
    @app_commands.command(
        name="toggle_responses",
        description="暫停或恢復機器人的回應 (僅限管理員使用)"
    )
    async def toggle_responses(self, interaction: discord.Interaction):
        """暫停或恢復機器人的回應"""
        # 檢查權限
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 此指令僅限管理員使用！", ephemeral=True)
            return
            
        # 切換回應狀態
        self.responses_paused = not self.responses_paused
        
        # 創建嵌入消息
        embed = discord.Embed(
            title="🔄 機器人回應狀態已更改",
            description=f"機器人回應功能已{'暫停' if self.responses_paused else '恢復'}",
            color=discord.Color.orange() if self.responses_paused else discord.Color.green()
        )
        
        if self.responses_paused:
            embed.add_field(
                name="⚠️ 注意",
                value="機器人現在不會回應任何聊天請求。用戶仍然可以發送訊息，但機器人會回覆暫停通知。",
                inline=False
            )
        else:
            embed.add_field(
                name="✅ 已恢復",
                value="機器人現在會正常回應所有聊天請求。",
                inline=False
            )
            
        # 記錄操作
        logger.info(f"管理員 {interaction.user} 已{'暫停' if self.responses_paused else '恢復'}機器人的回應功能")
        
        # 發送回應
        await interaction.response.send_message(embed=embed)
        
        # 在操作日誌頻道公告此變更（如果存在）
        try:
            admin_cog = self.bot.get_cog("AdminCommands")
            if admin_cog and hasattr(admin_cog, "log_channel_id"):
                for guild in self.bot.guilds:
                    log_channel_id = admin_cog.log_channel_id.get(guild.id)
                    if log_channel_id:
                        log_channel = guild.get_channel(log_channel_id)
                        if log_channel:
                            system_embed = discord.Embed(
                                title="📢 系統通知",
                                description=f"管理員 {interaction.user.mention} 已{'暫停' if self.responses_paused else '恢復'}機器人的回應功能",
                                color=discord.Color.orange() if self.responses_paused else discord.Color.green(),
                                timestamp=discord.utils.utcnow()
                            )
                            await log_channel.send(embed=system_embed)
        except Exception as e:
            logger.error(f"發送系統通知時發生錯誤: {str(e)}")
            
    @app_commands.command(
        name="api_status",
        description="查看 API 使用狀態和配額設置 (僅限管理員使用)"
    )
    async def api_status(self, interaction: discord.Interaction):
        """查看 API 使用狀態和配額設置"""
        # 檢查權限
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 此指令僅限管理員使用！", ephemeral=True)
            return
            
        # 建立狀態嵌入消息
        embed = discord.Embed(
            title="🔌 API 狀態監控",
            description="Gemini API 使用情況和配額設置",
            color=discord.Color.blue()
        )
        
        # 基本配額設置
        embed.add_field(
            name="📊 目前配額設置",
            value=f"每分鐘最大請求數: **{self.max_requests_per_minute}**",
            inline=False
        )
        
        # 當前使用情況
        current_time = time.time()
        recent_requests = [t for t in self.request_times if current_time - t < 60]
        
        embed.add_field(
            name="📈 當前使用情況",
            value=f"過去一分鐘請求: **{len(recent_requests)}/{self.max_requests_per_minute}**\n"
                  f"配額狀態: {'⚠️ 已超出' if self.quota_exceeded else '✅ 正常'}",
            inline=False
        )
        
        # 如果配額已超出，顯示重置時間
        if self.quota_exceeded:
            remaining = int(self.quota_reset_time - current_time)
            embed.add_field(
                name="⏱️ 配額重置",
                value=f"預計重置時間: **{remaining}** 秒後",
                inline=False
            )
            
        # 顯示活躍用戶冷卻時間
        cooldown_users = len(self.cooldown_users)
        embed.add_field(
            name="👥 用戶冷卻狀態",
            value=f"目前處於冷卻時間的用戶: **{cooldown_users}**",
            inline=False
        )
        
        # 使用模型信息
        embed.add_field(
            name="🤖 使用中的模型",
            value=f"模型名稱: **{self.current_model_name}**",
            inline=False
        )
        
        # 添加建議
        embed.set_footer(text="使用 /set_rate_limit 指令可以調整每分鐘請求數限制")
        
        # 發送回應
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(
        name="set_rate_limit",
        description="設置 API 請求速率限制 (僅限管理員使用)"
    )
    @app_commands.describe(
        requests_per_minute="每分鐘允許的最大請求數 (1-10)"
    )
    async def set_rate_limit(
        self,
        interaction: discord.Interaction,
        requests_per_minute: int
    ):
        """設置 API 請求速率限制"""
        # 檢查權限
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 每分鐘請求數必須在 1 到 10 之間！", ephemeral=True)
            return
            
        # 驗證參數範圍
        if requests_per_minute < 1 or requests_per_minute > 10:
            await interaction.response.send_message("❌ 每分鐘請求數必須在 1 到 10 之間！", ephemeral=True)
            return
            
        # 更新設置
        old_limit = self.max_requests_per_minute
        self.max_requests_per_minute = requests_per_minute
        
        # 創建嵌入消息
        embed = discord.Embed(
            title="🔄 API 速率限制已更新",
            description=f"每分鐘最大請求數已從 **{old_limit}** 更改為 **{requests_per_minute}**",
            color=discord.Color.green()
        )
        
        # 根據設置提供建議
        if requests_per_minute >= 9:
            embed.add_field(
                name="⚠️ 警告",
                value="設置接近 Gemini API 的免費配額上限，可能會頻繁觸發配額限制",
                inline=False
            )
        elif requests_per_minute <= 3:
            embed.add_field(
                name="💡 提示",
                value="當前設置較為保守，API 使用效率較低但更安全",
                inline=False
            )
        else:
            embed.add_field(
                name="✅ 適中設置",
                value="當前設置平衡了 API 使用效率和安全性",
                inline=False
            )
            
        # 記錄操作
        logger.info(f"管理員 {interaction.user} 將 API 速率限制從 {old_limit} 更改為 {requests_per_minute}")
        
        # 發送回應
        await interaction.response.send_message(embed=embed)
        
        # 在操作日誌頻道公告此變更（如果存在）
        try:
            admin_cog = self.bot.get_cog("AdminCommands")
            if admin_cog and hasattr(admin_cog, "log_channel_id"):
                for guild in self.bot.guilds:
                    log_channel_id = admin_cog.log_channel_id.get(guild.id)
                    if log_channel_id:
                        log_channel = guild.get_channel(log_channel_id)
                        if log_channel:
                            system_embed = discord.Embed(
                                title="📢 系統設置變更",
                                description=f"管理員 {interaction.user.mention} 已更改 API 速率限制",
                                color=discord.Color.blue(),
                                timestamp=discord.utils.utcnow()
                            )
                            system_embed.add_field(
                                name="變更詳情",
                                value=f"每分鐘最大請求數: {old_limit} → {requests_per_minute}",
                                inline=False
                            )
                            await log_channel.send(embed=system_embed)
        except Exception as e:
            logger.error(f"發送系統通知時發生錯誤: {str(e)}")
            
    @app_commands.command(
        name="reset_quota",
        description="手動重置 API 配額限制狀態 (僅限管理員使用)"
    )
    async def reset_quota(self, interaction: discord.Interaction):
        """手動重置 API 配額限制狀態"""
        # 檢查權限
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 此指令僅限管理員使用！", ephemeral=True)
            return
            
        # 重置配額狀態
        old_status = "已達到限制" if self.quota_exceeded else "正常"
        self.quota_exceeded = False
        self.quota_reset_time = 0
        self.request_times = []
        
        # 創建嵌入消息
        embed = discord.Embed(
            title="🔄 API 配額狀態已重置",
            description=f"API 配額狀態已從「{old_status}」重置為「正常」",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="✅ 操作完成",
            value="所有請求計數已清除，用戶現在可以正常使用 API",
            inline=False
        )
        
        embed.add_field(
            name="💡 提示",
            value="此操作僅重置了機器人內部的配額計數，如果 Google API 本身仍有限制，可能仍會遇到問題",
            inline=False
        )
            
        # 記錄操作
        logger.info(f"管理員 {interaction.user} 手動重置了 API 配額狀態")
        
        # 發送回應
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(
        name="dev_mode",
        description="開啟或關閉開發者模式 (僅限開發者使用)"
    )
    @app_commands.describe(
        enable="是否啟用開發者模式",
        all_guilds="是否在所有伺服器上啟用"
    )
    async def dev_mode(
        self,
        interaction: discord.Interaction,
        enable: bool,
        all_guilds: bool = False
    ):
        """開啟或關閉開發者模式"""
        # 檢查開發者權限
        if not self._is_developer(interaction.user.id):
            await interaction.response.send_message("❌ 此指令僅限機器人開發者使用！", ephemeral=True)
            return
            
        # 更新開發者模式狀態
        self.dev_mode_enabled = enable
        
        # 根據all_guilds參數決定是更新所有伺服器還是僅當前伺服器
        if enable:
            if all_guilds:
                # 添加所有伺服器到開發者模式
                for guild in self.bot.guilds:
                    self.dev_mode_guilds.add(guild.id)
                guild_msg = "所有伺服器"
            else:
                # 僅添加當前伺服器
                self.dev_mode_guilds.add(interaction.guild.id)
                guild_msg = f"當前伺服器 ({interaction.guild.name})"
        else:
            if all_guilds:
                # 清空所有開發者模式伺服器
                self.dev_mode_guilds.clear()
                guild_msg = "所有伺服器"
            else:
                # 僅移除當前伺服器
                if interaction.guild.id in self.dev_mode_guilds:
                    self.dev_mode_guilds.remove(interaction.guild.id)
                guild_msg = f"當前伺服器 ({interaction.guild.name})"
        
        # 創建嵌入消息
        embed = discord.Embed(
            title="⚙️ 開發者模式設置",
            description=f"開發者模式已{'啟用' if enable else '禁用'} ({guild_msg})",
            color=discord.Color.gold() if enable else discord.Color.light_grey()
        )
        
        if enable:
            embed.add_field(
                name="✅ 已啟用",
                value="在開發者模式中，伺服器管理員可以使用開發者指令",
                inline=False
            )
            
            # 顯示哪些伺服器啟用了開發者模式
            if self.dev_mode_guilds:
                enabled_guilds = []
                for guild_id in self.dev_mode_guilds:
                    guild = self.bot.get_guild(guild_id)
                    if guild:
                        enabled_guilds.append(f"• {guild.name} (ID: {guild.id})")
                
                if enabled_guilds:
                    embed.add_field(
                        name="📋 已啟用的伺服器",
                        value="\n".join(enabled_guilds),
                        inline=False
                    )
        else:
            embed.add_field(
                name="❌ 已禁用",
                value="開發者模式已關閉，只有機器人開發者可以使用開發者指令",
                inline=False
            )
            
        # 記錄操作
        logger.info(f"開發者 {interaction.user} {'啟用' if enable else '禁用'}了開發者模式 (範圍: {guild_msg})")
        
        # 發送回應
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @app_commands.command(
        name="add_developer",
        description="添加開發者 (僅限現有開發者使用)"
    )
    @app_commands.describe(
        user="要添加為開發者的用戶"
    )
    async def add_developer(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        """添加新的開發者"""
        # 檢查是否為開發者
        if not self._is_developer(interaction.user.id):
            await interaction.response.send_message("❌ 此指令僅限機器人開發者使用！", ephemeral=True)
            return
            
        # 檢查用戶是否已經是開發者
        if self._is_developer(user.id):
            await interaction.response.send_message(f"⚠️ {user.mention} 已經是開發者了！", ephemeral=True)
            return
            
        # 添加開發者
        self.developer_ids.append(str(user.id))
        
        # 創建嵌入消息
        embed = discord.Embed(
            title="👑 添加開發者",
            description=f"{user.mention} 已被添加為機器人開發者",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="✅ 權限已授予",
            value=f"用戶 ID: {user.id}\n用戶名: {user.name}",
            inline=False
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # 記錄操作
        logger.info(f"開發者 {interaction.user} 將 {user.name} (ID: {user.id}) 添加為開發者")
        
        # 發送回應
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(
        name="remove_developer",
        description="移除開發者身份 (僅限現有開發者使用)"
    )
    @app_commands.describe(
        user_id="要移除的開發者ID"
    )
    async def remove_developer(
        self,
        interaction: discord.Interaction,
        user_id: str
    ):
        """移除開發者"""
        # 檢查是否為開發者
        if not self._is_developer(interaction.user.id):
            await interaction.response.send_message("❌ 此指令僅限機器人開發者使用！", ephemeral=True)
            return
            
        # 檢查要移除的ID是否存在
        if user_id not in map(str, self.developer_ids):
            await interaction.response.send_message(f"⚠️ ID `{user_id}` 不是開發者！", ephemeral=True)
            return
            
        # 防止移除自己
        if str(interaction.user.id) == user_id:
            await interaction.response.send_message("❌ 你不能移除自己的開發者身份！", ephemeral=True)
            return
            
        # 移除開發者
        self.developer_ids.remove(user_id)
        
        # 創建嵌入消息
        embed = discord.Embed(
            title="👑 移除開發者",
            description=f"ID `{user_id}` 已被移除開發者身份",
            color=discord.Color.red()
        )
        
        # 嘗試獲取用戶資訊
        user = None
        for guild in self.bot.guilds:
            user = guild.get_member(int(user_id))
            if user:
                break
                
        if user:
            embed.add_field(
                name="用戶資訊",
                value=f"用戶名: {user.name}\n提及: {user.mention}",
                inline=False
            )
            embed.set_thumbnail(url=user.display_avatar.url)
        
        # 記錄操作
        logger.info(f"開發者 {interaction.user} 移除了開發者 ID: {user_id}")
        
        # 發送回應
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(
        name="list_developers",
        description="列出所有開發者 (僅限開發者和管理員使用)"
    )
    async def list_developers(self, interaction: discord.Interaction):
        """列出所有開發者"""
        # 檢查權限 (開發者或管理員)
        if not (self._check_dev_permission(interaction.user.id, interaction.guild.id) or 
                interaction.user.guild_permissions.administrator):
            await interaction.response.send_message("❌ 此指令僅限開發者或管理員使用！", ephemeral=True)
            return
            
        # 創建嵌入消息
        embed = discord.Embed(
            title="👑 開發者列表",
            description=f"共有 {len(self.developer_ids)} 位開發者",
            color=discord.Color.gold()
        )
        
        # 獲取所有開發者資訊
        developer_info = []
        for dev_id in self.developer_ids:
            info = f"• ID: {dev_id}"
            
            # 嘗試獲取用戶資訊
            user = None
            for guild in self.bot.guilds:
                user = guild.get_member(int(dev_id))
                if user:
                    break
                    
            if user:
                info = f"• {user.name} ({dev_id})"
                
            developer_info.append(info)
            
        if developer_info:
            embed.add_field(
                name="📋 開發者",
                value="\n".join(developer_info),
                inline=False
            )
        else:
            embed.add_field(
                name="📋 開發者",
                value="目前沒有已註冊的開發者",
                inline=False
            )
            
        # 開發者模式狀態
        embed.add_field(
            name="⚙️ 開發者模式",
            value=f"當前狀態: {'已啟用' if self.dev_mode_enabled else '已禁用'}\n"
                  f"啟用的伺服器數: {len(self.dev_mode_guilds)}",
            inline=False
        )
        
        # 發送回應
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @app_commands.command(
        name="dev_debug",
        description="執行開發者偵錯動作 (僅限開發者使用)"
    )
    @app_commands.describe(
        action="要執行的偵錯動作",
        target="目標 (根據動作不同而變)",
        value="數值 (根據動作不同而變)"
    )
    async def dev_debug(
        self,
        interaction: discord.Interaction,
        action: str,
        target: str = None,
        value: str = None
    ):
        """開發者偵錯工具"""
        # 檢查開發者權限
        if not self._check_dev_permission(interaction.user.id, interaction.guild.id):
            await interaction.response.send_message("❌ 此指令僅限開發者使用！", ephemeral=True)
            return
            
        # 延遲回應，因為某些操作可能需要時間
        await interaction.response.defer(ephemeral=True)
        
        # 根據不同的偵錯動作執行相應的操作
        action = action.lower()
        result_msg = ""
        
        if action == "info":
            # 顯示系統信息
            result_msg = (
                f"**系統資訊**\n"
                f"Python 版本: {sys.version.split()[0]}\n"
                f"Discord.py 版本: {discord.__version__}\n"
                f"模型: {self.current_model_name}\n"
                f"對話歷史數: {len(self.chat_history)}\n"
                f"開發者數量: {len(self.developer_ids)}\n"
                f"開發者模式: {'啟用' if self.dev_mode_enabled else '禁用'}\n"
                f"API請求數: {len(self.request_times)}/分鐘\n"
                f"配額狀態: {'受限' if self.quota_exceeded else '正常'}\n"
            )
            
        elif action == "reset_all":
            # 重置所有數據
            self.chat_history.clear()
            self.quota_exceeded = False
            self.quota_reset_time = 0
            self.request_times.clear()
            self.cooldown_users.clear()
            
            if not self._is_developer(interaction.user.id):
                # 如果不是直接開發者，只重置數據，不重置開發者模式
                result_msg = "✅ 已重置所有使用數據 (對話歷史、配額狀態、用戶冷卻時間)"
            else:
                # 如果是直接開發者，同時重置開發者模式
                self.dev_mode_enabled = True  # 重置後仍保持開發者模式啟用
                self.dev_mode_guilds.clear()
                result_msg = "✅ 已重置所有系統數據 (包括對話歷史、配額狀態、開發者模式設置)"
                
        elif action == "test_response":
            # 測試API回應
            try:
                test_response = await asyncio.to_thread(
                    lambda: self.model.generate_content("測試回應，請回覆「API工作正常」").text
                )
                result_msg = f"API測試結果: {test_response}"
            except Exception as e:
                result_msg = f"❌ API測試失敗: {str(e)}"
                
        elif action == "toggle_logs" and self._is_developer(interaction.user.id):
            # 切換日誌等級 (僅適用於直接開發者)
            log_level = logging.getLogger().level
            if log_level == logging.INFO:
                logging.getLogger().setLevel(logging.DEBUG)
                result_msg = "✅ 已將日誌等級設為 DEBUG"
            else:
                logging.getLogger().setLevel(logging.INFO)
                result_msg = "✅ 已將日誌等級設為 INFO"
                
        elif action == "set_limit" and target and value and self._is_developer(interaction.user.id):
            # 設置各種限制 (僅適用於直接開發者)
            try:
                if target == "rate":
                    self.max_requests_per_minute = int(value)
                    result_msg = f"✅ 已將API速率限制設為每分鐘 {value} 個請求"
                elif target == "cooldown":
                    default_cooldown = int(value)
                    result_msg = f"✅ 已將預設用戶冷卻時間設為 {value} 秒"
                else:
                    result_msg = "❌ 未知的目標參數，可用選項: rate, cooldown"
            except ValueError:
                result_msg = "❌ 數值必須為整數"
        else:
            result_msg = "❌ 未知的偵錯動作或無足夠權限執行此動作"
        
        # 記錄操作
        logger.info(f"開發者 {interaction.user} 執行了偵錯操作: {action} {target} {value}")
        
        # 發送偵錯結果
        await interaction.followup.send(result_msg, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ChatCommands(bot))