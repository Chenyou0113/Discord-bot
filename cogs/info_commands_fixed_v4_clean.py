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
import os
from dotenv import load_dotenv

load_dotenv()

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

class InfoCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.earthquake_cache = {}
        self.tsunami_cache = {}  # 新增海嘯資料快取
        self.weather_alert_cache = {}
        self.reservoir_cache = {}
        self.water_info_cache = {}  # 新增水情資料快取
        self.cache_time = 0
        self.tsunami_cache_time = 0  # 新增海嘯資料快取時間
        self.weather_alert_cache_time = 0
        self.reservoir_cache_time = 0
        self.water_info_cache_time = 0  # 新增水情資料快取時間
        
        # 從環境變數讀取 CWA API 密鑰
        import os
        from dotenv import load_dotenv
        load_dotenv()
        self.api_auth = os.getenv('CWA_API_KEY')
        if not self.api_auth:
            logger.error("❌ 錯誤: 找不到 CWA_API_KEY 環境變數")
            logger.info("請在 .env 檔案中設定 CWA_API_KEY=您的中央氣象署API密鑰")
        
        self.notification_channels = {}
        self.last_eq_time = {}
        self.check_interval = 300  # 每5分鐘檢查一次
          # 建立 aiohttp 工作階段
        self.session = None

    async def _check_admin(self, interaction: discord.Interaction) -> bool:
        """檢查使用者是否為機器人開發者"""
        developer_id = os.getenv('BOT_DEVELOPER_ID')
        if developer_id and str(interaction.user.id) == developer_id:
            return True
        
        await interaction.response.send_message("❌ 此指令僅限機器人開發者使用！", ephemeral=True)
        logger.warning(f"用戶 {interaction.user.name} ({interaction.user.id}) 嘗試使用管理員指令")
        return False
        self.eq_check_task = None
        
    async def cog_load(self):
        """Cog 載入時的初始化"""
        await self.init_aiohttp_session()
        # 開始地震監控
        self.eq_check_task = asyncio.create_task(self.check_earthquake_updates())

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
        if self.eq_check_task:
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
    
    async def fetch_with_retry(self, url: str, params: Dict[str, Any] = None, timeout: int = 20, max_retries: int = 3) -> Optional[Dict[str, Any]]:
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
                async with self.session.get(url, params=params, timeout=timeout) as response:
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
          # 嘗試多種 API 調用方式 - 優先使用有認證模式
        api_attempts = [
            {
                "name": "有認證模式", 
                "params": {
                    'Authorization': self.api_auth,
                    'limit': 1,
                    'format': 'JSON'
                }
            },
            {
                "name": "無認證模式",
                "params": {
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
                    if data and isinstance(data, dict):                        # 驗證資料結構
                        if 'success' in data and (data['success'] == 'true' or data['success'] is True):
                            # 檢查是否為API異常格式（只有欄位定義，無實際資料）
                            # 修復：有認證模式的 result 也會包含 records
                            if ('result' in data and isinstance(data['result'], dict) and 
                                set(data['result'].keys()) == {'resource_id', 'fields'} and 
                                'records' not in data):
                                logger.warning(f"API回傳異常資料結構（{attempt['name']}失敗），嘗試下一種方式")
                                continue  # 嘗試下一種 API 調用方式
                            
                            # 檢查是否有實際的地震資料 (支援兩種資料結構)
                            records_data = None
                            if 'records' in data:
                                # 有認證模式：records 在根級別
                                records_data = data['records']
                                logger.info(f"使用有認證模式資料結構 (根級別 records)")
                            elif 'result' in data and 'records' in data.get('result', {}):
                                # 無認證模式：records 在 result 內
                                records_data = data['result']['records']
                                logger.info(f"使用無認證模式資料結構 (result.records)")
                            
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
                                logger.warning(f"records_data 內容: {records_data}")
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

    async def fetch_weather_station_data(self) -> Optional[Dict[str, Any]]:
        """獲取自動氣象站觀測資料"""
        try:
            url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001"
            params = {
                'Authorization': self.api_auth,
                'format': 'JSON'
            }
            
            logger.info("開始獲取自動氣象站觀測資料")
            weather_station_data = await self.fetch_with_retry(url, params=params)
            
            if weather_station_data:
                logger.info("✅ 成功獲取自動氣象站觀測資料")
                return weather_station_data
            else:
                logger.warning("❌ 無法獲取自動氣象站觀測資料")
                return None
                
        except Exception as e:
            logger.error(f"獲取自動氣象站觀測資料時發生錯誤: {str(e)}")
            return None

    async def fetch_weather_station_info(self) -> Optional[Dict[str, Any]]:
        """獲取氣象測站基本資料"""
        try:
            url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/C-B0074-001"
            params = {
                'Authorization': self.api_auth,
                'format': 'JSON'
            }
            
            logger.info("開始獲取氣象測站基本資料")
            station_info_data = await self.fetch_with_retry(url, params=params)
            
            if station_info_data:
                logger.info("✅ 成功獲取氣象測站基本資料")
                return station_info_data
            else:
                logger.warning("❌ 無法獲取氣象測站基本資料")
                return None
                
        except Exception as e:
            logger.error(f"獲取氣象測站基本資料時發生錯誤: {str(e)}")
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
            # 優先從 EarthquakeInfo 獲取 OriginTime，如果沒有則從根級別獲取
            report_time = eq_data.get('OriginTime', '未知時間')
            if 'EarthquakeInfo' in eq_data and 'OriginTime' in eq_data['EarthquakeInfo']:
                report_time = eq_data['EarthquakeInfo']['OriginTime']
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
                return            # 在日誌中記錄完整的資料結構以進行調試
            logger.info(f"Earthquake 指令獲取的資料結構: {str(eq_data.keys())}")
              # 檢查是否為API異常格式（只有resource_id和fields，無實際資料）
            # 修復：正確檢查異常格式 - 真正的異常是只有result含有resource_id和fields，且沒有任何records
            if ('result' in eq_data and isinstance(eq_data['result'], dict) and 
                set(eq_data['result'].keys()) == {'resource_id', 'fields'} and 
                'records' not in eq_data and 'records' not in eq_data.get('result', {})):
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
                logger.info("✅ 使用根層級單一地震資料")            # 處理結果
            if latest_eq:
                # v4 增強：在格式化前進行資料完整性檢查和修復
                enhanced_data = self.enhance_earthquake_data(latest_eq)
                
                # 從增強後的數據中提取實際的地震記錄用於格式化
                earthquake_record = None
                if 'records' in enhanced_data and 'Earthquake' in enhanced_data['records']:
                    earthquakes = enhanced_data['records']['Earthquake']
                    if isinstance(earthquakes, list) and len(earthquakes) > 0:
                        earthquake_record = earthquakes[0]
                elif isinstance(enhanced_data, dict) and ('EarthquakeNo' in enhanced_data or 'EarthquakeInfo' in enhanced_data):
                    earthquake_record = enhanced_data
                
                if earthquake_record:
                    # 格式化為Discord嵌入訊息
                    embed = await self.format_earthquake_data(earthquake_record)
                    
                    if embed:
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send("❌ 無法解析地震資料，請稍後再試。")
                else:
                    await interaction.followup.send("❌ 地震資料結構異常，無法解析。")
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

    @app_commands.command(name="set_earthquake_channel", description="設定地震通知頻道 (需管理員權限)")
    @app_commands.describe(channel="要設定為地震通知頻道的文字頻道")
    async def set_earthquake_channel(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """設定地震通知頻道"""
        # 檢查權限
        if not await self._check_admin(interaction):
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
                        }                    }]
                }
            }
        }
        return backup_data



    async def format_weather_station_data(self, station_id: str = None, location: str = None) -> Optional[discord.Embed]:
        """將自動氣象站觀測資料格式化為Discord嵌入訊息"""
        try:
            # 獲取氣象站觀測資料
            station_data = await self.fetch_weather_station_data()
            
            if not station_data or 'records' not in station_data:
                return None
            
            records = station_data['records']
            if 'Station' not in records:
                return None
                
            stations = records['Station']
            
            # 如果指定了測站ID，尋找該測站
            if station_id:
                target_station = None
                for station in stations:
                    if station.get('StationId') == station_id:
                        target_station = station
                        break
                
                if not target_station:
                    return None
                    
                return self._create_single_station_embed(target_station)
            
            # 如果指定了地區名稱，尋找該地區的測站
            elif location:
                target_stations = []
                for station in stations:
                    station_name = station.get('StationName', '')
                    county_name = station.get('GeoInfo', {}).get('CountyName', '')
                    if (location in station_name or station_name in location or 
                        location in county_name or county_name in location):
                        target_stations.append(station)
                
                if not target_stations:
                    return None
                
                if len(target_stations) == 1:
                    return self._create_single_station_embed(target_stations[0])
                else:
                    return self._create_multiple_stations_embed(target_stations, location)
            
            # 如果沒有指定條件，顯示主要縣市的概況
            else:
                return self._create_overview_embed(stations)
                
        except Exception as e:
            logger.error(f"格式化氣象站資料時發生錯誤: {str(e)}")
            return None

    def _create_single_station_embed(self, station_data: Dict[str, Any]) -> discord.Embed:
        """創建單一測站的詳細資料嵌入"""
        station_name = station_data.get('StationName', '未知測站')
        station_id = station_data.get('StationId', '未知')
        
        embed = discord.Embed(
            title=f"🌡️ {station_name} 氣象觀測",
            description=f"測站代碼: {station_id}",
            color=discord.Color.blue()
        )
        
        # 獲取觀測時間
        obs_time = station_data.get('ObsTime', {}).get('DateTime', '未知時間')
        
        # 獲取氣象要素
        weather_element = station_data.get('WeatherElement', {})
        
        # 解析氣象要素
        temp = weather_element.get('AirTemperature', 'N/A')
        humidity = weather_element.get('RelativeHumidity', 'N/A')
        pressure = weather_element.get('AirPressure', 'N/A')
        wind_dir = weather_element.get('WindDirection', 'N/A')
        wind_speed = weather_element.get('WindSpeed', 'N/A')
        weather = weather_element.get('Weather', 'N/A')
        rainfall = weather_element.get('Now', {}).get('Precipitation', 'N/A')
        
        if weather != 'N/A':
            embed.add_field(name="☁️ 天氣", value=weather, inline=True)
        if temp != 'N/A':
            embed.add_field(name="🌡️ 溫度", value=f"{temp}°C", inline=True)
        if humidity != 'N/A':
            embed.add_field(name="💧 相對濕度", value=f"{humidity}%", inline=True)
        if pressure != 'N/A':
            embed.add_field(name="📊 氣壓", value=f"{pressure} hPa", inline=True)
        if wind_dir != 'N/A':
            embed.add_field(name="🧭 風向", value=f"{wind_dir}°", inline=True)
        if wind_speed != 'N/A':
            embed.add_field(name="💨 風速", value=f"{wind_speed} m/s", inline=True)
        if rainfall != 'N/A':
            embed.add_field(name="🌧️ 降雨量", value=f"{rainfall} mm", inline=True)
        
        # 添加地理資訊
        geo_info = station_data.get('GeoInfo', {})
        county = geo_info.get('CountyName', '')
        town = geo_info.get('TownName', '')
        if county and town:
            embed.add_field(name="📍 位置", value=f"{county}{town}", inline=True)
        
        embed.set_footer(text=f"觀測時間: {obs_time} | 資料來源: 中央氣象署")
        return embed

    def _create_multiple_stations_embed(self, stations: List[Dict[str, Any]], location: str) -> discord.Embed:
        """創建多個測站的概況嵌入"""
        embed = discord.Embed(
            title=f"🌡️ {location} 地區氣象觀測",
            description=f"找到 {len(stations)} 個測站",
            color=discord.Color.blue()
        )
        
        for station in stations[:10]:  # 最多顯示10個測站
            station_name = station.get('StationName', '未知測站')
            station_id = station.get('StationId', '未知')
            
            weather_element = station.get('WeatherElement', {})
            temp = weather_element.get('AirTemperature', 'N/A')
            humidity = weather_element.get('RelativeHumidity', 'N/A')
            
            temp_str = f"{temp}°C" if temp != 'N/A' else "N/A"
            humidity_str = f"{humidity}%" if humidity != 'N/A' else "N/A"
            
            embed.add_field(
                name=f"📍 {station_name} ({station_id})",
                value=f"🌡️{temp_str} 💧{humidity_str}",
                inline=True
            )
        
        obs_time = stations[0].get('ObsTime', {}).get('DateTime', '未知時間') if stations else '未知時間'
        embed.set_footer(text=f"觀測時間: {obs_time} | 資料來源: 中央氣象署")
        return embed

    def _create_overview_embed(self, stations: List[Dict[str, Any]]) -> discord.Embed:
        """創建全台氣象概況嵌入"""
        embed = discord.Embed(
            title="🌡️ 全台氣象觀測概況",
            description="主要縣市氣象觀測資料",
            color=discord.Color.blue()
        )
        
        # 主要縣市測站代碼
        major_stations = {
            '466920': '臺北',
            '467410': '板橋', 
            'C0C480': '桃園',
            '467490': '新竹',
            '467440': '臺中',
            '467480': '臺南',
            '467570': '高雄',
            '466990': '宜蘭',
            '467660': '花蓮',
            '467770': '臺東'
        }
        
        found_stations = 0
        for station in stations:
            station_id = station.get('StationId', '')
            if station_id in major_stations and found_stations < 8:
                station_name = major_stations[station_id]
                
                weather_element = station.get('WeatherElement', {})
                temp = weather_element.get('AirTemperature', 'N/A')
                humidity = weather_element.get('RelativeHumidity', 'N/A')
                
                temp_str = f"{temp}°C" if temp != 'N/A' else "N/A"
                humidity_str = f"{humidity}%" if humidity != 'N/A' else "N/A"
                
                embed.add_field(
                    name=f"📍 {station_name}",
                    value=f"🌡️{temp_str}\n💧{humidity_str}",
                    inline=True
                )
                found_stations += 1
        
        obs_time = stations[0].get('ObsTime', {}).get('DateTime', '未知時間') if stations else '未知時間' 
        embed.set_footer(text=f"觀測時間: {obs_time} | 資料來源: 中央氣象署")
        return embed

