import discord
from discord import app_commands
from discord.ext import commands
import datetime
import aiohttp
import xmltodict
import logging
import asyncio
from typing import Optional, Dict, Any, List
import urllib3
from discord.ui import Select, View

logger = logging.getLogger(__name__)

# 台灣縣市列表
TW_LOCATIONS = [
    "基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣", "苗栗縣",
    "臺中市", "彰化縣", "南投縣", "雲林縣", "嘉義市", "嘉義縣", "臺南市",
    "高雄市", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"
]

# 縣市分區
TW_REGIONS = {
    "北部": ["基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣", "宜蘭縣"],
    "中部": ["苗栗縣", "臺中市", "彰化縣", "南投縣", "雲林縣"],
    "南部": ["嘉義市", "嘉義縣", "臺南市", "高雄市", "屏東縣"],
    "東部": ["花蓮縣", "臺東縣"],
    "離島": ["澎湖縣", "金門縣", "連江縣"]
}

class WeatherSelectView(View):
    def __init__(self, cog):
        super().__init__(timeout=120)  # 設定選單超時時間為120秒
        self.cog = cog
        self.add_item(self.create_select_menu())

    def create_select_menu(self):
        select = Select(
            placeholder="請選擇縣市...",
            min_values=1,
            max_values=1
        )
        
        # 依照區域分組添加選項
        for region, cities in TW_REGIONS.items():
            for city in cities:
                select.add_option(
                    label=city,
                    value=city,
                    description=f"{region}地區",
                    emoji="🌆" if city.endswith("市") else "🏞️"
                )
        
        select.callback = self.select_callback
        return select

    async def select_callback(self, interaction: discord.Interaction):
        """處理縣市選擇後的回調函數"""
        selected_city = interaction.data["values"][0]
        
        try:
            await interaction.response.defer(ephemeral=False, thinking=True)
            
            # 獲取天氣資料
            try:
                async with asyncio.timeout(5):  # 設定5秒超時
                    data = await self.cog.fetch_weather_data()
            except asyncio.TimeoutError:
                # 如果超時，檢查快取
                data = self.cog.weather_cache
                
                if not data:
                    await interaction.followup.send(
                        embed=discord.Embed(
                            title="⚠️ 處理超時",
                            description="獲取天氣資料時發生延遲，請稍後再試",
                            color=discord.Color.orange()
                        )
                    )
                    return
            
            if not data:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="❌ 錯誤",
                        description="無法獲取天氣資料，請稍後再試",
                        color=discord.Color.red()
                    )
                )
                return
            
            # 格式化並發送天氣資料
            embed = self.cog.format_weather_data(data, selected_city)
            await interaction.followup.send(embed=embed)
            logger.info(f"用戶 {interaction.user} 查詢了 {selected_city} 的天氣預報")
            
        except Exception as e:
            logger.error(f"處理天氣查詢選擇時發生錯誤: {str(e)}")
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ 錯誤",
                    description="處理選擇時發生錯誤，請稍後再試",
                    color=discord.Color.red()
                )
            )
            
    async def on_timeout(self):
        """處理選單逾時"""
        # 選單逾時時，禁用所有選項
        for item in self.children:
            item.disabled = True

class ReservoirSelectView(View):
    def __init__(self, cog):
        super().__init__(timeout=120)  # 設定選單超時時間為120秒
        self.cog = cog
        self.add_item(self.create_select_menu())

    def create_select_menu(self):
        """創建水庫選擇選單"""
        select = Select(
            placeholder="選擇要查詢的水庫",
            min_values=1,
            max_values=1
        )

        reservoirs_by_region = {
            "北部": ["石門水庫", "寶山第二水庫", "永和山水庫", "寶山水庫", "德基水庫"],
            "中部": ["鯉魚潭水庫", "德基水庫", "霧社水庫", "日月潭水庫", "仁義潭水庫"],
            "南部": ["曾文水庫", "烏山頭水庫", "南化水庫", "阿公店水庫", "牡丹水庫"]
        }
        
        added_reservoirs = set() # 用於追蹤已添加的水庫，確保唯一性
        
        try:
            # 計算總選項數量，確保不超過25個
            option_count = 0
            for region, reservoirs in reservoirs_by_region.items():
                for reservoir in reservoirs:
                    if option_count < 25 and reservoir not in added_reservoirs:  # 確保不超過25個選項且水庫未被添加過
                        select.add_option(
                            label=reservoir,
                            value=reservoir, # value 必須是唯一的
                            description=f"{region}地區",
                            emoji="💧"
                        )
                        added_reservoirs.add(reservoir) # 將已添加的水庫加入集合
                        option_count += 1
                    elif reservoir in added_reservoirs:
                        logger.info(f"水庫 '{reservoir}' 已存在於選單中，跳過重複添加。")
                    elif option_count >= 25:
                        logger.warning(f"已達選項上限，略過水庫: {reservoir}")
        except Exception as e:
            logger.error(f"建立水庫選單時發生錯誤: {str(e)}")
            # 發生錯誤時添加一個預設選項
            select.add_option(
                label="錯誤",
                value="error_loading_reservoirs", # 確保錯誤選項的 value 也唯一
                description="無法載入水庫選項",
                emoji="⚠️"
            )
        
        select.callback = self.select_callback
        return select

    async def select_callback(self, interaction: discord.Interaction):
        """處理水庫選擇後的回調函數"""
        selected_reservoir = interaction.data["values"][0]
        
        try:
            await interaction.response.defer(ephemeral=False, thinking=True)
            
            # 獲取水庫資料
            try:
                async with asyncio.timeout(5):  # 設定5秒超時
                    data = await self.cog.fetch_reservoir_data()
            except asyncio.TimeoutError:
                # 如果超時，檢查快取
                data = self.cog.reservoir_cache
                
                if not data:
                    await interaction.followup.send(
                        embed=discord.Embed(
                            title="⚠️ 處理超時",
                            description="獲取水庫資料時發生延遲，請稍後再試",
                            color=discord.Color.orange()
                        )
                    )
                    return
            
            if not data:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="❌ 錯誤",
                        description="無法獲取水庫資料，請稍後再試",
                        color=discord.Color.red()
                    )
                )
                return
            
            # 格式化並發送水庫資料
            embed = self.cog.format_reservoir_data(data, selected_reservoir)
            await interaction.followup.send(embed=embed)
            logger.info(f"用戶 {interaction.user} 查詢了 {selected_reservoir} 的水庫情況")
            
        except Exception as e:
            logger.error(f"處理水庫查詢選擇時發生錯誤: {str(e)}")
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ 錯誤",
                    description="處理選擇時發生錯誤，請稍後再試",
                    color=discord.Color.red()
                )
            )
            
    async def on_timeout(self):
        """處理選單逾時"""
        # 選單逾時時，禁用所有選項
        for item in self.children:
            item.disabled = True

