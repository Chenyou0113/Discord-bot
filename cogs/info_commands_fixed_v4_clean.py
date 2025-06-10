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

# 氣象顏色代碼
WEATHER_COLOR_MAP = {
    '第三階段': discord.Color.red(),
    '第二階段': discord.Color.orange(),
    '第一階段': discord.Color.gold(),
    '特報': discord.Color.blue(),
    '解除': discord.Color.green(),
    '災防': discord.Color.dark_red(),
    '土石流': discord.Color.dark_gold(),
    'default': discord.Color.light_grey()
}

# 天氣預報用表情符號對應
WEATHER_EMOJI = {
    "晴天": "☀️",
    "晴時多雲": "🌤️",
    "多雲時晴": "⛅",
    "多雲": "☁️",
    "多雲時陰": "☁️",
    "陰時多雲": "🌥️",
    "陰天": "🌫️",
    "多雲陣雨": "🌦️",
    "多雲短暫雨": "🌦️",
    "多雲時陰短暫雨": "🌧️",
    "陰時多雲短暫雨": "🌧️",
    "陰天陣雨": "🌧️",
    "陰天短暫雨": "🌧️", 
    "短暫雨": "🌧️",
    "雨天": "🌧️",
    "陣雨": "🌧️",
    "午後雷陣雨": "⛈️",
    "雷雨": "⛈️",
    "多雲雷陣雨": "⛈️",
    "晴午後陣雨": "🌦️",
    "晴午後雷陣雨": "⛈️",
    "陰陣雨": "🌧️",
    "多雲時晴短暫陣雨": "🌦️",
    "多雲時晴短暫雨": "🌦️",
    "多雲短暫陣雨": "🌦️",
    "多雲時陰陣雨": "🌧️",
    "陰時多雲陣雨": "🌧️",
    "陰短暫陣雨": "🌧️",
    "雨或雪": "🌨️",
    "雨夾雪": "🌨️",
    "陰有雨或雪": "🌨️",
    "多雲時陰有雨或雪": "🌨️",
    "多雲時陰短暫雨或雪": "🌨️",
    "多雲時陰短暫雪": "🌨️",
    "短暫雨或雪": "🌨️",
    "短暫雪": "❄️",
    "下雪": "❄️",
    "積雪": "❄️",
    "暴雨": "🌊",
    "大雨": "💦",
    "豪雨": "🌊",
    "大豪雨": "🌊",
    "超大豪雨": "🌊",
    "焚風": "🔥",
    "乾燥": "🏜️",
    "寒冷": "❄️",
    "熱浪": "🔥",
    "鋒面": "🌡️",
    "雲系": "☁️",
    "有霧": "🌫️",
    "霧": "🌫️",
    "煙霧": "🌫️",
    "沙塵暴": "🏜️"
}

class WeatherView(View):
    def __init__(self, cog, user_id: int, locations: List[str]):
        super().__init__(timeout=120)
        self.cog = cog
        self.user_id = user_id
        self.locations = locations
        self.add_location_select()

    def add_location_select(self):
        select = Select(
            placeholder="選擇縣市查看天氣預報...",
            options=[discord.SelectOption(label=location, value=location) for location in self.locations]
        )
        select.callback = self.on_location_select
        self.add_item(select)

    async def on_location_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("⚠️ 請使用自己的天氣選單！", ephemeral=True)
            return
            
        location = interaction.data['values'][0]
        
        try:
            # 使用缓存获取天气数据
            await interaction.response.defer(ephemeral=True, thinking=True)
            embed = await self.cog.format_weather_data(location)
            
            if embed:
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send("❌ 無法獲取天氣資料，請稍後再試。", ephemeral=True)
        except Exception as e:
            logger.error(f"處理天氣選單選擇時發生錯誤: {str(e)}")
            await interaction.followup.send("❌ 處理請求時發生錯誤，請稍後再試。", ephemeral=True)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("⚠️ 這不是您的天氣選單！", ephemeral=True)
            return False
        return True

class InfoCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.earthquake_cache = {}
        self.tsunami_cache = {}  # 新增海嘯資料快取
        self.weather_cache = {}
        self.weather_alert_cache = {}
        self.reservoir_cache = {}
        self.water_info_cache = {}  # 新增水情資料快取
        self.cache_time = 0
        self.tsunami_cache_time = 0  # 新增海嘯資料快取時間
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
            try:                # 檢查一般地震
                data = await self.fetch_earthquake_data(small_area=False)
                if data:
                    # 支援兩種資料結構
                    records = None
                    if 'records' in data:
                        # 有認證模式：records 在根級別
                        records = data['records']
                    elif 'result' in data and 'records' in data['result']:
                        # 無認證模式：records 在 result 內
                        records = data['result']['records']
                    
                    if records:
                        latest_eq = None
                        
                        # 檢查不同可能的資料格式
                        if isinstance(records, dict) and 'Earthquake' in records:
                            earthquake_data = records['Earthquake']
                            if isinstance(earthquake_data, list) and len(earthquake_data) > 0:
                                latest_eq = earthquake_data[0]
                            elif isinstance(earthquake_data, dict):
                                latest_eq = earthquake_data
                    
                    if latest_eq:
                        report_time = latest_eq.get('EarthquakeNo', '')
                        
                        # 檢查是否有新地震報告
                        for guild in self.bot.guilds:
                            channel_id = self.notification_channels.get(guild.id, None)
                            
                            # 如果該伺服器已設定通知頻道，且有新地震報告
                            if channel_id and guild.id in self.last_eq_time and report_time != self.last_eq_time[guild.id]:
                                channel = guild.get_channel(channel_id)
                                if channel:
                                    try:
                                        # 檢查機器人是否有此頻道的發送權限
                                        if channel.permissions_for(guild.me).send_messages:
                                            # 獲取並發送地震嵌入
                                            embed = await self.format_earthquake_data(latest_eq)
                                            if embed:
                                                embed.title = "🚨 新地震通報！"
                                                await channel.send(embed=embed)
                                    except Exception as e:
                                        logger.error(f"發送地震通知時發生錯誤: {str(e)}")
                        
                        # 更新最後地震時間
                        for guild in self.bot.guilds:
                            self.last_eq_time[guild.id] = report_time
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

        # 選擇適當的 API 端點
        if small_area:
            endpoint = "E-A0016-001"  # 小區域有感地震
        else:
            endpoint = "E-A0015-001"  # 一般地震
            
        url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{endpoint}"
        
        # 嘗試多種 API 調用方式
        api_attempts = [
            {
                "name": "無認證模式",
                "params": {
                    'limit': 1,
                    'format': 'JSON'
                }
            },
            {
                "name": "有認證模式", 
                "params": {
                    'Authorization': self.api_auth,
                    'limit': 1,
                    'format': 'JSON'
                }
            }
        ]

        try:
            # 按順序嘗試不同的 API 調用方式
            for attempt in api_attempts:
                logger.info(f"嘗試{attempt['name']}獲取地震資料")
                
                # 構建完整的URL
                param_string = "&".join([f"{k}={v}" for k, v in attempt['params'].items()])
                full_url = f"{url}?{param_string}"
                
                logger.info(f"正在獲取地震資料，URL: {full_url}")
                
                # 使用非同步請求獲取資料，並處理 SSL 相關錯誤
                try:
                    data = await self.fetch_with_retry(full_url, timeout=30, max_retries=3)                    
                    if data and isinstance(data, dict):
                        # 驗證資料結構
                        if 'success' in data and (data['success'] == 'true' or data['success'] is True):
                            # 檢查是否為API異常格式（只有欄位定義，無實際資料）
                            if ('result' in data and isinstance(data['result'], dict) and 
                                set(data['result'].keys()) == {'resource_id', 'fields'}):
                                logger.warning(f"API回傳異常資料結構（{attempt['name']}失敗），嘗試下一種方式")
                                continue  # 嘗試下一種 API 調用方式
                              # 檢查是否有實際的地震資料 (支援兩種資料結構)
                            records_data = None
                            if 'records' in data:
                                # 有認證模式：records 在根級別
                                records_data = data['records']
                            elif 'result' in data and 'records' in data.get('result', {}):
                                # 無認證模式：records 在 result 內
                                records_data = data['result']['records']
                            
                            if (records_data and isinstance(records_data, dict) and
                                'Earthquake' in records_data and records_data['Earthquake']):
                                
                                logger.info(f"✅ {attempt['name']}成功獲取地震資料")
                                
                                # 更新快取
                                self.earthquake_cache[cache_key] = data
                                self.cache_time = current_time
                                logger.info(f"成功獲取並更新地震資料快取")
                                
                                return data
                            else:
                                logger.warning(f"{attempt['name']}獲取的資料結構不完整，嘗試下一種方式")
                                continue
                        else:
                            logger.warning(f"{attempt['name']} API 請求不成功: {data.get('success', 'unknown')}")
                            continue
                    else:
                        logger.warning(f"{attempt['name']}獲取到的資料格式不正確")
                        continue
                        
                except Exception as api_e:
                    logger.error(f"{attempt['name']}請求失敗: {str(api_e)}")
                    continue  # 嘗試下一種方式
              # 如果所有 API 調用方式都失敗，使用備用資料
            logger.warning("所有 API 調用方式都失敗，使用備用地震資料")
            return await self.get_backup_earthquake_data(small_area)
            
        except Exception as e:
            logger.error(f"獲取地震資料時發生錯誤: {str(e)}")
            
            # 如果發生錯誤，檢查是否有快取資料可用
            if cache_key in self.earthquake_cache:
                logger.info("發生錯誤，使用地震快取資料")
                return self.earthquake_cache[cache_key]
            
            # 最後的備用方案
            logger.warning("沒有可用的快取資料，使用備用地震資料")
            return await self.get_backup_earthquake_data(small_area)

    async def fetch_weather_data(self) -> Optional[Dict[str, Any]]:
        """從氣象局取得36小時天氣預報資料 (使用非同步請求)"""
        current_time = datetime.datetime.now().timestamp()
          # 如果快取資料未過期（30分鐘內），直接返回快取
        if (self.weather_cache and 
            current_time - self.weather_cache_time < 1800):
            logger.info("使用快取的天氣預報資料")
            return self.weather_cache

        try:
            url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
            params = {
                'Authorization': self.api_auth,
                'format': 'JSON'
            }
            
            # 構建完整的URL
            param_string = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{param_string}"
            
            # 使用非同步請求獲取資料
            data = await self.fetch_with_retry(full_url, timeout=15, max_retries=3)
            
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

    async def fetch_tsunami_data(self) -> Optional[Dict[str, Any]]:
        """從氣象局取得最新海嘯資料 (使用非同步請求)"""
        current_time = datetime.datetime.now().timestamp()
        
        logger.info("開始獲取海嘯資料")
          # 如果快取資料未過期（5分鐘內），直接返回快取
        if (self.tsunami_cache and 
            current_time - self.tsunami_cache_time < 300):
            logger.info("使用快取的海嘯資料")
            return self.tsunami_cache

        try:
            # 使用海嘯資料API端點
            url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0014-001"
            params = {
                'Authorization': self.api_auth,
                'format': 'JSON'
            }
            
            # 構建完整的URL
            param_string = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{param_string}"
            
            logger.info(f"正在獲取海嘯資料，URL: {full_url}")
            
            # 使用非同步請求獲取資料
            data = await self.fetch_with_retry(full_url, timeout=30, max_retries=3)
            
            if data and isinstance(data, dict):
                # 驗證資料結構
                if 'success' in data and (data['success'] == 'true' or data['success'] is True):
                    # 記錄完整的資料結構，以便調試
                    logger.info(f"海嘯API返回的資料結構: {str(data.keys())}")
                    
                    # 更新快取
                    self.tsunami_cache = data
                    self.tsunami_cache_time = current_time
                    logger.info("成功獲取並更新海嘯資料快取")
                    
                    return data
                else:
                    logger.error(f"海嘯API請求不成功: {data}")
            else:
                logger.error(f"獲取到的海嘯資料格式不正確: {data}")
                
            # 如果請求失敗，檢查是否有快取資料可用
            if self.tsunami_cache:
                logger.warning("使用過期的海嘯資料快取")
                return self.tsunami_cache
                
            return None
                
        except Exception as e:
            logger.error(f"獲取海嘯資料時發生錯誤: {str(e)}")
            
            # 如果發生錯誤，檢查是否有快取資料可用
            if self.tsunami_cache:
                logger.info("發生錯誤，使用海嘯快取資料")
                return self.tsunami_cache
                
            return None

    # 這裡添加其他方法 (如 format_weather_data, format_earthquake_data 等)...

    async def format_earthquake_data(self, eq_data: Dict[str, Any]) -> Optional[discord.Embed]:
        """將地震資料格式化為Discord嵌入訊息"""
        try:
            # 確認必要的欄位是否存在
            if not all(k in eq_data for k in ['ReportContent', 'EarthquakeNo']):
                return None
                
            # 取得地震資訊
            report_content = eq_data.get('ReportContent', '地震資料不完整')
            report_color = eq_data.get('ReportColor', '綠色')
            report_time = eq_data.get('OriginTime', '未知時間')
            report_web = eq_data.get('Web', '')
            report_image = eq_data.get('ReportImageURI', '')
            
            # 設定嵌入顏色
            color = discord.Color.green()
            if report_color == '黃色':
                color = discord.Color.gold()
            elif report_color == '橘色':
                color = discord.Color.orange()
            elif report_color == '紅色':
                color = discord.Color.red()
                
            # 建立嵌入訊息
            embed = discord.Embed(
                title="🌋 地震報告",
                description=report_content,
                color=color,
                url=report_web if report_web else None
            )
            
            # 添加地震相關資訊
            if 'EarthquakeInfo' in eq_data:
                eq_info = eq_data['EarthquakeInfo']
                epicenter = eq_info.get('Epicenter', {})
                magnitude = eq_info.get('EarthquakeMagnitude', {})
                
                location = epicenter.get('Location', '未知位置')
                focal_depth = eq_info.get('FocalDepth', '未知')
                magnitude_value = magnitude.get('MagnitudeValue', '未知')
                
                embed.add_field(
                    name="📍 震央位置",
                    value=location,
                    inline=True
                )
                
                embed.add_field(
                    name="🔍 規模",
                    value=f"{magnitude_value}",
                    inline=True
                )
                
                embed.add_field(
                    name="⬇️ 深度",
                    value=f"{focal_depth} 公里",
                    inline=True
                )
                
            # 添加有感地區資訊
            if 'Intensity' in eq_data and 'ShakingArea' in eq_data['Intensity']:
                max_intensity = "0級"
                max_areas = []
                
                for area in eq_data['Intensity']['ShakingArea']:
                    area_desc = area.get('AreaDesc', '')
                    intensity = area.get('AreaIntensity', '')
                    
                    # 記錄最大震度和對應地區
                    if intensity in ['7級', '6強', '6弱', '5強', '5弱', '4級']:
                        if max_intensity == "0級" or max_intensity < intensity:
                            max_intensity = intensity
                            max_areas = [area_desc]
                        elif max_intensity == intensity:
                            max_areas.append(area_desc)
                
                if max_intensity != "0級" and max_areas:
                    embed.add_field(
                        name=f"⚠️ 最大震度 {max_intensity} 地區",
                        value=", ".join(max_areas),
                        inline=False
                    )
            
            # 添加地震報告圖片
            if report_image:
                embed.set_image(url=report_image)
            
            # 添加頁尾資訊
            embed.set_footer(text=f"地震報告編號: {eq_data.get('EarthquakeNo', '未知')} | 震源時間: {report_time}")
            
            return embed
            
        except Exception as e:
            logger.error(f"格式化地震資料時發生錯誤: {str(e)}")
            return None

    async def format_weather_data(self, location: str) -> Optional[discord.Embed]:
        """將天氣預報資料格式化為Discord嵌入訊息，同一天的資訊顯示在一起"""
        try:
            # 獲取天氣預報資料
            weather_data = await self.fetch_weather_data()
            
            if not weather_data or 'records' not in weather_data or 'location' not in weather_data['records']:
                return None
                
            # 尋找指定地區的天氣資料
            target_location = None
            for loc in weather_data['records']['location']:
                if loc['locationName'] == location:
                    target_location = loc
                    break
                    
            if not target_location:
                return None
                
            # 建立嵌入訊息
            embed = discord.Embed(
                title=f"🌤️ {location}天氣預報",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            # 整理資料，按日期分組
            date_groups = {}
            time_periods = []
            
            # 先獲取所有時間段
            if target_location['weatherElement'] and len(target_location['weatherElement']) > 0:
                for period in target_location['weatherElement'][0]['time']:
                    start_time = period['startTime']
                    end_time = period['endTime']
                    
                    # 提取日期 (忽略時間)
                    date = start_time.split(' ')[0]
                    
                    # 創建日期組
                    if date not in date_groups:
                        date_groups[date] = []
                    
                    # 將時間段添加到對應的日期組
                    date_groups[date].append({
                        'start': start_time,
                        'end': end_time,
                        'data': {}
                    })
                    
                    # 保存時間段順序
                    time_periods.append({
                        'date': date,
                        'start': start_time,
                        'end': end_time
                    })
                    
            # 填充每個時間段的天氣資料
            for element in target_location['weatherElement']:
                element_name = element['elementName']
                
                for i, period in enumerate(element['time']):
                    if i < len(time_periods):
                        date = time_periods[i]['date']
                        start_time = time_periods[i]['start']
                        end_time = time_periods[i]['end']
                        
                        # 在對應的時間段中找到正確的條目
                        for entry in date_groups[date]:
                            if entry['start'] == start_time and entry['end'] == end_time:
                                entry['data'][element_name] = period['parameter']
                                break
            
            # 按日期顯示天氣資料
            for date, periods in date_groups.items():
                # 轉換日期格式為更友好的顯示
                display_date = date.replace('-', '/')
                
                # 添加日期標題
                embed.add_field(
                    name=f"📅 {display_date}",
                    value="天氣預報資訊",
                    inline=False
                )
                
                # 添加每個時間段的詳細資訊
                for period in periods:
                    # 提取時間部分
                    start_hour = period['start'].split(' ')[1].split(':')[0]
                    end_hour = period['end'].split(' ')[1].split(':')[0]
                    time_range = f"{start_hour}:00 - {end_hour}:00"
                    
                    # 獲取天氣資料
                    wx_data = period['data'].get('Wx', {})
                    pop_data = period['data'].get('PoP', {})
                    min_t_data = period['data'].get('MinT', {})
                    max_t_data = period['data'].get('MaxT', {})
                    ci_data = period['data'].get('CI', {})
                    
                    # 取得天氣描述和表情符號
                    wx_desc = wx_data.get('parameterName', '未知')
                    weather_emoji = WEATHER_EMOJI.get(wx_desc, "🌈")
                      # 建立資訊字串
                    info = []
                    info.append(f"**天氣狀況:** {wx_desc}")
                    
                    if pop_data:
                        info.append(f"**降雨機率:** {pop_data.get('parameterName', '未知')}%")
                    if min_t_data and max_t_data:
                        info.append(f"**溫度範圍:** {min_t_data.get('parameterName', '未知')}°C - {max_t_data.get('parameterName', '未知')}°C")
                    
                    if ci_data:
                        info.append(f"**舒適度:** {ci_data.get('parameterName', '未知')}")
                    
                    # 添加到嵌入訊息
                    embed.add_field(
                        name=f"{weather_emoji} {time_range}",
                        value="\n".join(info),
                        inline=True            )
            
            # 添加資料來源和更新時間
            embed.set_footer(text=f"資料來源: 中央氣象署 | 查詢時間: {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
            
            return embed
            
        except Exception as e:
            logger.error(f"格式化天氣資料時發生錯誤: {str(e)}")
            return None
            
    @app_commands.command(name="earthquake", description="查詢最新地震資訊")
    @app_commands.describe(earthquake_type="選擇地震資料類型")
    @app_commands.choices(earthquake_type=[
        app_commands.Choice(name="一般地震", value="normal"),
        app_commands.Choice(name="小區域地震", value="small_area")
    ])
    async def earthquake(self, interaction: discord.Interaction, earthquake_type: str = "normal"):
        """查詢最新地震資訊 - v4 增強版本，具備多格式資料處理能力"""
        await interaction.response.defer()
        
        try:
            # 根據類型獲取地震資料
            small_area = earthquake_type == "small_area"
            eq_data = await self.fetch_earthquake_data(small_area=small_area)
            
            if not eq_data:
                await interaction.followup.send("❌ 無法獲取地震資料，請稍後再試。")
                return
                  # 在日誌中記錄完整的資料結構以進行調試
            logger.info(f"Earthquake 指令獲取的資料結構: {str(eq_data.keys())}")
            
            # 檢查是否為API異常格式（只有resource_id和fields）
            if ('result' in eq_data and isinstance(eq_data['result'], dict) and 
                set(eq_data['result'].keys()) == {'resource_id', 'fields'}):
                logger.warning("earthquake指令：API回傳異常格式，顯示友善錯誤訊息")
                await interaction.followup.send(
                    "❌ 地震資料服務目前無法取得實際資料，可能原因：\n"
                    "• API 授權金鑰問題\n"
                    "• 服務暫時無法使用\n"
                    "• 請稍後再試或聯繫管理員"
                )
                return
              # v4 增強功能：智能資料結構解析
            latest_eq = None
            records = None
            
            # 支援兩種資料結構
            if 'records' in eq_data:
                # 有認證模式：records 在根級別
                records = eq_data['records']
                logger.info("✅ 檢測到有認證模式資料結構")
            elif 'result' in eq_data and 'records' in eq_data['result']:
                # 無認證模式：records 在 result 內
                records = eq_data['result']['records']
                logger.info("✅ 檢測到無認證模式資料結構")
            
            if records:
                # 標準格式檢查
                if isinstance(records, dict) and 'Earthquake' in records:
                    earthquake_data = records['Earthquake']
                    if isinstance(earthquake_data, list) and len(earthquake_data) > 0:
                        latest_eq = earthquake_data[0]
                        logger.info("✅ 使用標準列表格式地震資料")
                    elif isinstance(earthquake_data, dict):
                        latest_eq = earthquake_data
                        logger.info("✅ 使用標準字典格式地震資料")
                        
                # v4 新增：處理2025年新格式 - datasetDescription + Earthquake
                elif isinstance(records, dict) and 'datasetDescription' in records and 'Earthquake' in records:
                    earthquake_data = records['Earthquake']
                    if isinstance(earthquake_data, list) and len(earthquake_data) > 0:
                        latest_eq = earthquake_data[0]
                        logger.info("✅ 使用2025年新格式地震資料")
                    elif isinstance(earthquake_data, dict):
                        latest_eq = earthquake_data
                        logger.info("✅ 使用2025年新格式字典地震資料")
                        
                # v4 新增：處理直接資料格式（無 Earthquake 層級）
                elif isinstance(records, list) and len(records) > 0:
                    # 檢查列表中的第一個元素是否包含地震資料特徵
                    first_record = records[0]
                    if isinstance(first_record, dict) and ('EarthquakeNo' in first_record or 'EarthquakeInfo' in first_record):
                        latest_eq = first_record
                        logger.info("✅ 使用直接列表格式地震資料")
                        
                # v4 新增：處理單一記錄格式
                elif isinstance(records, dict) and ('EarthquakeNo' in records or 'EarthquakeInfo' in records):
                    latest_eq = records
                    logger.info("✅ 使用單一記錄格式地震資料")
                
            # v4 新增：處理缺少 result 或 records 的情況
            elif 'Earthquake' in eq_data:
                earthquake_data = eq_data['Earthquake']
                if isinstance(earthquake_data, list) and len(earthquake_data) > 0:
                    latest_eq = earthquake_data[0]
                    logger.info("✅ 使用根層級地震資料")
                elif isinstance(earthquake_data, dict):
                    latest_eq = earthquake_data
                    logger.info("✅ 使用根層級字典地震資料")
                    
            # v4 新增：處理完全不同的API格式
            elif isinstance(eq_data, dict) and ('EarthquakeNo' in eq_data or 'EarthquakeInfo' in eq_data):
                latest_eq = eq_data
                logger.info("✅ 使用根層級單一地震資料")
            
            # 處理結果
            if latest_eq:
                # v4 增強：在格式化前進行資料完整性檢查和修復
                latest_eq = self.enhance_earthquake_data(latest_eq)
                
                # 格式化為Discord嵌入訊息
                embed = await self.format_earthquake_data(latest_eq)
                
                if embed:
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("❌ 無法解析地震資料，請稍後再試。")
            else:
                logger.warning(f"v4 所有解析方法都失敗，原始資料結構: {str(eq_data)[:200]}...")
                await interaction.followup.send("❌ 目前沒有可用的地震資料，請稍後再試。")
                
        except Exception as e:
            logger.error(f"earthquake指令執行時發生錯誤: {str(e)}")
            await interaction.followup.send("❌ 執行指令時發生錯誤，請稍後再試。")
    
    def enhance_earthquake_data(self, eq_data: Dict[str, Any]) -> Dict[str, Any]:
        """v4 新增：增強地震資料，確保所有必要欄位存在並修復缺失的資料結構"""
        try:
            enhanced_data = eq_data.copy()
            
            # 確保有基本的記錄結構
            if 'records' not in enhanced_data:
                logger.info("🔧 地震資料缺少 records 欄位，正在修復...")
                enhanced_data = {
                    'records': enhanced_data
                }
            
            # 確保記錄中有 Earthquake 結構
            if isinstance(enhanced_data.get('records'), dict):
                records = enhanced_data['records']
                
                # 如果 records 直接包含地震資料，包裝為 Earthquake 結構
                if 'EarthquakeNo' in records or 'EarthquakeInfo' in records:
                    logger.info("🔧 將根層級地震資料包裝為標準 Earthquake 結構...")
                    enhanced_data['records'] = {
                        'Earthquake': [records]
                    }
                # 如果已經有 Earthquake 但是字典格式，轉換為列表格式
                elif 'Earthquake' in records and isinstance(records['Earthquake'], dict):
                    logger.info("🔧 將字典格式 Earthquake 轉換為列表格式...")
                    enhanced_data['records']['Earthquake'] = [records['Earthquake']]
            
            # 確保地震資料完整性
            if 'records' in enhanced_data and 'Earthquake' in enhanced_data['records']:
                earthquakes = enhanced_data['records']['Earthquake']
                if isinstance(earthquakes, list) and len(earthquakes) > 0:
                    eq = earthquakes[0]
                    
                    # 修復缺失的基本欄位
                    if 'EarthquakeNo' not in eq:
                        eq['EarthquakeNo'] = f"UNKNOWN_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                        logger.info("🔧 補充缺失的 EarthquakeNo 欄位")
                    
                    # 確保有基本的地震資訊結構
                    if 'EarthquakeInfo' not in eq:
                        eq['EarthquakeInfo'] = {}
                        logger.info("🔧 補充缺失的 EarthquakeInfo 結構")
                    
                    # 確保有震央位置資訊
                    if 'Epicenter' not in eq['EarthquakeInfo']:
                        eq['EarthquakeInfo']['Epicenter'] = {}
                        logger.info("🔧 補充缺失的 Epicenter 結構")
                    
                    # 確保有規模資訊
                    if 'EarthquakeMagnitude' not in eq['EarthquakeInfo']:
                        eq['EarthquakeInfo']['EarthquakeMagnitude'] = {}
                        logger.info("🔧 補充缺失的 EarthquakeMagnitude 結構")
            
            logger.info("✅ 地震資料結構增強完成")
            return enhanced_data
            
        except Exception as e:
            logger.error(f"增強地震資料時發生錯誤: {str(e)}")
            return eq_data  # 返回原始資料

    @app_commands.command(name="weather", description="查詢天氣預報")
    @app_commands.describe(location="要查詢的地區 (縣市)")
    @app_commands.choices(location=[
        app_commands.Choice(name=loc, value=loc) for loc in TW_LOCATIONS
    ])
    async def weather(self, interaction: discord.Interaction, location: str = None):
        """查詢天氣預報"""
        if location:
            await interaction.response.defer()
            
            try:
                # 獲取並格式化天氣資料
                embed = await self.format_weather_data(location)
                
                if embed:
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("❌ 無法獲取天氣資料，請稍後再試。")
            except Exception as e:
                logger.error(f"weather指令執行時發生錯誤: {str(e)}")
                await interaction.followup.send("❌ 執行指令時發生錯誤，請稍後再試。")
        else:
            # 提供互動式選單
            view = WeatherView(self, interaction.user.id, TW_LOCATIONS)
            await interaction.response.send_message("請選擇要查詢的縣市：", view=view, ephemeral=True)

    @app_commands.command(name="set_earthquake_channel", description="設定地震通知頻道 (需管理員權限)")
    @app_commands.describe(channel="要設定為地震通知頻道的文字頻道")
    async def set_earthquake_channel(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """設定地震通知頻道"""
        # 檢查權限
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 此指令需要管理員權限！", ephemeral=True)
            return
            
        if channel:
            # 檢查機器人是否有該頻道的發送訊息權限
            if not channel.permissions_for(interaction.guild.me).send_messages:
                await interaction.response.send_message("❌ 我沒有在該頻道發送訊息的權限！請選擇另一個頻道或給予我適當的權限。", ephemeral=True)
                return
                
            # 設定通知頻道
            self.notification_channels[interaction.guild.id] = channel.id
              # 初始化最後地震時間
            try:
                eq_data = await self.fetch_earthquake_data()
                if eq_data:
                    # 支援兩種資料結構
                    records = None
                    if 'records' in eq_data:
                        # 有認證模式：records 在根級別
                        records = eq_data['records']
                    elif 'result' in eq_data and 'records' in eq_data['result']:
                        # 無認證模式：records 在 result 內
                        records = eq_data['result']['records']
                    
                    if records and isinstance(records, dict) and 'Earthquake' in records:
                        earthquake_data = records['Earthquake']
                        if isinstance(earthquake_data, list) and len(earthquake_data) > 0:
                            latest_eq = earthquake_data[0]
                            self.last_eq_time[interaction.guild.id] = latest_eq.get('EarthquakeNo', '')
            except Exception as e:
                logger.error(f"初始化最後地震時間時發生錯誤: {str(e)}")
                self.last_eq_time[interaction.guild.id] = ""
                
            await interaction.response.send_message(f"✅ 已將 {channel.mention} 設定為地震通知頻道。當有新的地震報告時，我會在此頻道發送通知。", ephemeral=True)
            
            # 發送測試訊息
            try:
                embed = discord.Embed(
                    title="✅ 地震通知頻道設定成功",
                    description="此頻道已被設定為地震通知頻道。當有新的地震報告時，機器人會在此頻道發送通知。",
                    color=discord.Color.green()
                )
                embed.set_footer(text=f"設定者: {interaction.user} | 設定時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                await channel.send(embed=embed)
            except Exception as e:
                logger.error(f"發送測試訊息時發生錯誤: {str(e)}")
        else:            # 清除設定
            if interaction.guild.id in self.notification_channels:
                del self.notification_channels[interaction.guild.id]
            if interaction.guild.id in self.last_eq_time:
                del self.last_eq_time[interaction.guild.id]
                
            await interaction.response.send_message("✅ 已清除地震通知頻道設定。", ephemeral=True)

    async def format_tsunami_data(self, tsunami_data: Dict[str, Any]) -> Optional[discord.Embed]:
        """將海嘯資料格式化為Discord嵌入訊息"""
        try:
            # 確認必要的欄位是否存在
            if not all(key in tsunami_data for key in ['ReportContent', 'ReportType']):
                return None
                
            # 取得海嘯資訊
            report_content = tsunami_data.get('ReportContent', '海嘯資料不完整')
            report_color = tsunami_data.get('ReportColor', '綠色')
            report_type = tsunami_data.get('ReportType', '海嘯消息')
            report_no = tsunami_data.get('ReportNo', '未知')
            report_web = tsunami_data.get('Web', '')
            
            # 設定嵌入顏色
            color = discord.Color.green()
            if report_color == '黃色':
                color = discord.Color.gold()
            elif report_color == '橘色':
                color = discord.Color.orange()
            elif report_color == '紅色':
                color = discord.Color.red()
                
            # 設置標題
            title = "🌊 海嘯消息"
            if "警報" in report_type:
                title = "⚠️ 海嘯警報"
            elif "解除" in report_type:
                title = "✅ 海嘯警報解除"
                
            # 建立嵌入訊息
            embed = discord.Embed(
                title=title,
                description=report_content,
                color=color,
                url=report_web if report_web else None
            )
            
            # 添加海嘯相關資訊
            if 'EarthquakeInfo' in tsunami_data:
                eq_info = tsunami_data['EarthquakeInfo']
                epicenter = eq_info.get('Epicenter', {})
                magnitude = eq_info.get('EarthquakeMagnitude', {})
                
                location = epicenter.get('Location', '未知位置')
                focal_depth = eq_info.get('FocalDepth', '未知')
                magnitude_value = magnitude.get('MagnitudeValue', '未知')
                origin_time = eq_info.get('OriginTime', '未知時間')
                source = eq_info.get('Source', '未知來源')
                
                embed.add_field(
                    name="📍 地震位置",
                    value=location,
                    inline=True
                )
                
                embed.add_field(
                    name="🔍 規模",
                    value=f"{magnitude_value}",
                    inline=True
                )
                
                embed.add_field(
                    name="⬇️ 深度",
                    value=f"{focal_depth} 公里",
                    inline=True
                )
                
                embed.add_field(
                    name="📊 資料來源",
                    value=source,
                    inline=True
                )
                
                embed.add_field(
                    name="⏰ 發生時間",
                    value=origin_time,
                    inline=True
                )
            
            # 添加影響地區資訊（如果有）
            if 'TsunamiWave' in tsunami_data and 'WarningArea' in tsunami_data['TsunamiWave']:
                warning_areas = tsunami_data['TsunamiWave']['WarningArea']
                if isinstance(warning_areas, list) and warning_areas:
                    area_descriptions = []
                    for area in warning_areas:
                        area_desc = area.get('AreaDesc', '')
                        wave_height = area.get('WaveHeight', '')
                        arrival_time = area.get('ArrivalTime', '')
                        if area_desc:
                            area_info = f"{area_desc} - 預估波高: {wave_height}, 預估抵達時間: {arrival_time}"
                            area_descriptions.append(area_info)
                    
                    if area_descriptions:
                        embed.add_field(
                            name="⚠️ 影響地區",
                            value="\n".join(area_descriptions),
                            inline=False
                        )
            
            # 添加觀測站資訊（如果有）
            if 'TsunamiWave' in tsunami_data and 'TsuStation' in tsunami_data['TsunamiWave']:
                stations = tsunami_data['TsunamiWave']['TsuStation']
                if isinstance(stations, list) and stations:
                    station_info = []
                    for station in stations[:5]:  # 只顯示前5個，避免超過嵌入限制
                        station_name = station.get('StationName', '')
                        wave_height = station.get('WaveHeight', '')
                        arrival_time = station.get('ArrivalTime', '')
                        if station_name:
                            info = f"{station_name} - 觀測波高: {wave_height}, 抵達時間: {arrival_time}"
                            station_info.append(info)
                    
                    if station_info:
                        embed.add_field(
                            name="📡 觀測站資料",
                            value="\n".join(station_info),
                            inline=False
                        )
                        
                        if len(stations) > 5:
                            embed.add_field(
                                name="",
                                value=f"*尚有 {len(stations) - 5} 筆觀測站資料未顯示*",
                                inline=False
                            )
              # 添加頁尾資訊
            footer_text = f"{report_type} 第{report_no}"
            if 'TsunamiNo' in tsunami_data:
                footer_text += f" | 海嘯編號: {tsunami_data.get('TsunamiNo', '未知')}"
                
            embed.set_footer(text=footer_text)
            
            return embed
            
        except Exception as e:
            logger.error(f"格式化海嘯資料時發生錯誤: {str(e)}")
            return None

    @app_commands.command(name="tsunami", description="查詢最新海嘯資訊")
    async def tsunami(self, interaction: discord.Interaction):
        """查詢最新海嘯資訊"""
        await interaction.response.defer()
        
        try:
            # 添加超時處理，防止 Discord 交互超時
            tsunami_data = await asyncio.wait_for(
                self.fetch_tsunami_data(), 
                timeout=8.0  # 8秒超時，留足夠時間給 Discord 回應
            )
            if not tsunami_data:
                await interaction.followup.send("❌ 無法獲取海嘯資料，請稍後再試。")
                return
            
            # 檢查資料結構 - 修正API結構：records是根層級的
            if ('records' not in tsunami_data or 
                'Tsunami' not in tsunami_data['records']):
                logger.warning("tsunami指令：API回傳異常格式，顯示友善錯誤訊息")
                logger.info(f"海嘯資料實際結構: {list(tsunami_data.keys())}")
                if 'records' in tsunami_data:
                    logger.info(f"records內容: {list(tsunami_data['records'].keys()) if isinstance(tsunami_data['records'], dict) else type(tsunami_data['records'])}")
                await interaction.followup.send("❌ 海嘯資料服務目前無法取得實際資料，請稍後再試。")
                return
                
            # 取得最新海嘯資料
            tsunami_records = tsunami_data['records']['Tsunami']
            if not tsunami_records or not isinstance(tsunami_records, list) or len(tsunami_records) == 0:
                await interaction.followup.send("✅ 目前沒有海嘯資料或警報。")
                return
                
            # 取得最新一筆資料
            latest_tsunami = tsunami_records[0]
            
            # 格式化為Discord嵌入訊息
            embed = await self.format_tsunami_data(latest_tsunami)
            
            if embed:
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ 無法解析海嘯資料，請稍後再試。")
                
        except asyncio.TimeoutError:
            logger.warning("tsunami指令：API請求超時")
            await interaction.followup.send("❌ 海嘯資料查詢超時，請稍後再試。")
        except Exception as e:
            logger.error(f"tsunami指令執行時發生錯誤: {str(e)}")
            await interaction.followup.send("❌ 執行指令時發生錯誤，請稍後再試。")

    async def get_backup_earthquake_data(self, small_area: bool = False) -> Optional[Dict[str, Any]]:
        """當 API 失敗時提供備用地震資料"""
        logger.info("使用備用地震資料")
        
        # 創建模擬的地震資料結構
        current_time = datetime.datetime.now()
        
        backup_data = {
            "success": "true",
            "result": {
                "resource_id": "E-A0016-001" if small_area else "E-A0015-001",
                "records": {
                    "Earthquake": [{
                        "EarthquakeNo": 999999,
                        "ReportType": "小區域有感地震報告" if small_area else "有感地震報告",
                        "ReportContent": f"備用地震資料 - API 暫時不可用 (時間: {current_time.strftime('%Y-%m-%d %H:%M:%S')})",
                        "ReportColor": "綠色",
                        "ReportRemark": "此為備用資料，請稍後重試以獲取最新地震資訊",
                        "Web": "https://www.cwa.gov.tw/V8/C/E/index.html",
                        "ShakemapImageURI": "",
                        "ReportImageURI": "",
                        "EarthquakeInfo": {
                            "OriginTime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "Source": "中央氣象署",
                            "FocalDepth": "資料更新中",
                            "Epicenter": {
                                "Location": "資料更新中",
                                "EpicenterLatitude": 0.0,
                                "EpicenterLongitude": 0.0
                            },
                            "EarthquakeMagnitude": {
                                "MagnitudeType": "ML",
                                "MagnitudeValue": 0.0
                            }
                        },                        "Intensity": {
                            "ShakingArea": [{
                                "AreaDesc": "API 暫時無法提供資料",
                                "CountyName": "",
                                "InfoStatus": "資料更新中",
                                "AreaIntensity": "0級"
                            }]
                        }
                    }]
                }
            }
        }
        
        return backup_data

async def setup(bot):
    await bot.add_cog(InfoCommands(bot))
