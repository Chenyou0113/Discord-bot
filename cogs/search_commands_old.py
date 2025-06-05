import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import logging
import json
import asyncio
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
import urllib.parse
from datetime import datetime
import google.generativeai as genai

load_dotenv()
logger = logging.getLogger(__name__)

class SearchCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = None
        
        # Google Custom Search API 設定
        self.google_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        # Google Gemini AI 設定
        self.gemini_api_key = os.getenv('GOOGLE_API_KEY')
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        else:
            self.gemini_model = None
        
        # 速率限制設定
        self.search_cooldowns = {}  # 用戶冷卻時間
        self.cooldown_time = 10  # 10秒冷卻時間
        self.max_daily_searches = 50  # 每日搜尋限制
        self.daily_search_count = {}  # 每日搜尋計數
        
        # 管理員權限檢查
        self.admin_user_ids = [
            # 在這裡添加管理員的 Discord ID
            # 例如: 123456789012345678,
        ]
        
        # 初始化 aiohttp session
        self.bot.loop.create_task(self.init_aiohttp_session())
        
    async def init_aiohttp_session(self):
        """初始化 aiohttp 工作階段"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("SearchCommands: aiohttp session 已初始化")
    
    async def cog_unload(self):
        """當Cog被卸載時關閉aiohttp工作階段"""
        if self.session:
            await self.session.close()
            logger.info("SearchCommands: aiohttp session 已關閉")
    
    def _check_admin_permission(self, user_id: int, guild_id: int = None) -> bool:
        """檢查用戶是否為管理員或開發者"""
        # 檢查是否為預設管理員
        if user_id in self.admin_user_ids:
            return True
        
        # 檢查是否為伺服器管理員
        if guild_id:
            guild = self.bot.get_guild(guild_id)
            if guild:
                member = guild.get_member(user_id)
                if member and member.guild_permissions.administrator:
                    return True
        
        return False
    
    def _check_user_cooldown(self, user_id: int) -> bool:
        """檢查用戶是否在冷卻時間內"""
        current_time = datetime.now().timestamp()
        if user_id in self.search_cooldowns:
            time_diff = current_time - self.search_cooldowns[user_id]
            if time_diff < self.cooldown_time:
                return False
        return True
    
    def _set_user_cooldown(self, user_id: int):
        """設定用戶冷卻時間"""
        self.search_cooldowns[user_id] = datetime.now().timestamp()
    
    def _check_daily_limit(self, user_id: int) -> bool:
        """檢查用戶是否超過每日搜尋限制"""
        today = datetime.now().strftime('%Y-%m-%d')
        user_key = f"{user_id}_{today}"
        
        if user_key not in self.daily_search_count:
            self.daily_search_count[user_key] = 0
        
        return self.daily_search_count[user_key] < self.max_daily_searches
    
    def _increment_daily_count(self, user_id: int):
        """增加用戶每日搜尋計數"""
        today = datetime.now().strftime('%Y-%m-%d')
        user_key = f"{user_id}_{today}"
        
        if user_key not in self.daily_search_count:
            self.daily_search_count[user_key] = 0
        
        self.daily_search_count[user_key] += 1
    
    async def _google_search(self, query: str, num_results: int = 5) -> Optional[Dict[str, Any]]:
        """使用 Google Custom Search API 進行搜尋"""
        if not self.google_api_key or not self.search_engine_id:
            logger.error("Google Search API 配置缺失")
            return None
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.google_api_key,
            'cx': self.search_engine_id,
            'q': query,
            'num': min(num_results, 10),  # Google API 最多返回10個結果
            'safe': 'active',  # 安全搜尋
            'lr': 'lang_zh-TW|lang_zh-CN|lang_en',  # 語言限制
        }
        
        try:
            if not self.session:
                await self.init_aiohttp_session()
            
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"Google Search API 錯誤: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Google Search API 請求失敗: {str(e)}")
            return None
    
    def _format_search_results(self, search_data: Dict[str, Any], query: str) -> discord.Embed:
        """格式化搜尋結果為 Discord Embed"""
        embed = discord.Embed(
            title=f"🔍 搜尋結果：{query}",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        if 'items' not in search_data or not search_data['items']:
            embed.description = "❌ 沒有找到相關結果"
            return embed
        
        # 搜尋統計資訊
        if 'searchInformation' in search_data:
            search_info = search_data['searchInformation']
            total_results = search_info.get('totalResults', '0')
            search_time = search_info.get('searchTime', '0')
            embed.add_field(
                name="📊 搜尋統計",
                value=f"約 {total_results} 個結果 (耗時 {search_time} 秒)",
                inline=False
            )
        
        # 顯示搜尋結果
        results = search_data['items'][:5]  # 最多顯示5個結果
        
        for i, item in enumerate(results, 1):
            title = item.get('title', '無標題')
            link = item.get('link', '')
            snippet = item.get('snippet', '無描述')
              # 限制標題和描述長度
            if len(title) > 60:
                title = title[:57] + "..."
            if len(snippet) > 150:
                snippet = snippet[:147] + "..."
            
            embed.add_field(
                name=f"{i}. {title}",
                value=f"{snippet}\n[🔗 點擊查看]({link})",
                inline=False
            )
        
        embed.set_footer(text="由 Google Custom Search 提供")
        return embed
    
    async def _generate_search_summary(self, search_data: Dict[str, Any], query: str) -> Optional[str]:
        """使用 Gemini AI 生成搜尋結果總結"""
        if not self.gemini_model:
            return None
            
        try:
            # 提取搜尋結果內容
            if 'items' not in search_data or not search_data['items']:
                return None
                
            results = search_data['items'][:3]  # 取前3個結果進行總結
            content_for_summary = []
            
            for item in results:
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                if title and snippet:
                    content_for_summary.append(f"標題: {title}\n內容: {snippet}")
            
            if not content_for_summary:
                return None
            
            # 建構提示詞
            prompt = f"""
            用戶搜尋了："{query}"
            
            以下是搜尋結果：
            {chr(10).join(content_for_summary)}
            
            請根據以上搜尋結果，用繁體中文提供一個簡潔而有用的總結（約100-200字）。
            總結應該：
            1. 直接回答用戶的搜尋問題
            2. 整合多個搜尋結果的關鍵資訊
            3. 提供實用的洞察或建議
            4. 保持客觀和準確
            
            請以自然的方式回答，不要提及「根據搜尋結果」等字眼。
            """
            
            # 調用 Gemini API
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.gemini_model.generate_content(prompt)
            )
            
            if response.text:
                return response.text.strip()
            else:
                return None
                  except Exception as e:
            logger.error(f"生成搜尋總結時發生錯誤: {str(e)}")
            return None
    
    @app_commands.command(name="search", description="在網路上搜尋資訊")
    @app_commands.describe(
        query="要搜尋的關鍵字或問題",
        num_results="結果數量 (1-5，預設為3)",
        with_summary="是否生成AI總結 (預設為否)"
    )
    async def search(
        self,
        interaction: discord.Interaction,
        query: str,
        num_results: int = 3,
        with_summary: bool = False
    ):
        """網路搜尋指令"""
        user_id = interaction.user.id
        
        # 檢查API配置
        if not self.google_api_key or not self.search_engine_id:
            embed = discord.Embed(
                title="❌ 搜尋功能不可用",
                description="搜尋功能尚未配置，請聯繫管理員設置 Google Custom Search API。",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 檢查用戶冷卻時間
        if not self._check_user_cooldown(user_id):
            remaining_time = self.cooldown_time - (datetime.now().timestamp() - self.search_cooldowns[user_id])
            embed = discord.Embed(
                title="⏰ 搜尋冷卻中",
                description=f"請等待 {remaining_time:.1f} 秒後再進行搜尋",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 檢查每日搜尋限制
        if not self._check_daily_limit(user_id):
            embed = discord.Embed(
                title="📊 達到每日搜尋限制",
                description=f"您今天已達到最大搜尋次數限制 ({self.max_daily_searches} 次)，請明天再試",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 驗證輸入參數
        if len(query.strip()) < 2:
            embed = discord.Embed(
                title="❌ 搜尋關鍵字太短",
                description="請輸入至少2個字元的搜尋關鍵字",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not 1 <= num_results <= 5:
            num_results = 3
        
        # 開始搜尋
        await interaction.response.defer()
        
        logger.info(f"用戶 {interaction.user} 搜尋: {query}")
        
        try:
            # 執行搜尋
            search_data = await self._google_search(query, num_results)
            
            if search_data is None:
                embed = discord.Embed(
                    title="❌ 搜尋失敗",
                    description="無法連接到搜尋服務，請稍後再試",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
              # 格式化搜尋結果
            result_embed = self._format_search_results(search_data, query)
            
            # 設定用戶冷卻時間和增加計數
            self._set_user_cooldown(user_id)
            self._increment_daily_count(user_id)
            
            # 發送搜尋結果
            await interaction.followup.send(embed=result_embed)
            
            # 如果要求生成總結，則生成並發送總結
            if with_summary and self.gemini_model:
                try:
                    summary = await self._generate_search_summary(search_data, query)
                    if summary:
                        summary_embed = discord.Embed(
                            title="🤖 AI 總結",
                            description=summary,
                            color=discord.Color.green(),
                            timestamp=datetime.now()
                        )
                        summary_embed.set_footer(text="由 Google Gemini AI 提供")
                        await interaction.followup.send(embed=summary_embed)
                    else:
                        await interaction.followup.send("❌ 無法生成總結，請稍後再試。", ephemeral=True)
                except Exception as e:
                    logger.error(f"生成總結時發生錯誤: {str(e)}")
                    await interaction.followup.send("❌ 總結生成失敗，但搜尋結果已顯示。", ephemeral=True)
            elif with_summary and not self.gemini_model:
                await interaction.followup.send("❌ AI 總結功能不可用，請聯繫管理員檢查 Gemini API 配置。", ephemeral=True)
            
        except Exception as e:
            logger.error(f"搜尋過程中發生錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 搜尋錯誤",
                description="處理搜尋請求時發生錯誤，請稍後再試",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="search_settings", description="查看或調整搜尋功能設定 (僅限管理員)")
    @app_commands.describe(
        action="要執行的動作",
        value="新的設定值"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="查看設定", value="view"),
        app_commands.Choice(name="設定冷卻時間", value="cooldown"),
        app_commands.Choice(name="設定每日限制", value="daily_limit"),
        app_commands.Choice(name="重置用戶統計", value="reset_stats")
    ])
    async def search_settings(
        self,
        interaction: discord.Interaction,
        action: str,
        value: int = None
    ):
        """搜尋功能設定管理"""
        user_id = interaction.user.id
        guild_id = interaction.guild.id if interaction.guild else None
        
        # 檢查管理員權限
        if not self._check_admin_permission(user_id, guild_id):
            embed = discord.Embed(
                title="❌ 權限不足",
                description="此指令僅限管理員使用",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="⚙️ 搜尋功能設定",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        if action == "view":
            # 查看當前設定
            embed.add_field(
                name="🕐 冷卻時間",
                value=f"{self.cooldown_time} 秒",
                inline=True
            )
            embed.add_field(
                name="📊 每日搜尋限制",
                value=f"{self.max_daily_searches} 次",
                inline=True
            )
            embed.add_field(
                name="📈 今日搜尋統計",
                value=f"{len([k for k in self.daily_search_count.keys() if datetime.now().strftime('%Y-%m-%d') in k])} 位用戶使用",
                inline=True
            )
            embed.add_field(
                name="🔧 API狀態",
                value="✅ 已配置" if (self.google_api_key and self.search_engine_id) else "❌ 未配置",
                inline=True
            )
            
        elif action == "cooldown" and value is not None:
            # 設定冷卻時間
            if 1 <= value <= 300:  # 1秒到5分鐘
                self.cooldown_time = value
                embed.description = f"✅ 冷卻時間已設定為 {value} 秒"
            else:
                embed.description = "❌ 冷卻時間必須介於 1-300 秒之間"
                embed.color = discord.Color.red()
                
        elif action == "daily_limit" and value is not None:
            # 設定每日限制
            if 1 <= value <= 1000:
                self.max_daily_searches = value
                embed.description = f"✅ 每日搜尋限制已設定為 {value} 次"
            else:
                embed.description = "❌ 每日限制必須介於 1-1000 次之間"
                embed.color = discord.Color.red()
                
        elif action == "reset_stats":
            # 重置統計資料
            self.search_cooldowns.clear()
            self.daily_search_count.clear()
            embed.description = "✅ 已重置所有用戶搜尋統計資料"
            
        else:
            embed.description = "❌ 無效的動作或缺少必要參數"
            embed.color = discord.Color.red()
        
        embed.set_footer(text=f"設定者: {interaction.user.name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="search_stats", description="查看個人搜尋統計")
    async def search_stats(self, interaction: discord.Interaction):
        """查看個人搜尋統計"""
        user_id = interaction.user.id
        today = datetime.now().strftime('%Y-%m-%d')
        user_key = f"{user_id}_{today}"
        
        # 獲取今日搜尋次數
        today_searches = self.daily_search_count.get(user_key, 0)
        remaining_searches = max(0, self.max_daily_searches - today_searches)
        
        # 檢查冷卻狀態
        cooldown_remaining = 0
        if user_id in self.search_cooldowns:
            time_diff = datetime.now().timestamp() - self.search_cooldowns[user_id]
            if time_diff < self.cooldown_time:
                cooldown_remaining = self.cooldown_time - time_diff
        
        embed = discord.Embed(
            title="📊 您的搜尋統計",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📈 今日使用情況",
            value=f"已使用: {today_searches}/{self.max_daily_searches} 次\n剩餘: {remaining_searches} 次",
            inline=True
        )
        
        embed.add_field(
            name="⏰ 冷卻狀態",
            value=f"{'✅ 可以搜尋' if cooldown_remaining <= 0 else f'⏳ 等待 {cooldown_remaining:.1f} 秒'}",
            inline=True
        )
        
        # 使用進度條顯示使用率
        usage_percentage = (today_searches / self.max_daily_searches) * 100
        progress_bar = "█" * int(usage_percentage / 10) + "░" * (10 - int(usage_percentage / 10))
        
        embed.add_field(
            name="📊 使用率",
            value=f"{progress_bar} {usage_percentage:.1f}%",
            inline=False
        )
        
        embed.set_footer(text="使用 /search 指令進行網路搜尋")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="search_summarize", description="搜尋並生成AI總結")
    @app_commands.describe(
        query="要搜尋並總結的關鍵字或問題",
        num_results="用於總結的搜尋結果數量 (1-5，預設為3)"
    )
    async def search_summarize(
        self,
        interaction: discord.Interaction,
        query: str,
        num_results: int = 3
    ):
        """搜尋並生成AI總結指令"""
        user_id = interaction.user.id
        
        # 檢查API配置
        if not self.google_api_key or not self.search_engine_id:
            embed = discord.Embed(
                title="❌ 搜尋功能不可用",
                description="搜尋功能尚未配置，請聯繫管理員設置 Google Custom Search API。",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        if not self.gemini_model:
            embed = discord.Embed(
                title="❌ AI 總結功能不可用",
                description="AI 總結功能尚未配置，請聯繫管理員檢查 Gemini API 配置。",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 檢查用戶冷卻時間
        if not self._check_user_cooldown(user_id):
            remaining_time = self.cooldown_time - (datetime.now().timestamp() - self.search_cooldowns[user_id])
            embed = discord.Embed(
                title="⏰ 搜尋冷卻中",
                description=f"請等待 {remaining_time:.1f} 秒後再進行搜尋",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 檢查每日搜尋限制
        if not self._check_daily_limit(user_id):
            embed = discord.Embed(
                title="📊 達到每日搜尋限制",
                description=f"您今天已達到最大搜尋次數限制 ({self.max_daily_searches} 次)，請明天再試",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 驗證輸入參數
        if len(query.strip()) < 2:
            embed = discord.Embed(
                title="❌ 搜尋關鍵字太短",
                description="請輸入至少2個字元的搜尋關鍵字",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not 1 <= num_results <= 5:
            num_results = 3
        
        # 開始搜尋和總結
        await interaction.response.defer()
        
        logger.info(f"用戶 {interaction.user} 請求總結: {query}")
        
        try:
            # 執行搜尋
            search_data = await self._google_search(query, num_results)
            
            if search_data is None:
                embed = discord.Embed(
                    title="❌ 搜尋失敗",
                    description="無法連接到搜尋服務，請稍後再試",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 檢查是否有搜尋結果
            if 'items' not in search_data or not search_data['items']:
                embed = discord.Embed(
                    title="❌ 沒有找到相關結果",
                    description=f"關於「{query}」沒有找到足夠的資訊來生成總結",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 設定用戶冷卻時間和增加計數
            self._set_user_cooldown(user_id)
            self._increment_daily_count(user_id)
            
            # 生成AI總結
            summary = await self._generate_search_summary(search_data, query)
            
            if summary:
                # 創建總結 Embed
                summary_embed = discord.Embed(
                    title=f"🤖 AI 總結：{query}",
                    description=summary,
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                
                # 添加搜尋統計資訊
                if 'searchInformation' in search_data:
                    search_info = search_data['searchInformation']
                    total_results = search_info.get('totalResults', '0')
                    summary_embed.add_field(
                        name="📊 資料來源",
                        value=f"基於約 {total_results} 個搜尋結果的前 {len(search_data['items'])} 個結果",
                        inline=False
                    )
                
                summary_embed.set_footer(text="由 Google Search + Gemini AI 提供")
                await interaction.followup.send(embed=summary_embed)
                
                # 可選：同時提供詳細搜尋結果的按鈕
                view = discord.ui.View()
                button = discord.ui.Button(
                    label="📄 查看詳細搜尋結果",
                    style=discord.ButtonStyle.secondary,
                    custom_id=f"detailed_search_{user_id}_{int(datetime.now().timestamp())}"
                )
                
                async def show_details(button_interaction):
                    if button_interaction.user.id != user_id:
                        await button_interaction.response.send_message("❌ 只有原始搜尋者可以查看詳細結果", ephemeral=True)
                        return
                    
                    result_embed = self._format_search_results(search_data, query)
                    await button_interaction.response.send_message(embed=result_embed, ephemeral=True)
                
                button.callback = show_details
                view.add_item(button)
                
                await interaction.followup.send("💡 需要更詳細的搜尋結果嗎？", view=view, ephemeral=True)
            else:
                embed = discord.Embed(
                    title="❌ 總結生成失敗",
                    description="無法生成總結，但您可以使用 `/search` 指令查看原始搜尋結果",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"搜尋總結過程中發生錯誤: {str(e)}")
            embed = discord.Embed(
                title="❌ 總結錯誤",
                description="處理總結請求時發生錯誤，請稍後再試",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(SearchCommands(bot))
