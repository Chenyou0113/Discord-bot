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
from datetime import datetime, timedelta
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
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
          # 速率限制設定
        self.search_cooldowns = {}  # 用戶冷卻時間
        self.cooldown_time = 10  # 10秒冷卻時間
        self.max_daily_searches = 50  # 每日搜尋限制
        self.daily_search_count = {}  # 每日搜尋計數
        
        # 自動搜尋設定
        self.auto_search_enabled = {}  # 每個伺服器的自動搜尋開關 {guild_id: bool}
        self.auto_search_keywords = ["搜尋", "搜索", "查找"]  # 觸發關鍵字
        
        # 管理員權限檢查
        self.admin_user_ids = [
            # 在這裡添加管理員的 Discord ID
            # 例如: 123456789012345678,
        ]
        
        # 初始化 aiohttp session
        asyncio.create_task(self.init_aiohttp_session())
        
    async def init_aiohttp_session(self):
        """初始化 aiohttp 工作階段"""
        try:
            self.session = aiohttp.ClientSession()
            logger.info("Search commands aiohttp session initialized")
        except Exception as e:
            logger.error(f"Failed to initialize aiohttp session: {e}")
    
    async def cog_unload(self):
        """清理資源"""
        if self.session:
            await self.session.close()
    
    def _is_admin(self, user_id: int) -> bool:
        """檢查用戶是否為管理員"""
        return user_id in self.admin_user_ids or len(self.admin_user_ids) == 0
    
    def _check_cooldown(self, user_id: int) -> Optional[int]:
        """檢查用戶冷卻時間"""
        now = datetime.now()
        if user_id in self.search_cooldowns:
            time_diff = (now - self.search_cooldowns[user_id]).total_seconds()
            if time_diff < self.cooldown_time:
                return int(self.cooldown_time - time_diff)
        return None
    
    def _update_cooldown(self, user_id: int):
        """更新用戶冷卻時間"""
        self.search_cooldowns[user_id] = datetime.now()
    
    def _check_daily_limit(self, user_id: int) -> bool:
        """檢查用戶每日搜尋限制"""
        today = datetime.now().date()
        if user_id not in self.daily_search_count:
            self.daily_search_count[user_id] = {}
        
        if today not in self.daily_search_count[user_id]:
            self.daily_search_count[user_id][today] = 0
        
        return self.daily_search_count[user_id][today] < self.max_daily_searches
    
    def _increment_daily_count(self, user_id: int):
        """增加用戶每日搜尋計數"""
        today = datetime.now().date()
        if user_id not in self.daily_search_count:
            self.daily_search_count[user_id] = {}
        
        if today not in self.daily_search_count[user_id]:
            self.daily_search_count[user_id][today] = 0
        
        self.daily_search_count[user_id][today] += 1
    
    async def _google_search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """執行 Google 自定義搜尋"""
        if not self.google_api_key or not self.search_engine_id:
            return {"error": "Google Search API 未配置"}
        
        if not self.session:
            await self.init_aiohttp_session()
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": min(num_results, 10),  # 限制最多10個結果
            "safe": "active"  # 啟用安全搜尋
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"Google Search API error: {response.status} - {error_text}")
                    return {"error": f"搜尋失敗 (HTTP {response.status})"}
        except Exception as e:
            logger.error(f"Google Search error: {e}")
            return {"error": f"搜尋過程中發生錯誤: {str(e)}"}
    
    async def _generate_search_summary(self, search_results: List[Dict], query: str) -> str:
        """使用 AI 生成搜尋結果的總結"""
        if not self.gemini_model:
            return "AI 總結功能暫時無法使用（API 未配置）"
        
        # 準備搜尋結果文本
        results_text = f"搜尋查詢: {query}\n\n搜尋結果:\n"
        for i, item in enumerate(search_results[:5], 1):
            title = item.get('title', '無標題')
            snippet = item.get('snippet', '無摘要')
            link = item.get('link', '無連結')
            results_text += f"{i}. 標題: {title}\n摘要: {snippet}\n連結: {link}\n\n"
        
        # 建立 AI 提示
        prompt = f"""
請基於以下搜尋結果，為用戶提供一個簡潔且有用的總結。請用繁體中文回答。

{results_text}

請提供:
1. 主要重點的簡要總結
2. 關鍵資訊整理
3. 如果適用，提供建議或結論

總結應該在300字以內，並且要準確反映搜尋結果的內容。
"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"AI summary generation error: {e}")
            return f"生成總結時發生錯誤: {str(e)}"
    
    def _format_search_results(self, data: Dict[str, Any], with_summary: bool = False) -> discord.Embed:
        """格式化搜尋結果為 Discord Embed"""
        if "error" in data:
            embed = discord.Embed(
                title="❌ 搜尋錯誤",
                description=data["error"],
                color=discord.Color.red()
            )
            return embed
        
        items = data.get("items", [])
        if not items:
            embed = discord.Embed(
                title="🔍 搜尋結果",
                description="未找到相關結果",
                color=discord.Color.orange()
            )
            return embed
        
        # 取得搜尋資訊
        search_info = data.get("searchInformation", {})
        total_results = search_info.get("totalResults", "未知")
        search_time = search_info.get("searchTime", "未知")
        
        embed = discord.Embed(
            title="🔍 搜尋結果",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📊 搜尋統計",
            value=f"總計: {total_results} 個結果\n時間: {search_time} 秒",
            inline=False
        )
        
        # 添加搜尋結果
        for i, item in enumerate(items[:5], 1):
            title = item.get("title", "無標題")
            snippet = item.get("snippet", "無摘要")
            link = item.get("link", "")
            
            # 限制標題和摘要長度
            if len(title) > 100:
                title = title[:97] + "..."
            if len(snippet) > 200:
                snippet = snippet[:197] + "..."
            
            embed.add_field(
                name=f"{i}. {title}",
                value=f"{snippet}\n[🔗 查看完整內容]({link})",
                inline=False
            )
        
        embed.set_footer(text="💡 使用 /search_summarize 獲取 AI 總結")
        return embed
    
    @app_commands.command(name="search", description="使用 Google 搜尋網路內容")
    @app_commands.describe(
        query="要搜尋的關鍵字",
        results="結果數量 (1-10，預設 5)",
        with_summary="是否包含 AI 總結"
    )
    async def search(
        self, 
        interaction: discord.Interaction, 
        query: str, 
        results: Optional[int] = 5,
        with_summary: Optional[bool] = False
    ):
        """執行網路搜尋"""
        user_id = interaction.user.id
        
        # 檢查冷卻時間
        cooldown = self._check_cooldown(user_id)
        if cooldown and not self._is_admin(user_id):
            embed = discord.Embed(
                title="⏰ 冷卻中",
                description=f"請等待 {cooldown} 秒後再次搜尋",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 檢查每日限制
        if not self._check_daily_limit(user_id) and not self._is_admin(user_id):
            embed = discord.Embed(
                title="📈 達到每日限制",
                description=f"您今天已達到搜尋限制 ({self.max_daily_searches} 次)",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 驗證參數
        if not query.strip():
            embed = discord.Embed(
                title="❌ 錯誤",
                description="請提供搜尋關鍵字",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        results = max(1, min(results or 5, 10))
        
        await interaction.response.defer()
        
        try:
            # 執行搜尋
            search_data = await self._google_search(query, results)
            
            if "error" not in search_data:
                # 更新限制
                self._update_cooldown(user_id)
                self._increment_daily_count(user_id)
            
            # 格式化結果
            embed = self._format_search_results(search_data, with_summary)
            
            # 如果需要 AI 總結
            if with_summary and "error" not in search_data and search_data.get("items"):
                try:
                    summary = await self._generate_search_summary(search_data["items"], query)
                    embed.add_field(
                        name="🤖 AI 總結",
                        value=summary[:1000] + ("..." if len(summary) > 1000 else ""),
                        inline=False
                    )
                except Exception as e:
                    logger.error(f"Summary generation failed: {e}")
                    embed.add_field(
                        name="🤖 AI 總結",
                        value="總結生成失敗",
                        inline=False
                    )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Search command error: {e}")
            embed = discord.Embed(
                title="❌ 錯誤",
                description=f"搜尋過程中發生錯誤: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="search_summarize", description="對搜尋結果進行 AI 總結")
    @app_commands.describe(query="要搜尋並總結的關鍵字")
    async def search_summarize(self, interaction: discord.Interaction, query: str):
        """搜尋並提供 AI 總結"""
        user_id = interaction.user.id
        
        # 檢查冷卻時間
        cooldown = self._check_cooldown(user_id)
        if cooldown and not self._is_admin(user_id):
            embed = discord.Embed(
                title="⏰ 冷卻中",
                description=f"請等待 {cooldown} 秒後再次搜尋",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 檢查每日限制
        if not self._check_daily_limit(user_id) and not self._is_admin(user_id):
            embed = discord.Embed(
                title="📈 達到每日限制",
                description=f"您今天已達到搜尋限制 ({self.max_daily_searches} 次)",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not query.strip():
            embed = discord.Embed(
                title="❌ 錯誤",
                description="請提供搜尋關鍵字",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            # 執行搜尋
            search_data = await self._google_search(query, 5)
            
            if "error" in search_data:
                embed = discord.Embed(
                    title="❌ 搜尋錯誤",
                    description=search_data["error"],
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            items = search_data.get("items", [])
            if not items:
                embed = discord.Embed(
                    title="🔍 搜尋結果",
                    description="未找到相關結果",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 更新限制
            self._update_cooldown(user_id)
            self._increment_daily_count(user_id)
            
            # 生成 AI 總結
            summary = await self._generate_search_summary(items, query)
            
            embed = discord.Embed(
                title="🤖 AI 搜尋總結",
                description=f"**搜尋查詢:** {query}",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📝 總結內容",
                value=summary[:2000] + ("..." if len(summary) > 2000 else ""),
                inline=False
            )
            
            # 添加參考資料
            references = ""
            for i, item in enumerate(items[:3], 1):
                title = item.get("title", "無標題")
                link = item.get("link", "")
                if len(title) > 50:
                    title = title[:47] + "..."
                references += f"{i}. [🔗 {title}]({link})\n"
            
            if references:
                embed.add_field(
                    name="📚 參考資料",
                    value=references,
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Search summarize error: {e}")
            embed = discord.Embed(
                title="❌ 錯誤",
                description=f"總結過程中發生錯誤: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="search_settings", description="查看或修改搜尋設定 (管理員限定)")
    @app_commands.describe(
        max_daily="設定每日搜尋限制",
        cooldown="設定冷卻時間 (秒)"
    )
    async def search_settings(
        self, 
        interaction: discord.Interaction,
        max_daily: Optional[int] = None,
        cooldown: Optional[int] = None
    ):
        """管理搜尋設定"""
        if not self._is_admin(interaction.user.id):
            embed = discord.Embed(
                title="❌ 權限不足",
                description="此指令僅限管理員使用",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # 更新設定
        updated = []
        if max_daily is not None:
            if 1 <= max_daily <= 1000:
                self.max_daily_searches = max_daily
                updated.append(f"每日搜尋限制: {max_daily}")
            else:
                embed = discord.Embed(
                    title="❌ 錯誤",
                    description="每日搜尋限制必須在 1-1000 之間",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        if cooldown is not None:
            if 1 <= cooldown <= 300:
                self.cooldown_time = cooldown
                updated.append(f"冷卻時間: {cooldown} 秒")
            else:
                embed = discord.Embed(
                    title="❌ 錯誤",
                    description="冷卻時間必須在 1-300 秒之間",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # 顯示目前設定
        embed = discord.Embed(
            title="⚙️ 搜尋設定",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📊 目前設定",
            value=f"每日搜尋限制: {self.max_daily_searches}\n冷卻時間: {self.cooldown_time} 秒",
            inline=False
        )
        
        if updated:
            embed.add_field(
                name="✅ 已更新",
                value="\n".join(updated),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="search_stats", description="查看搜尋統計")
    async def search_stats(self, interaction: discord.Interaction):
        """顯示搜尋統計資訊"""
        user_id = interaction.user.id
        today = datetime.now().date()
        
        # 獲取用戶今日搜尋次數
        user_searches_today = 0
        if user_id in self.daily_search_count and today in self.daily_search_count[user_id]:
            user_searches_today = self.daily_search_count[user_id][today]
        
        # 檢查冷卻狀態
        cooldown_remaining = self._check_cooldown(user_id)
        
        embed = discord.Embed(
            title="📊 搜尋統計",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="👤 您的統計",
            value=f"今日搜尋: {user_searches_today}/{self.max_daily_searches}\n剩餘次數: {self.max_daily_searches - user_searches_today}",
            inline=False
        )
        
        if cooldown_remaining:
            embed.add_field(
                name="⏰ 冷卻狀態",
                value=f"請等待 {cooldown_remaining} 秒",
                inline=False
            )
        else:
            embed.add_field(
                name="✅ 可用狀態",
                value="您可以立即進行搜尋",
                inline=False        )
        
        embed.add_field(
            name="⚙️ 系統設定",
            value=f"每日限制: {self.max_daily_searches} 次\n冷卻時間: {self.cooldown_time} 秒",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """監聽訊息中的搜尋關鍵字並自動執行搜尋"""
        # 忽略機器人自己的訊息
        if message.author == self.bot.user:
            return
            
        # 忽略私人訊息
        if not message.guild:
            return
            
        # 檢查該伺服器是否啟用自動搜尋
        guild_id = message.guild.id
        if not self.auto_search_enabled.get(guild_id, False):
            return
        
        # 檢查訊息是否包含搜尋關鍵字
        message_lower = message.content.lower()
        triggered_keyword = None
        
        for keyword in self.auto_search_keywords:
            if keyword in message_lower:
                triggered_keyword = keyword
                break
                
        if not triggered_keyword:
            return
            
        user_id = message.author.id
        
        # 檢查冷卻時間
        cooldown = self._check_cooldown(user_id)
        if cooldown and not self._is_admin(user_id):
            await message.add_reaction("⏰")  # 使用反應而不是回覆，避免干擾
            return
        
        # 檢查每日限制
        if not self._check_daily_limit(user_id) and not self._is_admin(user_id):
            await message.add_reaction("📈")  # 使用反應表示達到限制
            return
        
        try:
            # 提取搜尋關鍵字
            content = message.content
            
            # 尋找搜尋關鍵字並提取查詢內容
            query = ""
            for pattern in self.auto_search_keywords:
                if pattern in content:
                    # 嘗試不同的提取方式
                    parts = content.split(pattern, 1)
                    if len(parts) > 1:
                        potential_query = parts[1].strip()
                        # 檢查是否有實際內容
                        if potential_query and len(potential_query) > 1:
                            query = potential_query
                            break
            
            # 如果沒有找到明確查詢，嘗試其他方式
            if not query:
                # 移除觸發關鍵字後的內容
                query = content
                for keyword in self.auto_search_keywords:
                    query = query.replace(keyword, "").strip()
            
            # 清理查詢字串
            query = query.strip("，。！？；：\"'()（）[]【】{}").strip()
            
            # 檢查查詢有效性
            if not query or len(query.strip()) < 2:
                await message.add_reaction("❓")  # 表示需要更明確的搜尋內容
                return
            
            # 限制查詢長度
            if len(query) > 100:
                query = query[:100] + "..."
            
            # 添加搜尋反應表示正在處理
            await message.add_reaction("🔍")
            
            async with message.channel.typing():
                # 執行搜尋
                search_data = await self._google_search(query, 3)  # 自動搜尋時只顯示 3 個結果
                
                if "error" not in search_data:
                    # 更新限制
                    self._update_cooldown(user_id)
                    self._increment_daily_count(user_id)
                    
                    # 移除搜尋反應，添加完成反應
                    await message.remove_reaction("🔍", self.bot.user)
                    await message.add_reaction("✅")
                else:
                    # 搜尋失敗
                    await message.remove_reaction("🔍", self.bot.user)
                    await message.add_reaction("❌")
                
                # 格式化結果
                embed = self._format_search_results(search_data, False)
                
                # 添加自動搜尋標記
                embed.set_footer(
                    text=f"🤖 自動搜尋 | 關鍵字: {query} | 觸發詞: {triggered_keyword}",
                    icon_url=message.author.display_avatar.url
                )
                
                # 回覆原訊息
                await message.reply(embed=embed)
                
        except Exception as e:
            logger.error(f"Auto search error: {e}")
            try:
                await message.remove_reaction("🔍", self.bot.user)
                await message.add_reaction("❌")
            except:
                pass

    @app_commands.command(name="auto_search", description="管理自動搜尋功能設定 (管理員限定)")
    @app_commands.describe(
        enable="是否啟用自動搜尋功能",
        keywords="設定觸發關鍵字（用逗號分隔）"
    )
    async def auto_search_settings(
        self, 
        interaction: discord.Interaction,
        enable: Optional[bool] = None,
        keywords: Optional[str] = None
    ):
        """管理自動搜尋功能設定"""
        # 檢查權限 - 需要管理員權限或Bot管理員
        if not (self._is_admin(interaction.user.id) or 
                interaction.user.guild_permissions.manage_guild):
            embed = discord.Embed(
                title="❌ 權限不足",
                description="此指令需要伺服器管理權限或Bot管理員權限",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_id = interaction.guild.id
        current_status = self.auto_search_enabled.get(guild_id, False)
        current_keywords = self.auto_search_keywords.copy()
        
        updated = []
        
        # 更新啟用狀態
        if enable is not None:
            self.auto_search_enabled[guild_id] = enable
            status_text = "啟用" if enable else "停用"
            updated.append(f"自動搜尋功能: {status_text}")
        
        # 更新關鍵字
        if keywords is not None:
            keyword_list = [kw.strip() for kw in keywords.split(",") if kw.strip()]
            if keyword_list:
                self.auto_search_keywords = keyword_list
                updated.append(f"觸發關鍵字: {', '.join(keyword_list)}")
            else:
                embed = discord.Embed(
                    title="❌ 錯誤",
                    description="請提供至少一個有效的觸發關鍵字",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # 顯示設定結果
        embed = discord.Embed(
            title="🔧 自動搜尋功能設定",
            color=discord.Color.blue()
        )
        
        current_status = self.auto_search_enabled.get(guild_id, False)
        status_emoji = "✅" if current_status else "❌"
        
        embed.add_field(
            name="📊 目前狀態",
            value=f"{status_emoji} 自動搜尋: {'啟用' if current_status else '停用'}\n"
                  f"🔑 觸發關鍵字: {', '.join(self.auto_search_keywords)}",
            inline=False
        )
        
        if updated:
            embed.add_field(
                name="✅ 已更新",
                value="\n".join(updated),
                inline=False
            )
        
        embed.add_field(
            name="ℹ️ 使用說明",
            value="• 當用戶訊息包含觸發關鍵字時，Bot會自動執行搜尋\n"
                  "• 自動搜尋仍受冷卻時間和每日限制約束\n"
                  "• 使用表情符號反應來減少對話干擾\n"
                  "• 僅在啟用的伺服器中生效",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
async def setup(bot):
    await bot.add_cog(SearchCommands(bot))