# 氣象測站資料翻頁視圖類
class WeatherStationView(View):
    """氣象站資料翻頁視圖"""
    def __init__(self, cog, user_id: int, stations: List[Dict[str, Any]], query_type: str = "multiple", location: str = ""):
        super().__init__(timeout=300)  # 5分鐘超時
        self.cog = cog
        self.user_id = user_id
        self.stations = stations
        self.query_type = query_type  # "multiple", "overview", "single"
        self.location = location
        self.current_page = 0
        self.stations_per_page = 5  # 每頁顯示5個測站
        self.total_pages = max(1, (len(stations) + self.stations_per_page - 1) // self.stations_per_page)
        
        self._update_buttons()
    
    def _update_buttons(self):
        """更新按鈕狀態"""
        self.clear_items()
        
        # 只有在多頁時才顯示翻頁按鈕
        if self.total_pages > 1:
            # 上一頁按鈕
            prev_button = discord.ui.Button(
                label="◀️ 上一頁",
                style=discord.ButtonStyle.primary,
                disabled=self.current_page == 0
            )
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
            
            # 頁面資訊按鈕
            page_button = discord.ui.Button(
                label=f"{self.current_page + 1}/{self.total_pages}",
                style=discord.ButtonStyle.secondary,
                disabled=True
            )
            self.add_item(page_button)
            
            # 下一頁按鈕
            next_button = discord.ui.Button(
                label="下一頁 ▶️",
                style=discord.ButtonStyle.primary,
                disabled=self.current_page >= self.total_pages - 1
            )
            next_button.callback = self.next_page
            self.add_item(next_button)
        
        # 重新整理按鈕
        refresh_button = discord.ui.Button(
            label="🔄 重新整理",
            style=discord.ButtonStyle.success
        )
        refresh_button.callback = self.refresh_data
        self.add_item(refresh_button)
    
    async def previous_page(self, interaction: discord.Interaction):
        """上一頁"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("⚠️ 請使用自己的氣象站選單！", ephemeral=True)
            return
        
        if self.current_page > 0:
            self.current_page -= 1
            await self._update_message(interaction)
    
    async def next_page(self, interaction: discord.Interaction):
        """下一頁"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("⚠️ 請使用自己的氣象站選單！", ephemeral=True)
            return
        
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await self._update_message(interaction)
    
    async def refresh_data(self, interaction: discord.Interaction):
        """重新整理資料"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("⚠️ 請使用自己的氣象站選單！", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            # 重新獲取氣象站資料
            station_data = await self.cog.fetch_weather_station_data()
            if station_data and 'records' in station_data:
                records = station_data['records']
                if 'Station' in records:
                    self.stations = records['Station']
                    
                    # 根據查詢類型重新篩選資料
                    if self.query_type == "multiple" and self.location:
                        filtered_stations = []
                        for station in self.stations:
                            station_name = station.get('StationName', '')
                            county_name = station.get('GeoInfo', {}).get('CountyName', '')
                            if (self.location in station_name or station_name in self.location or 
                                self.location in county_name or county_name in self.location):
                                filtered_stations.append(station)
                        self.stations = filtered_stations
                    
                    # 重新計算總頁數
                    self.total_pages = max(1, (len(self.stations) + self.stations_per_page - 1) // self.stations_per_page)
                    
                    # 確保當前頁面不超出範圍
                    if self.current_page >= self.total_pages:
                        self.current_page = max(0, self.total_pages - 1)
                    
                    await self._update_message(interaction)
                else:
                    await interaction.followup.send("❌ 重新整理失敗：無法獲取氣象站資料", ephemeral=True)
            else:
                await interaction.followup.send("❌ 重新整理失敗：API 回應異常", ephemeral=True)
                
        except Exception as e:
            logger.error(f"重新整理氣象站資料時發生錯誤: {str(e)}")
            await interaction.followup.send("❌ 重新整理時發生錯誤，請稍後再試", ephemeral=True)
    
    async def _update_message(self, interaction: discord.Interaction):
        """更新訊息內容"""
        try:
            embed = self._create_current_page_embed()
            self._update_buttons()
            await interaction.response.edit_message(embed=embed, view=self)
        except discord.InteractionResponse:
            # 如果回應已經被處理，使用 edit_original_response
            embed = self._create_current_page_embed()
            self._update_buttons()
            await interaction.edit_original_response(embed=embed, view=self)
    
    def _create_current_page_embed(self) -> discord.Embed:
        """創建當前頁面的嵌入訊息"""
        if self.query_type == "multiple":
            return self._create_paginated_multiple_stations_embed()
        elif self.query_type == "overview":
            return self._create_paginated_overview_embed()
        else:
            # 單一測站不需要翻頁
            return self.cog._create_single_station_embed(self.stations[0])
    
    def _create_paginated_multiple_stations_embed(self) -> discord.Embed:
        """創建分頁的多測站嵌入"""
        start_idx = self.current_page * self.stations_per_page
        end_idx = min(start_idx + self.stations_per_page, len(self.stations))
        current_stations = self.stations[start_idx:end_idx]
        
        embed = discord.Embed(
            title=f"🌡️ {self.location} 地區氣象觀測",
            description=f"第 {self.current_page + 1}/{self.total_pages} 頁 (共 {len(self.stations)} 個測站)",
            color=discord.Color.blue()
        )
        
        for station in current_stations:
            station_name = station.get('StationName', '未知測站')
            station_id = station.get('StationId', '未知')
            
            weather_element = station.get('WeatherElement', {})
            temp = weather_element.get('AirTemperature', 'N/A')
            humidity = weather_element.get('RelativeHumidity', 'N/A')
            weather = weather_element.get('Weather', 'N/A')
            
            temp_str = f"{temp}°C" if temp != 'N/A' else "N/A"
            humidity_str = f"{humidity}%" if humidity != 'N/A' else "N/A"
            weather_str = f" {weather}" if weather != 'N/A' else ""
            
            # 獲取地理位置
            geo_info = station.get('GeoInfo', {})
            county = geo_info.get('CountyName', '')
            town = geo_info.get('TownName', '')
            location_str = f"{county}{town}" if county and town else ""
            
            embed.add_field(
                name=f"📍 {station_name} ({station_id})",
                value=f"🌡️ {temp_str} | 💧 {humidity_str}{weather_str}\n📍 {location_str}",
                inline=False
            )
        
        obs_time = current_stations[0].get('ObsTime', {}).get('DateTime', '未知時間') if current_stations else '未知時間'
        embed.set_footer(text=f"觀測時間: {obs_time} | 資料來源: 中央氣象署")
        return embed
    
    def _create_paginated_overview_embed(self) -> discord.Embed:
        """創建分頁的全台概況嵌入"""
        # 全台概況通常不需要翻頁，但為了一致性保留此方法
        return self.cog._create_overview_embed(self.stations)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """檢查互動權限"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("⚠️ 這不是您的氣象站選單！", ephemeral=True)
            return False
        return True

# 測站基本資料翻頁視圖類
class StationInfoView(discord.ui.View):
    def __init__(self, cog, user_id: int, stations: List[Dict[str, Any]], county: str = None, status: str = "現存測站"):
        super().__init__(timeout=300)
        self.cog = cog
        self.user_id = user_id
        self.stations = stations
        self.county = county
        self.status = status
        self.current_page = 0
        self.stations_per_page = 5
        self.total_pages = (len(stations) + self.stations_per_page - 1) // self.stations_per_page
        
        self._update_buttons()

    def _update_buttons(self):
        """更新按鈕狀態"""
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= self.total_pages - 1

    @discord.ui.button(label='◀️ 上一頁', style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """上一頁按鈕"""
        self.current_page = max(0, self.current_page - 1)
        self._update_buttons()
        embed = self._create_current_page_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='▶️ 下一頁', style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """下一頁按鈕"""
        self.current_page = min(self.total_pages - 1, self.current_page + 1)
        self._update_buttons()
        embed = self._create_current_page_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='🔄 重新整理', style=discord.ButtonStyle.primary)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """重新整理按鈕"""
        await interaction.response.defer()
        try:
            # 重新獲取資料
            station_info_data = await self.cog.fetch_weather_station_info()
            if station_info_data and 'records' in station_info_data:
                stations = station_info_data['records']['data']['stationStatus']['station']
                
                # 重新篩選
                filtered_stations = []
                if self.county:
                    for station in stations:
                        station_county = station.get('CountyName', '')
                        if self.county in station_county or station_county in self.county:
                            if self.status == "all" or station.get('status', '') == self.status:
                                filtered_stations.append(station)
                else:
                    for station in stations:
                        if self.status == "all" or station.get('status', '') == self.status:
                            filtered_stations.append(station)
                    
                self.stations = filtered_stations[:20]  # 限制20個
                self.total_pages = (len(self.stations) + self.stations_per_page - 1) // self.stations_per_page
                self.current_page = min(self.current_page, self.total_pages - 1)
                self._update_buttons()
            
            embed = self._create_current_page_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        except Exception as e:
            logger.error(f"重新整理測站資料時發生錯誤: {str(e)}")
            await interaction.followup.send("❌ 重新整理時發生錯誤", ephemeral=True)

    def _create_current_page_embed(self) -> discord.Embed:
        """創建當前頁面的嵌入訊息"""
        start_idx = self.current_page * self.stations_per_page
        end_idx = min(start_idx + self.stations_per_page, len(self.stations))
        current_stations = self.stations[start_idx:end_idx]
        
        title = f"🏢 氣象測站基本資料"
        if self.county:
            title += f" - {self.county}"
        if self.status != "all":
            title += f" ({self.status})"
            
        embed = discord.Embed(
            title=title,
            description=f"第 {self.current_page + 1}/{self.total_pages} 頁 (共 {len(self.stations)} 個測站)",
            color=discord.Color.blue()
        )
        
        for station in current_stations:
            station_name = station.get('StationName', '未知測站')
            station_id = station.get('StationID', '未知')
            station_status = station.get('status', '未知狀態')
            county_name = station.get('CountyName', 'N/A')
            altitude = station.get('StationAltitude', 'N/A')
            start_date = station.get('StationStartDate', 'N/A')
            location = station.get('Location', 'N/A')
            
            status_emoji = "🟢" if station_status == "現存測站" else "🔴"
            altitude_str = f" | 🏔️ {altitude}m" if altitude != 'N/A' else ""
            date_str = f" | 📅 自 {start_date}" if start_date != 'N/A' else ""
            
            location_display = location[:50] + "..." if len(location) > 50 else location
            
            embed.add_field(
                name=f"{status_emoji} {station_name} ({station_id})",
                value=f"📍 {county_name}\n🏠 {location_display}{altitude_str}{date_str}",
                inline=False
            )
        
        embed.set_footer(text="資料來源: 中央氣象署 | 使用 /station_info 查詢單一測站詳細資料")
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """檢查互動權限"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("⚠️ 這不是您的測站資料選單！", ephemeral=True)
            return False
        return True

async def setup(bot):
    await bot.add_cog(InfoCommands(bot))
