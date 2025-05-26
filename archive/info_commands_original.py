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
                if data and 'result' in data and 'records' in data['result'] and 'Earthquake' in data['result']['records']:
                    latest_eq = data['result']['records']['Earthquake'][0]
                    report_time = latest_eq.get('EarthquakeNo', '')
                    
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
                    if 'success' in data and data['success'] == 'true':
                        if 'result' in data and 'records' in data['result'] and 'Earthquake' in data['result']['records'] and data['result']['records']['Earthquake']:
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
                        if data and isinstance(data, dict) and data.get('success') == 'true':
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

    # 這裡添加其他方法 (如 format_weather_data, format_earthquake_data 等)...

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

async def setup(bot):
    await bot.add_cog(InfoCommands(bot))