class WaterInfoSelectView(View):
    def __init__(self, cog):
        super().__init__(timeout=120)  # 設定選單超時時間為120秒
        self.cog = cog
        self.add_item(self.create_select_menu())

    def create_select_menu(self):
        """創建水庫選擇選單"""
        select = Select(
            placeholder="選擇要查詢的水庫",
            min_values=1,
            max_values=1
        )

        reservoirs_by_region = {
            "北部": ["石門水庫", "寶山第二水庫", "永和山水庫", "寶山水庫", "德基水庫"],
            "中部": ["鯉魚潭水庫", "德基水庫", "霧社水庫", "日月潭水庫", "仁義潭水庫"],
            "南部": ["曾文水庫", "烏山頭水庫", "南化水庫", "阿公店水庫", "牡丹水庫"]
        }
        
        added_reservoirs = set() # 用於追蹤已添加的水庫，確保唯一性
        
        try:
            # 計算總選項數量，確保不超過25個
            option_count = 0
            for region, reservoirs in reservoirs_by_region.items():
                for reservoir in reservoirs:
                    if option_count < 25 and reservoir not in added_reservoirs:  # 確保不超過25個選項且水庫未被添加過
                        select.add_option(
                            label=reservoir,
                            value=reservoir, # value 必須是唯一的
                            description=f"{region}地區",
                            emoji="💧"
                        )
                        added_reservoirs.add(reservoir) # 將已添加的水庫加入集合
                        option_count += 1
                    elif reservoir in added_reservoirs:
                        logger.info(f"水庫 '{reservoir}' 已存在於選單中，跳過重複添加。")
                    elif option_count >= 25:
                        logger.warning(f"已達選項上限，略過水庫: {reservoir}")
        except Exception as e:
            logger.error(f"建立水庫選單時發生錯誤: {str(e)}")
            # 發生錯誤時添加一個預設選項
            select.add_option(
                label="錯誤",
                value="error_loading_waterinfo", # 確保錯誤選項的 value 也唯一
                description="無法載入水庫選項",
                emoji="⚠️"
            )
        
        select.callback = self.select_callback
        return select

    async def select_callback(self, interaction: discord.Interaction):
        """處理水庫選擇後的回調函數"""
        selected_reservoir = interaction.data["values"][0]
        
        try:
            await interaction.response.defer(ephemeral=False, thinking=True)
            
            # 獲取水庫資料
            try:
                async with asyncio.timeout(5):  # 設定5秒超時
                    data = await self.cog.fetch_water_info_data()
            except asyncio.TimeoutError:
                # 如果超時，檢查快取
                data = self.cog.water_info_cache
                
                if not data:
                    await interaction.followup.send(
                        embed=discord.Embed(
                            title="⚠️ 處理超時",
                            description="獲取水情資料時發生延遲，請稍後再試",
                            color=discord.Color.orange()
                        )
                    )
                    return
            
            if not data:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="❌ 錯誤",
                        description="無法獲取水情資料，請稍後再試",
                        color=discord.Color.red()
                    )
                )
                return
            
            # 格式化並發送水庫資料
            embed = self.cog.format_water_info_data(data, selected_reservoir)
            await interaction.followup.send(embed=embed)
            logger.info(f"用戶 {interaction.user} 查詢了 {selected_reservoir} 的水情")
            
        except Exception as e:
            logger.error(f"處理水情查詢選擇時發生錯誤: {str(e)}")
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ 錯誤",
                    description="處理選擇時發生錯誤，請稍後再試",
                    color=discord.Color.red()
                )
            )
            
    async def on_timeout(self):
        """處理選單逾時"""
        # 選單逾時時，禁用所有選項
        for item in self.children:
            item.disabled = True



# 新增水庫水情資料分頁器類別
class WaterInfoPaginator(discord.ui.View):
    """用於分頁顯示所有水庫水情資料的分頁器"""
    
    def __init__(self, embeds: list, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.total_pages = len(embeds)
        
        # 更新按鈕狀態
        self._update_buttons()
    
    def _update_buttons(self):
        """更新按鈕狀態"""
        # 第一頁時，禁用上一頁和第一頁按鈕
        self.first_page.disabled = (self.current_page == 0)
        self.prev_page.disabled = (self.current_page == 0)
        
        # 最後一頁時，禁用下一頁和最後一頁按鈕
        self.next_page.disabled = (self.current_page == self.total_pages - 1)
        self.last_page.disabled = (self.current_page == self.total_pages - 1)
    
    async def update_message(self, interaction: discord.Interaction):
        """更新訊息以顯示當前頁面"""
        embed = self.embeds[self.current_page]
        # 添加頁碼資訊到嵌入訊息
        embed.set_footer(text=f"第 {self.current_page + 1}/{self.total_pages} 頁 | 資料來源: 經濟部水利署")
        self._update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="首頁", style=discord.ButtonStyle.gray, emoji="⏮️")
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """跳轉到第一頁"""
        self.current_page = 0
        await self.update_message(interaction)
    
    @discord.ui.button(label="上一頁", style=discord.ButtonStyle.blurple, emoji="◀️")
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """顯示上一頁"""
        self.current_page -= 1
        if self.current_page < 0:
            self.current_page = 0
        await self.update_message(interaction)
    
    @discord.ui.button(label="下一頁", style=discord.ButtonStyle.blurple, emoji="▶️")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """顯示下一頁"""
        self.current_page += 1
        if self.current_page >= self.total_pages:
            self.current_page = self.total_pages - 1
        await self.update_message(interaction)
    
    @discord.ui.button(label="尾頁", style=discord.ButtonStyle.gray, emoji="⏭️")
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """跳轉到最後一頁"""
        self.current_page = self.total_pages - 1
        await self.update_message(interaction)
    
    async def on_timeout(self):
        """處理分頁器逾時"""
        # 分頁器逾時時，禁用所有按鈕
        for item in self.children:
            item.disabled = True

class InfoCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.earthquake_cache = {}
        self.weather_cache = {}
        self.weather_alert_cache = {}
        self.reservoir_cache = {}
        self.water_info_cache = {}  # 新增水情資料快取
        self.cache_time = 0
        self.weather_cache_time = 0
        self.weather_alert_cache_time = 0
        self.reservoir_cache_time = 0
        self.water_info_cache_time = 0  # 新增水情資料快取時間
        self.api_auth = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
        self.notification_channels = {}
        self.last_eq_time = {}
        self.check_interval = 300  # 每5分鐘檢查一次
        
        # 建立 aiohttp 工作階段
        self.session = None
        self.bot.loop.create_task(self.init_aiohttp_session())
        
        # 開始地震監控
        self.eq_check_task = self.bot.loop.create_task(self.check_earthquake_updates())

    async def init_aiohttp_session(self):
        """初始化 aiohttp 工作階段"""
        try:
            # 完全停用 SSL 驗證
            import ssl
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(
                ssl=ssl_context,  # 使用自訂的 SSL 上下文
                limit=10          # 同時連接數限制
            )
            
            # 建立 aiohttp 工作階段
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=20, connect=10, sock_read=15),
                connector=connector,
                trust_env=True   # 允許從環境變數讀取代理設定
            )
            logger.info("已初始化 aiohttp 工作階段 (使用自訂 SSL 上下文)")
        except Exception as e:
            logger.error(f"初始化 aiohttp 工作階段時發生錯誤: {str(e)}")

    async def cog_unload(self):
        """當Cog被卸載時停止地震檢查任務和關閉aiohttp工作階段"""
        self.eq_check_task.cancel()
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("已關閉 aiohttp 工作階段")

    async def check_earthquake_updates(self):
        """定期檢查是否有新地震"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                # 檢查一般地震
                data = await self.fetch_earthquake_data(small_area=False)
                if data and 'records' in data and 'earthquake' in data['records']:
                    latest_eq = data['records']['earthquake'][0]
                    report_time = latest_eq['reportTime']
                    
                    # 檢查是否為新地震
                    for guild_id, channel_id in self.notification_channels.items():
                        if guild_id not in self.last_eq_time or report_time != self.last_eq_time[guild_id]:
                            # 更新最後地震時間
                            self.last_eq_time[guild_id] = report_time
                            
                            # 發送通知
                            try:
                                channel = self.bot.get_channel(channel_id)
                                if channel:
                                    embed = self.format_earthquake_data(data, small_area=False)
                                    embed.title = "🚨 新地震通報！"
                                    await channel.send(embed=embed)
                            except Exception as e:
                                logger.error(f"發送地震通知時發生錯誤: {str(e)}")
                
            except asyncio.CancelledError:
                # 正常取消
                break
            except Exception as e:
                logger.error(f"檢查地震更新時發生錯誤: {str(e)}")
            
            await asyncio.sleep(self.check_interval)

    async def fetch_with_retry(self, url: str, timeout: int = 20, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """以重試機制發送非同步請求"""
        for attempt in range(max_retries):
            try:
                if self.session is None or self.session.closed:
                    # 建立新的會話時禁用SSL驗證
                    connector = aiohttp.TCPConnector(ssl=False, limit=10)
                    self.session = aiohttp.ClientSession(
                        timeout=aiohttp.ClientTimeout(total=30, connect=10, sock_read=20),
                        connector=connector,
                        raise_for_status=True
                    )
                    logger.info("已創建新的 aiohttp 工作階段")

                logger.info(f"正在發送請求到 {url} (嘗試 {attempt + 1}/{max_retries})")
                async with self.session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            logger.info(f"成功獲取資料: {str(data)[:200]}...")  # 只記錄前200個字元
                            return data
                        except Exception as e:
                            logger.error(f"解析JSON回應時發生錯誤: {str(e)}")
                            return None
                    else:
                        logger.warning(f"API請求返回非200狀態碼: {response.status}")
                        text = await response.text()
                        logger.warning(f"回應內容: {text[:200]}...")  # 只記錄前200個字元
                        return None
            except asyncio.TimeoutError:
                logger.error(f"API請求超時 (嘗試 {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))
            except Exception as e:
                logger.error(f"API請求錯誤 (嘗試 {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1 * (attempt + 1))
                if attempt == max_retries - 1:
                    # 最後一次嘗試失敗時，記錄詳細錯誤
                    logger.error(f"最終API請求失敗: {str(e)}")
        return None

    async def fetch_earthquake_data(self, small_area: bool = False) -> Optional[Dict[str, Any]]:
        """從氣象局取得最新地震資料 (使用非同步請求)"""
        current_time = datetime.datetime.now().timestamp()
        cache_key = "small" if small_area else "normal"
        
        logger.info(f"開始獲取地震資料 (類型: {cache_key})")
        
        # 如果快取資料未過期（5分鐘內），直接返回快取
        if (cache_key in self.earthquake_cache and 
            current_time - self.cache_time < 300):
            logger.info(f"使用快取的地震資料 (類型: {cache_key})")
            logger.info(f"快取資料內容: {str(self.earthquake_cache[cache_key])[:200]}...")
            return self.earthquake_cache[cache_key]

        try:
            # 選擇適當的 API 端點
            if small_area:
                url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={self.api_auth}&limit=1"  # 小區域有感地震
            else:
                url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001?Authorization={self.api_auth}&limit=1"  # 一般地震
            
            logger.info(f"正在獲取地震資料，URL: {url}")
            
            # 使用非同步請求獲取資料，並處理 SSL 相關錯誤
            try:
                data = await self.fetch_with_retry(url, timeout=30, max_retries=3)
                
                if data and isinstance(data, dict):
                    # 驗證資料結構
                    if 'success' in data and data['success']:
                        if 'records' in data and 'earthquake' in data['records'] and data['records']['earthquake']:
                            # 更新快取
                            self.earthquake_cache[cache_key] = data
                            self.cache_time = current_time
                            logger.info(f"成功獲取並更新地震資料快取，資料：{data}")
                            return data
                        else:
                            logger.error(f"地震資料結構不完整: {data}")
                    else:
                        logger.error(f"API 請求不成功: {data}")
                else:
                    logger.error(f"獲取到的資料格式不正確: {data}")
            
            except Exception as e:
                logger.error(f"地震資料請求失敗: {str(e)}")
                if 'SSL' in str(e):
                    logger.warning("SSL 驗證錯誤，嘗試重新初始化連線")
                    # 重新初始化工作階段並重試
                    await self.init_aiohttp_session()
                    try:
                        data = await self.fetch_with_retry(url, timeout=30, max_retries=3)
                        if data and isinstance(data, dict) and data.get('success'):
                            return data
                    except Exception as retry_e:
                        logger.error(f"重試請求也失敗了: {str(retry_e)}")
            
            # 如果請求失敗，檢查是否有快取資料可用
            if cache_key in self.earthquake_cache:
                logger.warning("使用過期的地震資料快取")
                return self.earthquake_cache[cache_key]
            
            return None
                
        except Exception as e:
            logger.error(f"獲取地震資料時發生錯誤: {str(e)}")
            
            # 如果發生錯誤，檢查是否有快取資料可用
            if cache_key in self.earthquake_cache:
                logger.info("發生錯誤，使用地震快取資料")
                return self.earthquake_cache[cache_key]
            
            return None

    async def fetch_weather_data(self) -> Optional[Dict[str, Any]]:
        """從氣象局取得36小時天氣預報資料 (使用非同步請求)"""
        """從氣象局取得36小時天氣預報資料 (使用非同步請求)"""
        current_time = datetime.datetime.now().timestamp()
        
        # 如果快取資料未過期（30分鐘內），直接返回快取
        if (self.weather_cache and 
            current_time - self.weather_cache_time < 1800):
            logger.info("使用快取的天氣預報資料")
            return self.weather_cache

        try:
            url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={self.api_auth}"
            
            # 使用非同步請求獲取資料
            data = await self.fetch_with_retry(url, timeout=15, max_retries=3)
            
            if data:
                # 更新快取
                self.weather_cache = data
                self.weather_cache_time = current_time
                logger.info("成功獲取並更新天氣預報資料快取")
                return data
            else:
                # 如果請求失敗，檢查是否有快取資料可用
                if self.weather_cache:
                    logger.warning("天氣資料請求失敗，使用過期的快取資料")
                    return self.weather_cache
                return None
                
        except Exception as e:
            logger.error(f"獲取天氣預報資料時發生錯誤: {str(e)}")
            
            # 如果發生錯誤，檢查是否有快取資料可用
            if self.weather_cache:
                logger.info("發生錯誤，使用天氣預報快取資料")
                return self.weather_cache
                
            return None

    async def fetch_reservoir_data(self) -> Optional[Dict[str, Any]]:
        """從水利署取得最新水庫資料 (使用非同步請求)"""
        current_time = datetime.datetime.now().timestamp()
        
        # 如果快取資料未過期（30分鐘內），直接返回快取
        if (self.reservoir_cache and 
            current_time - self.reservoir_cache_time < 1800):
            logger.info("使用快取的水庫資料")
            return self.reservoir_cache

        try:
            url = "https://data.wra.gov.tw/OpenAPI/api/OpenData/50C8256D-30C5-4B8D-9B84-2E14D5C6DF71/Data?size=1000&page=1"
            
            # 使用非同步請求獲取資料
            data = await self.fetch_with_retry(url, timeout=20, max_retries=3)
            
            if data:
                # 更新快取
                self.reservoir_cache = data
                self.reservoir_cache_time = current_time
                logger.info("成功獲取並更新水庫資料快取")
                return data
            else:
                # 如果請求失敗，檢查是否有快取資料可用
                if self.reservoir_cache:
                    logger.warning("水庫資料請求失敗，使用過期的快取資料")
                    return self.reservoir_cache
                return None
                
        except Exception as e:
            logger.error(f"獲取水庫資料時發生錯誤: {str(e)}")
            
            # 如果發生錯誤，檢查是否有快取資料可用
            if self.reservoir_cache:
                logger.info("發生錯誤，使用水庫資料快取")
                return self.reservoir_cache
                
            return None

    async def fetch_water_info_data(self) -> Optional[Dict[str, Any]]:
        """從水利署取得最新水庫水情資料 (使用非同步請求)"""
        current_time = datetime.datetime.now().timestamp()
        
        # 如果快取資料未過期（30分鐘內），直接返回快取
        if (self.water_info_cache and 
            current_time - self.water_info_cache_time < 1800):
            logger.info("使用快取的水庫水情資料")
            return self.water_info_cache

        try:
            # 設定API端點
            url = "https://data.wra.gov.tw/OpenAPI/api/OpenData/1602CA19-B224-4CC3-AA31-11B1B124530F/Data?size=1000&page=1"
            
            # 使用增強版的非同步請求方法，增加超時時間和重試次數
            data = None
            
            # 首次嘗試使用標準超時設定
            try:
                async with asyncio.timeout(30):  # 增加總超時時間到30秒
                    data = await self.fetch_with_retry(url, timeout=25, max_retries=5)
            except asyncio.TimeoutError:
                logger.warning("第一次獲取水庫水情資料超時，將嘗試降級請求")
                # 如果第一次超時，嘗試使用更寬鬆的超時設定
                try:
                    # 創建新的會話並設定更寬鬆的超時
                    async with aiohttp.ClientSession(
                        timeout=aiohttp.ClientTimeout(total=40, connect=20, sock_read=30),
                        connector=aiohttp.TCPConnector(verify_ssl=False)
                    ) as session:
                        async with session.get(url) as response:
                            if response.status == 200:
                                data = await response.json()
                                logger.info("透過降級請求成功獲取水庫水情資料")
                            else:
                                logger.error(f"降級請求失敗: HTTP狀態碼 {response.status}")
                except Exception as e:
                    logger.error(f"降級請求時發生錯誤: {str(e)}")
            
            if data:
                # 驗證數據結構
                if 'responseData' in data and isinstance(data['responseData'], list):
                    # 增強數據驗證: 檢查第一個項目是否包含必要字段
                    if data['responseData'] and isinstance(data['responseData'][0], dict) and 'ReservoirName' in data['responseData'][0]:
                        # 更新快取
                        self.water_info_cache = data
                        self.water_info_cache_time = current_time
                        logger.info("成功獲取並更新水庫水情資料快取")
                        return data
                    else:
                        logger.error("水庫水情資料結構無效: 資料項目缺少必要字段")
                else:
                    logger.error(f"水庫水情數據格式異常: {list(data.keys()) if isinstance(data, dict) else '非字典類型'}")
                
                # 即使數據結構不完整，也返回獲取到的數據，避免完全失敗
                logger.warning("水庫水情數據結構異常，但仍返回獲取到的數據")
                return data
            else:
                # 如果請求失敗，檢查是否有快取資料可用
                if self.water_info_cache:
                    logger.warning("水庫水情請求失敗，使用過期的快取資料")
                    return self.water_info_cache
                else:
                    logger.error("無法獲取水庫水情資料，且沒有可用的快取")
                return None
                
        except asyncio.TimeoutError:
            logger.error("獲取水庫水情資料超時")
            # 直接使用快取，避免再次嘗試可能會超時的請求
            if self.water_info_cache:
                logger.info("發生超時，使用水庫水情快取資料")
                return self.water_info_cache
            return None
                
        except Exception as e:
            logger.error(f"獲取水庫水情資料時發生錯誤: {str(e)}")
            
            # 如果發生錯誤，檢查是否有快取資料可用
            if self.water_info_cache:
                logger.info("發生錯誤，使用水庫水情快取資料")
                return self.water_info_cache
                
            return None



    def format_reservoir_data(self, data: Dict[str, Any], reservoir_name: str) -> discord.Embed:
        """格式化水庫資料為 Discord 嵌入消息"""
        try:
            # 檢查資料結構，適應可能的API變化
            reservoirs = None
            
            # 檢查舊格式 (有data欄位)
            if 'data' in data:
                reservoirs = data['data']
            # 檢查可能的新格式
            elif 'ReservoirConditionsToday' in data:
                reservoirs = data['ReservoirConditionsToday']
            elif 'ReservoirInfo' in data:
                reservoirs = data['ReservoirInfo']
            elif isinstance(data, list):  # 可能直接是列表格式
                reservoirs = data
            else:
                # 嘗試找出資料中可能包含水庫資訊的欄位
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0:
                        # 檢查第一個元素是否像水庫資料 (有 ReservoirName 欄位)
                        if isinstance(value[0], dict) and 'ReservoirName' in value[0]:
                            reservoirs = value
                            logger.info(f"找到可能的水庫資料欄位: {key}")
                            break
            
            if not reservoirs:
                logger.error(f"無法辨識水庫資料格式. 資料結構: {data.keys() if isinstance(data, dict) else type(data)}")
                return discord.Embed(
                    title="⚠️ 資料格式錯誤",
                    description="目前無法解析水庫資料格式，請通知管理員檢查API變更",
                    color=discord.Color.orange()
                )
            
            if not reservoirs:
                return discord.Embed(
                    title="⚠️ 沒有水庫資料",
                    description="目前沒有任何水庫資料可供顯示",
                    color=discord.Color.orange()
                )
            
            # 尋找指定水庫的資料
            reservoir_data = None
            for reservoir in reservoirs:
                if reservoir.get('ReservoirName') == reservoir_name:
                    reservoir_data = reservoir
                    break
            
            if not reservoir_data:
                return discord.Embed(
                    title="❌ 找不到資料",
                    description=f"找不到 {reservoir_name} 的資料",
                    color=discord.Color.red()
                )
            
            # 解析水庫資料
            name = reservoir_data.get('ReservoirName', '無資料')
            time = reservoir_data.get('ObservationTime', reservoir_data.get('DataTime', '無資料'))
            capacity = reservoir_data.get('EffectiveCapacity', reservoir_data.get('Capacity', '無資料'))  # 有效容量
            current_volume = reservoir_data.get('EffectiveWaterStorageCapacity', reservoir_data.get('WaterStorage', '無資料'))  # 有效蓄水量
            percentage = reservoir_data.get('PercentageOfStorage', reservoir_data.get('CapacityPercentage', '無資料'))  # 蓄水百分比
            inflow = reservoir_data.get('InflowVolume', reservoir_data.get('Inflow', '無資料'))  # 進水量
            outflow = reservoir_data.get('OutflowTotal', reservoir_data.get('Outflow', '無資料'))  # 出水量
            
            # 處理百分比格式，確保顯示為數字
            if percentage and percentage != '無資料':
                try:
                    # 嘗試將百分比轉換為浮點數
                    percentage = float(percentage)
                    # 檢查是否已經是小數形式 (例如0.75代表75%)
                    if percentage < 1.0:
                        percentage = percentage * 100
                    # 格式化為最多2位小數
                    percentage = f"{percentage:.2f}".rstrip('0').rstrip('.') if '.' in f"{percentage:.2f}" else f"{percentage:.0f}"
                except ValueError:
                    # 如果無法轉換，保持原樣
                    pass
            
            # 計算水情狀態
            water_status = "正常"
            status_color = discord.Color.green()
            status_emoji = "✅"
            
            if percentage and percentage != '無資料':
                try:
                    percent_float = float(percentage)
                    if percent_float < 20:
                        water_status = "嚴重水情"
                        status_color = discord.Color.red()
                        status_emoji = "⚠️"
                    elif percent_float < 30:
                        water_status = "水情警戒"
                        status_color = discord.Color.orange()
                        status_emoji = "⚠️"
                    elif percent_float < 50:
                        water_status = "水情提醒"
                        status_color = discord.Color.gold()
                        status_emoji = "⚠️"
                    elif percent_float < 70:
                        water_status = "水情注意"
                        status_color = discord.Color.blue()
                        status_emoji = "ℹ️"
                    elif percent_float >= 90:
                        water_status = "水情充裕"
                        status_color = discord.Color.dark_green()
                        status_emoji = "💯"
                except ValueError:
                    # 如果無法轉換百分比，使用預設值
                    pass
            
            # 建立嵌入消息
            embed = discord.Embed(
                title=f"💧 {name} 水庫每日營運情況",
                description=f"觀測時間: {time}",
                color=status_color
            )
            
            embed.add_field(
                name="📊 蓄水量",
                value=f"目前蓄水量: {current_volume} 萬立方公尺\n"
                      f"有效容量: {capacity} 萬立方公尺\n"
                      f"蓄水百分比: {percentage}%",
                inline=False
            )
            
            embed.add_field(
                name="🌊 進出水量",
                value=f"進水量: {inflow} 立方公尺/秒\n"
                      f"出水量: {outflow} 立方公尺/秒",
                inline=False
            )
            
            embed.add_field(
                name=f"{status_emoji} 水情狀態",
                value=water_status,
                inline=False
            )
            
            # 添加資料來源
            embed.set_footer(text=f"資料來源: 經濟部水利署")
            
            return embed
            
        except ValueError as ve:
            logger.error(f"格式化水庫資料時發生錯誤: {str(ve)}")
            return discord.Embed(
                title="❌ 資料格式錯誤",
                description=f"無法解析水庫資料: {str(ve)}",
                color=discord.Color.red()
            )
            
        except Exception as e:
            logger.error(f"格式化水庫資料時發生錯誤: {str(e)}")
            return discord.Embed(
                title="❌ 錯誤",
                description="格式化水庫資料時發生錯誤，請稍後再試",
                color=discord.Color.red()
            )

    def format_water_info_data(self, data: Dict[str, Any], reservoir_name: str) -> discord.Embed:
        """格式化水庫水情資料為 Discord 嵌入消息"""
        try:
            # 檢查資料結構
            if not data or 'responseData' not in data:
                logger.error(f"無效的水庫水情資料格式: 缺少 responseData 欄位")
                return discord.Embed(
                    title="⚠️ 資料格式錯誤",
                    description="無法讀取水庫水情資料，請通知管理員檢查API變更",
                    color=discord.Color.orange()
                )
            
            reservoirs = data.get('responseData', [])
            
            if not reservoirs:
                return discord.Embed(
                    title="⚠️ 沒有水庫水情資料",
                    description="目前沒有任何水庫水情資料可供顯示",
                    color=discord.Color.orange()
                )
            
            # 尋找指定水庫的資料
            reservoir_data = None
            for reservoir in reservoirs:
                if reservoir.get('ReservoirName') == reservoir_name:
                    reservoir_data = reservoir
                    break
            
            if not reservoir_data:
                return discord.Embed(
                    title="❌ 找不到資料",
                    description=f"找不到 {reservoir_name} 的水情資料",
                    color=discord.Color.red()
                )
            
            # 解析水庫水情資料
            name = reservoir_data.get('ReservoirName', '無資料')
            time = reservoir_data.get('ObservationTime', '無資料')
            water_level = reservoir_data.get('WaterLevel', '無資料')  # 水位高度
            effective_capacity = reservoir_data.get('EffectiveCapacity', '無資料')  # 有效容量
            effective_storage = reservoir_data.get('EffectiveStorage', '無資料')  # 有效蓄水量
            percentage = reservoir_data.get('PercentageOfStorage', '無資料')  # 蓄水百分比
            inflow = reservoir_data.get('InFlow', '無資料')  # 進水量
            outflow = reservoir_data.get('OutFlow', '無資料')  # 出水量
            
            # 處理百分比格式，確保顯示為數字
            if percentage and percentage != '無資料':
                try:
                    # 嘗試將百分比轉換為浮點數
                    percentage = float(percentage)
                    # 檢查是否已經是小數形式 (例如0.75代表75%)
                    if percentage < 1.0:
                        percentage = percentage * 100
                    # 格式化為最多2位小數
                    percentage = f"{percentage:.2f}".rstrip('0').rstrip('.') if '.' in f"{percentage:.2f}" else f"{percentage:.0f}"
                except ValueError:
                    # 如果無法轉換，保持原樣
                    pass
            
            # 計算水情狀態
            water_status = "正常"
            status_color = discord.Color.green()
            status_emoji = "✅"
            
            if percentage and percentage != '無資料':
                try:
                    percent_float = float(percentage)
                    if percent_float < 20:
                        water_status = "嚴重水情"
                        status_color = discord.Color.red()
                        status_emoji = "🔴"
                    elif percent_float < 30:
                        water_status = "水情警戒"
                        status_color = discord.Color.orange()
                        status_emoji = "🟠"
                    elif percent_float < 50:
                        water_status = "水情提醒"
                        status_color = discord.Color.gold()
                        status_emoji = "🟡"
                    elif percent_float < 70:
                        water_status = "水情注意"
                        status_color = discord.Color.blue()
                        status_emoji = "🔵"
                    elif percent_float >= 90:
                        water_status = "水情充裕"
                        status_color = discord.Color.dark_green()
                        status_emoji = "🟢"
                except ValueError:
                    # 如果無法轉換百分比，使用預設值
                    pass
            
            # 建立嵌入消息
            embed = discord.Embed(
                title=f"💧 {name} 水庫水情資料",
                description=f"觀測時間: {time}",
                color=status_color
            )
            
            embed.add_field(
                name="📊 水庫水位",
                value=f"目前水位: {water_level} 公尺",
                inline=False
            )
            
            embed.add_field(
                name="🌊 蓄水情況",
                value=f"有效容量: {effective_capacity} 萬立方公尺\n"
                      f"有效蓄水量: {effective_storage} 萬立方公尺\n"
                      f"蓄水百分比: {percentage}%",
                inline=False
            )
            
            embed.add_field(
                name="🔄 進出水量",
                value=f"進水量: {inflow} cms\n"
                      f"出水量: {outflow} cms",
                inline=False
            )
            
            embed.add_field(
                name=f"{status_emoji} 水情狀態",
                value=water_status,
                inline=False
            )
            
            # 添加資料來源
            embed.set_footer(text=f"資料來源: 經濟部水利署")
            
            return embed
            
        except Exception as e:
            logger.error(f"格式化水庫水情資料時發生錯誤: {str(e)}")
            return discord.Embed(
                title="❌ 錯誤",
                description="格式化水庫水情資料時發生錯誤，請稍後再試",
                color=discord.Color.red()
            )

    def format_earthquake_data(self, data: dict, small_area: bool = False) -> discord.Embed:
        """格式化地震資料為 Discord Embed"""
        try:
            # 驗證基本資料結構
            if (not data or 'success' not in data or data['success'] != 'true' or
                    'result' not in data or 'records' not in data['result'] or
                    'Earthquake' not in data['result']['records'] or
                    not data['result']['records']['Earthquake']):
                logger.error(f"無效的地震資料格式: {data}")
                return discord.Embed(title="❌ 錯誤", description="無法取得地震資料或資料格式不符。", color=discord.Color.red())
                
            eq_records = data['result']['records']
            eq = eq_records['Earthquake'][0]  # 取得最新一筆地震資料
            
            # 創建基本的 Embed
            embed = discord.Embed(
                title="🌋 最新地震報告",
                description=eq.get('ReportContent', '無描述資料'),
                color=self._get_report_color(eq.get('ReportColor', ''))
            )
            
            # 地震基本資訊
            if 'EarthquakeInfo' in eq:
                info = eq['EarthquakeInfo']
                embed.add_field(name="發生時間", value=info.get('OriginTime', '未知'), inline=True)
                
                # 震央資訊
                if 'Epicenter' in info:
                    epicenter = info['Epicenter']
                    location = (f"北緯 {epicenter.get('EpicenterLatitude', '未知')} 度\n"
                               f"東經 {epicenter.get('EpicenterLongitude', '未知')} 度")
                    embed.add_field(
                        name="震央位置",
                        value=f"{epicenter.get('Location', '未知')}\n{location}",
                        inline=False
                    )
                
                # 地震規模
                if 'EarthquakeMagnitude' in info:
                    mag = info['EarthquakeMagnitude']
                    embed.add_field(
                        name="地震規模",
                        value=f"{mag.get('MagnitudeType', '')} {mag.get('MagnitudeValue', '未知')}",
                        inline=True
                    )
                
                # 震源深度
                if 'FocalDepth' in info:
                    embed.add_field(name="震源深度", value=f"{info['FocalDepth']} 公里", inline=True)
            
            # 各地震度資訊
            max_intensity = "0級"
            intensity_areas = []
            
            if 'Intensity' in eq and 'ShakingArea' in eq['Intensity']:
                for area in eq['Intensity']['ShakingArea']:
                    if 'CountyName' in area and 'AreaIntensity' in area:
                        county_name = area['CountyName']
                        area_intensity = area['AreaIntensity']
                        intensity_areas.append(f"{county_name}: {area_intensity}")
                        
                        # 更新最大震度
                        if self._compare_intensity(area_intensity, max_intensity):
                            max_intensity = area_intensity
            
            # 添加最大震度
            if max_intensity != "0級":
                embed.add_field(
                    name=f"最大震度 {max_intensity}",
                    value="以下為各地區震度：",
                    inline=False
                )
                
                # 將震度資訊分組顯示，每組最多5個地區
                if intensity_areas:
                    chunks = [intensity_areas[i:i + 5] for i in range(0, len(intensity_areas), 5)]
                    for i, chunk in enumerate(chunks):
                        if i < 3:  # 最多顯示3組，避免太長
                            embed.add_field(
                                name="各地震度" if i == 0 else "\u200b",
                                value="\n".join(chunk),
                                inline=True
                            )
                    if len(chunks) > 3:
                        embed.add_field(
                            name="\u200b", 
                            value=f"...及其他 {len(intensity_areas) - 15} 個地區",
                            inline=True
                        )
            
            # 添加地震圖片
            if 'ReportImageURI' in eq:
                embed.set_image(url=eq['ReportImageURI'])
            
            # 添加詳細資訊連結
            if 'Web' in eq:
                embed.add_field(name="詳細資訊", value=eq['Web'], inline=False)
            
            # 添加備註資訊
            footer_text = []
            if 'ReportRemark' in eq:
                footer_text.append(eq['ReportRemark'])
            if 'EarthquakeInfo' in eq and 'Source' in eq['EarthquakeInfo']:
                footer_text.append(f"資料來源: {eq['EarthquakeInfo']['Source']}")
            
            embed.set_footer(text=" | ".join(footer_text) if footer_text else "資料來源：中央氣象署")
            
            return embed
            
        except Exception as e:
            logger.error(f"格式化地震資料時發生錯誤: {str(e)}")
            return discord.Embed(
                title="❌ 錯誤",
                description=f"處理地震資料時發生錯誤: {str(e)}",
                color=discord.Color.red()
            )

    def _get_report_color(self, color_text: str) -> discord.Color:
        """根據報告顏色文字返回對應的 Discord 顏色"""
        color_map = {
            "綠色": discord.Color.green(),
            "黃色": discord.Color.gold(),
            "橙色": discord.Color.orange(),
            "紅色": discord.Color.red()
        }
        return color_map.get(color_text, discord.Color.blue())

    def _compare_intensity(self, intensity1: str, intensity2: str) -> bool:
        """比較兩個震度，如果 intensity1 大於 intensity2 返回 True"""
        try:
            # 移除 "級" 字並轉換為數字
            level1 = int(intensity1.replace("級", ""))
            level2 = int(intensity2.replace("級", ""))
            return level1 > level2
        except (ValueError, TypeError):
            return False

    @app_commands.command(name="earthquake", description="查詢最新地震報告")
    @app_commands.describe(
        area_type="地震區域類型"
    )
    @app_commands.choices(area_type=[
        app_commands.Choice(name="一般地震", value="normal"),
        app_commands.Choice(name="小區域地震", value="small")
    ])
    async def earthquake_command(self, interaction: discord.Interaction, area_type: str = "normal"):
        """查詢最新地震報告的斜線指令"""
        try:
            # 立即回應，避免互動超時
            await interaction.response.defer(ephemeral=False, thinking=True)
            
            # 根據選擇的類型獲取地震資料
            data = await self.fetch_earthquake_data(small_area=(area_type == "small"))
            if not data:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="❌ 錯誤",
                        description="無法取得地震資料，請稍後再試",
                        color=discord.Color.red()
                    )
                )
                return
                
            # 格式化並發送地震資料
            embed = self.format_earthquake_data(data, small_area=(area_type == "small"))
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"執行地震查詢指令時發生錯誤: {str(e)}")
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ 錯誤",
                    description="處理地震資料時發生錯誤，請稍後再試",
                    color=discord.Color.red()
                )
            )

    @app_commands.command(
        name="weather",
        description="查詢地區36小時天氣預報"
    )
    async def weather(self, interaction: discord.Interaction):
        """開啟一個下拉式選單來選擇要查詢的縣市天氣預報"""
        try:
            # 創建下拉式選單視圖
            view = WeatherSelectView(self)
            
            # 發送選擇提示訊息
            embed = discord.Embed(
                title="🌤️ 天氣查詢",
                description="請從下方選單選擇要查詢的縣市",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📋 天氣資訊包含",
                value="• 未來36小時天氣預報\n• 降雨機率\n• 溫度範圍\n• 舒適度指數",
                inline=False
            )
            
            embed.add_field(
                name="⏱️ 選單有效時間",
                value="此選單將在2分鐘後自動失效",
                inline=False
            )
            
            embed.set_footer(text="資料來源：交通部中央氣象署")
            
            await interaction.response.send_message(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"創建天氣查詢選單時發生錯誤: {str(e)}")
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ 錯誤",
                    description="無法顯示天氣查詢選單，請稍後再試",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @app_commands.command(
        name="reservoir",
        description="查詢水庫每日營運情況"
    )
    async def reservoir(self, interaction: discord.Interaction):
        """開啟一個下拉式選單來選擇要查詢的水庫營運情況"""
        try:
            # 創建下拉式選單視圖
            view = ReservoirSelectView(self)
            
            # 發送選擇提示訊息
            embed = discord.Embed(
                title="💧 水庫營運情況查詢",
                description="請從下方選單選擇要查詢的水庫",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📋 水庫資訊包含",
                value="• 目前蓄水量\n• 有效容量\n• 蓄水百分比\n• 進出水量\n• 水情狀態",
                inline=False
            )
            
            embed.add_field(
                name="⏱️ 選單有效時間",
                value="此選單將在2分鐘後自動失效",
                inline=False
            )
            
            embed.set_footer(text="資料來源: 經濟部水利署")
            
            await interaction.response.send_message(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"創建水庫查詢選單時發生錯誤: {str(e)}")
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ 錯誤",
                    description="無法顯示水庫查詢選單，請稍後再試",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @app_commands.command(
        name="water_info",
        description="查詢水庫即時水情資料"
    )
    async def water_info(self, interaction: discord.Interaction):
        """開啟一個下拉式選單來選擇要查詢的水庫水情資料"""
        try:
            # 創建下拉式選單視圖
            view = WaterInfoSelectView(self)
            
            # 發送選擇提示訊息
            embed = discord.Embed(
                title="💧 水庫即時水情查詢",
                description="請從下方選單選擇要查詢的水庫",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📋 水情資訊包含",
                value="• 目前水位\n• 有效容量\n• 有效蓄水量\n• 蓄水百分比\n• 進出水量\n• 水情狀態",
                inline=False
            )
            
            embed.add_field(
                name="⏱️ 選單有效時間",
                value="此選單將在2分鐘後自動失效",
                inline=False
            )
            
            embed.set_footer(text="資料來源: 經濟部水利署")
            
            await interaction.response.send_message(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"創建水庫水情查詢選單時發生錯誤: {str(e)}")
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ 錯誤",
                    description="無法顯示水庫水情查詢選單，請稍後再試",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )



async def setup(bot):
    await bot.add_cog(InfoCommands(bot))

