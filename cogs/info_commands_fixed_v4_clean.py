import discord
from discord import app_commands
from discord.ext import commands
import datetime
import aiohttp
import xmltodict
import logging
import asyncio
import ssl
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

# 台鐵車站資料按縣市分類
TRA_STATIONS = {
    "基隆市": [
        {"name": "基隆", "id": "0900"},
        {"name": "三坑", "id": "0910"},
        {"name": "八堵", "id": "0920"}
    ],
    "臺北市": [
        {"name": "七堵", "id": "0930"},
        {"name": "百福", "id": "0940"},
        {"name": "五堵", "id": "0950"},
        {"name": "汐止", "id": "0960"},
        {"name": "汐科", "id": "0970"},
        {"name": "南港", "id": "1000"},
        {"name": "松山", "id": "1010"},
        {"name": "臺北", "id": "1020"},
        {"name": "萬華", "id": "1030"}
    ],
    "新北市": [
        {"name": "板橋", "id": "1040"},
        {"name": "浮洲", "id": "1050"},
        {"name": "樹林", "id": "1060"},
        {"name": "南樹林", "id": "1070"},
        {"name": "山佳", "id": "1080"},
        {"name": "鶯歌", "id": "1090"},
        {"name": "福隆", "id": "0140"},
        {"name": "貢寮", "id": "0150"},
        {"name": "雙溪", "id": "0160"},
        {"name": "牡丹", "id": "0170"},
        {"name": "三貂嶺", "id": "0180"},
        {"name": "大華", "id": "0190"},
        {"name": "十分", "id": "0200"},
        {"name": "望古", "id": "0210"},
        {"name": "嶺腳", "id": "0220"},
        {"name": "平溪", "id": "0230"},
        {"name": "菁桐", "id": "0240"}
    ],
    "桃園市": [
        {"name": "桃園", "id": "1100"},
        {"name": "內壢", "id": "1110"},
        {"name": "中壢", "id": "1120"},
        {"name": "埔心", "id": "1130"},
        {"name": "楊梅", "id": "1140"},
        {"name": "富岡", "id": "1150"}
    ],
    "新竹縣": [
        {"name": "新富", "id": "1160"},
        {"name": "北湖", "id": "1170"},
        {"name": "湖口", "id": "1180"},
        {"name": "新豐", "id": "1190"},
        {"name": "竹北", "id": "1200"}
    ],
    "新竹市": [
        {"name": "北新竹", "id": "1210"},
        {"name": "新竹", "id": "1220"},
        {"name": "三姓橋", "id": "1230"},
        {"name": "香山", "id": "1240"}
    ],
    "苗栗縣": [
        {"name": "崎頂", "id": "1250"},
        {"name": "竹南", "id": "1260"},
        {"name": "談文", "id": "1270"},
        {"name": "大山", "id": "1280"},
        {"name": "後龍", "id": "1290"},
        {"name": "龍港", "id": "1300"},
        {"name": "白沙屯", "id": "1310"},
        {"name": "新埔", "id": "1320"},
        {"name": "通霄", "id": "1330"},
        {"name": "苑裡", "id": "1340"},
        {"name": "造橋", "id": "1351"},
        {"name": "豐富", "id": "1361"},
        {"name": "苗栗", "id": "1371"},
        {"name": "南勢", "id": "1381"},
        {"name": "銅鑼", "id": "1391"},
        {"name": "三義", "id": "1401"}
    ],
    "臺中市": [
        {"name": "日南", "id": "1350"},
        {"name": "大甲", "id": "1360"},
        {"name": "臺中港", "id": "1370"},
        {"name": "清水", "id": "1380"},
        {"name": "沙鹿", "id": "1390"},
        {"name": "龍井", "id": "1400"},
        {"name": "大肚", "id": "1410"},
        {"name": "追分", "id": "1420"},
        {"name": "泰安", "id": "1411"},
        {"name": "后里", "id": "1421"},
        {"name": "豐原", "id": "1431"},
        {"name": "栗林", "id": "1441"},
        {"name": "潭子", "id": "1451"},
        {"name": "頭家厝", "id": "1461"},
        {"name": "松竹", "id": "1471"},
        {"name": "太原", "id": "1481"},
        {"name": "精武", "id": "1491"},
        {"name": "臺中", "id": "1500"},
        {"name": "五權", "id": "1510"},
        {"name": "大慶", "id": "1520"},
        {"name": "烏日", "id": "1530"},
        {"name": "新烏日", "id": "1540"}
    ],
    "彰化縣": [
        {"name": "成功", "id": "1430"},
        {"name": "彰化", "id": "1550"},
        {"name": "花壇", "id": "1560"},
        {"name": "大村", "id": "1570"},
        {"name": "員林", "id": "1580"},
        {"name": "永靖", "id": "1590"},
        {"name": "社頭", "id": "1600"},
        {"name": "田中", "id": "1610"},
        {"name": "二水", "id": "1620"}
    ],
    "雲林縣": [
        {"name": "林內", "id": "1630"},
        {"name": "石榴", "id": "1640"},
        {"name": "斗六", "id": "1650"},
        {"name": "斗南", "id": "1660"},
        {"name": "石龜", "id": "1670"}
    ],
    "嘉義縣": [
        {"name": "大林", "id": "1680"},
        {"name": "民雄", "id": "1690"},
        {"name": "水上", "id": "1700"},
        {"name": "南靖", "id": "1710"}
    ],
    "嘉義市": [
        {"name": "嘉義", "id": "1720"}
    ],
    "臺南市": [
        {"name": "後壁", "id": "1730"},
        {"name": "新營", "id": "1740"},
        {"name": "柳營", "id": "1750"},
        {"name": "林鳳營", "id": "1760"},
        {"name": "隆田", "id": "1770"},
        {"name": "拔林", "id": "1780"},
        {"name": "善化", "id": "1790"},
        {"name": "南科", "id": "1800"},
        {"name": "新市", "id": "1810"},
        {"name": "永康", "id": "1820"},
        {"name": "大橋", "id": "1830"},
        {"name": "臺南", "id": "1840"},
        {"name": "保安", "id": "1850"},
        {"name": "仁德", "id": "1860"},
        {"name": "中洲", "id": "1870"},
        {"name": "長榮大學", "id": "1880"},
        {"name": "沙崙", "id": "1890"}
    ],
    "高雄市": [
        {"name": "大湖", "id": "1900"},
        {"name": "路竹", "id": "1910"},
        {"name": "岡山", "id": "1920"},
        {"name": "橋頭", "id": "1930"},
        {"name": "楠梓", "id": "1940"},
        {"name": "新左營", "id": "1950"},
        {"name": "左營", "id": "1960"},
        {"name": "內惟", "id": "1970"},
        {"name": "美術館", "id": "1980"},
        {"name": "鼓山", "id": "1990"},
        {"name": "三塊厝", "id": "2000"},
        {"name": "高雄", "id": "2010"},
        {"name": "民族", "id": "2020"},
        {"name": "科工館", "id": "2030"},
        {"name": "正義", "id": "2040"},
        {"name": "鳳山", "id": "2050"},
        {"name": "後庄", "id": "2060"},
        {"name": "九曲堂", "id": "2070"}
    ],
    "屏東縣": [
        {"name": "六塊厝", "id": "2080"},
        {"name": "屏東", "id": "2090"},
        {"name": "歸來", "id": "2100"},
        {"name": "麟洛", "id": "2110"},
        {"name": "西勢", "id": "2120"},
        {"name": "竹田", "id": "2130"},
        {"name": "潮州", "id": "2140"},
        {"name": "崁頂", "id": "2150"},
        {"name": "南州", "id": "2160"},
        {"name": "鎮安", "id": "2170"},
        {"name": "林邊", "id": "2180"},
        {"name": "佳冬", "id": "2190"},
        {"name": "東海", "id": "2200"},
        {"name": "枋寮", "id": "2210"},
        {"name": "加祿", "id": "2220"},
        {"name": "內獅", "id": "2230"},
        {"name": "枋山", "id": "2240"}
    ],
    "臺東縣": [
        {"name": "古莊", "id": "2250"},
        {"name": "大武", "id": "2260"},
        {"name": "瀧溪", "id": "2270"},
        {"name": "金崙", "id": "2280"},
        {"name": "太麻里", "id": "2290"},
        {"name": "知本", "id": "2300"},
        {"name": "康樂", "id": "2310"},
        {"name": "臺東", "id": "2320"},
        {"name": "山里", "id": "2330"},
        {"name": "鹿野", "id": "2340"},
        {"name": "瑞源", "id": "2350"},
        {"name": "瑞和", "id": "2360"},
        {"name": "關山", "id": "2370"},
        {"name": "海端", "id": "2380"},
        {"name": "池上", "id": "2390"},
        {"name": "富里", "id": "2400"}
    ],
    "花蓮縣": [
        {"name": "東竹", "id": "2410"},
        {"name": "東里", "id": "2420"},
        {"name": "玉里", "id": "2430"},
        {"name": "三民", "id": "2440"},
        {"name": "瑞穗", "id": "2450"},
        {"name": "富源", "id": "2460"},
        {"name": "大富", "id": "2470"},
        {"name": "光復", "id": "2480"},
        {"name": "萬榮", "id": "2490"},
        {"name": "鳳林", "id": "2500"},
        {"name": "南平", "id": "2510"},
        {"name": "林榮新光", "id": "2520"},
        {"name": "豐田", "id": "2530"},
        {"name": "壽豐", "id": "2540"},
        {"name": "平和", "id": "2550"},
        {"name": "志學", "id": "2560"},
        {"name": "吉安", "id": "2570"},
        {"name": "花蓮", "id": "2580"},
        {"name": "北埔", "id": "2590"},
        {"name": "景美", "id": "2600"},
        {"name": "新城", "id": "2610"},
        {"name": "崇德", "id": "2620"},
        {"name": "和仁", "id": "2630"},
        {"name": "和平", "id": "2640"}
    ],
    "宜蘭縣": [
        {"name": "漢本", "id": "2650"},
        {"name": "武塔", "id": "2660"},
        {"name": "南澳", "id": "2670"},
        {"name": "東澳", "id": "2680"},
        {"name": "永樂", "id": "2690"},
        {"name": "蘇澳", "id": "2700"},
        {"name": "蘇澳新", "id": "2710"},
        {"name": "新馬", "id": "2720"},
        {"name": "冬山", "id": "2730"},
        {"name": "羅東", "id": "2740"},
        {"name": "中里", "id": "2750"},
        {"name": "二結", "id": "2760"},
        {"name": "宜蘭", "id": "2770"},
        {"name": "四城", "id": "2780"},
        {"name": "礁溪", "id": "2790"},
        {"name": "頂埔", "id": "2800"},
        {"name": "頭城", "id": "2810"},
        {"name": "外澳", "id": "2820"},
        {"name": "龜山", "id": "2830"},
        {"name": "大溪", "id": "2840"},
        {"name": "大里", "id": "2850"},
        {"name": "石城", "id": "2860"}
    ]
}

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
        
        # 從環境變數讀取 TDX API 憑證
        self.tdx_client_id = os.getenv('TDX_CLIENT_ID')
        self.tdx_client_secret = os.getenv('TDX_CLIENT_SECRET')
        if not self.tdx_client_id or not self.tdx_client_secret:
            logger.error("❌ 錯誤: 找不到 TDX API 憑證")
            logger.info("請在 .env 檔案中設定 TDX_CLIENT_ID 和 TDX_CLIENT_SECRET")
        
        # TDX 存取權杖快取
        self.tdx_access_token = None
        self.tdx_token_expires_at = 0
        
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
            
    @app_commands.command(name="地震資訊", description="查詢最新地震資訊")
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

    @app_commands.command(name="設定地震頻道", description="設定地震通知頻道 (需管理員權限)")
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

    @app_commands.command(name="海嘯資訊", description="查詢最新海嘯資訊")
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

    async def get_tdx_access_token(self) -> Optional[str]:
        """取得 TDX API 存取權杖"""
        try:
            import time
            import base64
            
            # 檢查是否有有效的權杖
            current_time = time.time()
            if (self.tdx_access_token and 
                current_time < self.tdx_token_expires_at - 60):  # 提前60秒更新
                return self.tdx_access_token
            
            # 準備認證資料
            auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
            
            # 建立 Basic Authentication
            credentials = f"{self.tdx_client_id}:{self.tdx_client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Basic {encoded_credentials}'
            }
            
            data = 'grant_type=client_credentials'
            
            logger.info("正在取得 TDX 存取權杖...")
            
            # 使用 aiohttp 發送請求
            async with self.session.post(auth_url, headers=headers, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    
                    self.tdx_access_token = token_data.get('access_token')
                    expires_in = token_data.get('expires_in', 3600)  # 預設1小時
                    self.tdx_token_expires_at = current_time + expires_in
                    
                    logger.info("✅ 成功取得 TDX 存取權杖")
                    return self.tdx_access_token
                else:
                    error_text = await response.text()
                    logger.error(f"❌ 取得 TDX 存取權杖失敗: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"取得 TDX 存取權杖時發生錯誤: {str(e)}")
            return None

    async def fetch_rail_alerts(self, rail_type: str = "tra") -> Optional[List[Dict[str, Any]]]:
        """從TDX平台取得鐵路事故資料"""
        try:
            # 取得 TDX 存取權杖
            access_token = await self.get_tdx_access_token()
            if not access_token:
                logger.error("❌ 無法取得 TDX 存取權杖")
                return None
            
            if rail_type == "tra":
                # 台鐵事故資料
                url = "https://tdx.transportdata.tw/api/basic/v3/Rail/TRA/Alert?$top=30&$format=JSON"
                logger.info("開始獲取台鐵事故資料")
            else:
                # 高鐵事故資料
                url = "https://tdx.transportdata.tw/api/basic/v2/Rail/THSR/AlertInfo?$top=30&$format=JSON"
                logger.info("開始獲取高鐵事故資料")
            
            # 設定認證標頭
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'User-Agent': 'Discord-Bot-TDX-Client/1.0'
            }
            
            # 使用非同步請求獲取資料
            logger.info(f"正在發送認證請求到 {url}")
            async with self.session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        
                        # 處理不同的回應格式
                        if isinstance(data, list):
                            logger.info(f"✅ 成功獲取{rail_type.upper()}事故資料，共 {len(data)} 筆 (列表格式)")
                            return data
                        elif isinstance(data, dict):
                            # 如果是字典格式，檢查是否有事故列表
                            if 'alerts' in data or 'data' in data:
                                alerts = data.get('alerts', data.get('data', []))
                                if isinstance(alerts, list):
                                    logger.info(f"✅ 成功獲取{rail_type.upper()}事故資料，共 {len(alerts)} 筆 (字典格式)")
                                    return alerts
                            
                            # 如果是單一事故物件，包裝為列表
                            if 'Title' in data or 'Description' in data:
                                logger.info(f"✅ 成功獲取{rail_type.upper()}事故資料，1 筆 (單一物件)")
                                return [data]
                            
                            # 如果字典中沒有明確的事故資料，返回空列表
                            logger.info(f"✅ {rail_type.upper()}目前沒有事故通報")
                            return []
                        else:
                            logger.warning(f"❌ {rail_type.upper()}事故資料格式不正確: {type(data)}")
                            return None
                    except Exception as e:
                        logger.error(f"解析{rail_type.upper()}事故資料JSON時發生錯誤: {str(e)}")
                        return None
                else:
                    error_text = await response.text()
                    logger.error(f"❌ TDX API請求失敗: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"獲取{rail_type.upper()}事故資料時發生錯誤: {str(e)}")
            return None

    async def fetch_metro_alerts(self, metro_system: str = "TRTC") -> Optional[List[Dict[str, Any]]]:
        """從TDX平台取得捷運系統事故資料"""
        try:
            # 取得 TDX 存取權杖
            access_token = await self.get_tdx_access_token()
            if not access_token:
                logger.error("❌ 無法取得 TDX 存取權杖")
                return None
            
            # 捷運系統 API 端點對應
            metro_apis = {
                "TRTC": "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/Alert/TRTC?$top=30&$format=JSON",  # 台北捷運
                "KRTC": "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/Alert/KRTC?$top=30&$format=JSON",  # 高雄捷運
                "TYMC": "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/Alert/TYMC?$top=30&$format=JSON",  # 桃園捷運
                "KLRT": "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/Alert/KLRT?$top=30&$format=JSON",  # 高雄輕軌
                "TMRT": "https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/Alert/TMRT?$top=30&$format=JSON"   # 台中捷運
            }
            
            url = metro_apis.get(metro_system)
            if not url:
                logger.error(f"❌ 不支援的捷運系統: {metro_system}")
                return None
            
            logger.info(f"開始獲取{metro_system}捷運事故資料")
            
            # 設定認證標頭
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'User-Agent': 'Discord-Bot-TDX-Client/1.0'
            }
            
            # 使用非同步請求獲取資料
            logger.info(f"正在發送認證請求到 {url}")
            async with self.session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        
                        # 處理不同的回應格式
                        if isinstance(data, list):
                            logger.info(f"✅ 成功獲取{metro_system}事故資料，共 {len(data)} 筆 (列表格式)")
                            return data
                        elif isinstance(data, dict):
                            # 如果是字典格式，檢查是否有事故列表
                            if 'alerts' in data or 'data' in data:
                                alerts = data.get('alerts', data.get('data', []))
                                if isinstance(alerts, list):
                                    logger.info(f"✅ 成功獲取{metro_system}事故資料，共 {len(alerts)} 筆 (字典格式)")
                                    return alerts
                            
                            # 如果是單一事故物件，包裝為列表
                            if 'Title' in data or 'Description' in data:
                                logger.info(f"✅ 成功獲取{metro_system}事故資料，1 筆 (單一物件)")
                                return [data]
                            
                            # 如果字典中沒有明確的事故資料，返回空列表
                            logger.info(f"✅ {metro_system}目前沒有事故通報")
                            return []
                        else:
                            logger.warning(f"❌ {metro_system}事故資料格式不正確: {type(data)}")
                            return None
                    except Exception as e:
                        logger.error(f"解析{metro_system}事故資料JSON時發生錯誤: {str(e)}")
                        return None
                else:
                    error_text = await response.text()
                    logger.error(f"❌ TDX API請求失敗: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"獲取{metro_system}事故資料時發生錯誤: {str(e)}")
            return None

    def format_metro_alert(self, alert_data: Dict[str, Any], metro_system: str = "TRTC") -> Optional[discord.Embed]:
        """將捷運事故資料格式化為Discord嵌入訊息"""
        try:
            # 捷運系統名稱對應
            metro_names = {
                "TRTC": "台北捷運",
                "KRTC": "高雄捷運", 
                "TYMC": "桃園捷運",
                "KLRT": "高雄輕軌",
                "TMRT": "台中捷運"
            }
            
            # 捷運系統顏色對應
            metro_colors = {
                "TRTC": discord.Color.blue(),      # 台北捷運 - 藍色
                "KRTC": discord.Color.red(),       # 高雄捷運 - 紅色
                "TYMC": discord.Color.purple(),    # 桃園捷運 - 紫色
                "KLRT": discord.Color.orange(),    # 高雄輕軌 - 橘色
                "TMRT": discord.Color.green()      # 台中捷運 - 綠色
            }
            
            metro_name = metro_names.get(metro_system, f"{metro_system}捷運")
            metro_color = metro_colors.get(metro_system, discord.Color.blue())
            
            # 取得事故資訊
            title = alert_data.get('Title', alert_data.get('AlertTitle', '未知事故'))
            description = alert_data.get('Description', alert_data.get('AlertDescription', '暫無詳細資訊'))
            start_time = alert_data.get('StartTime', alert_data.get('AlertStartTime', '未知時間'))
            end_time = alert_data.get('EndTime', alert_data.get('AlertEndTime', '尚未結束'))
            url_link = alert_data.get('URL', alert_data.get('AlertURL', ''))
            
            # 檢查是否為正常營運狀態
            if '正常' in title or 'Normal' in title or '營運正常' in title:
                embed = discord.Embed(
                    title=f"✅ {metro_name}營運狀況",
                    description=f"目前{metro_name}營運正常，沒有事故通報。",
                    color=discord.Color.green()
                )
                embed.set_footer(
                    text=f"資料來源: TDX運輸資料流通服務平臺 | 查詢時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                return embed
            
            # 建立事故通報嵌入
            embed = discord.Embed(
                title=f"⚠️ {metro_name}事故通報",
                description=f"**{title}**",
                color=metro_color,
                url=url_link if url_link else None
            )
            
            # 添加詳細資訊
            if description and description != title and description != '暫無詳細資訊':
                embed.add_field(
                    name="📋 詳細說明",
                    value=description[:1000] + ("..." if len(description) > 1000 else ""),
                    inline=False
                )
            
            # 添加時間資訊
            if start_time and start_time != '未知時間':
                try:
                    # 解析時間格式
                    if 'T' in start_time:
                        formatted_start = start_time.replace('T', ' ').split('+')[0].split('.')[0]
                    else:
                        formatted_start = start_time
                    embed.add_field(
                        name="⏰ 開始時間",
                        value=formatted_start,
                        inline=True
                    )
                except:
                    embed.add_field(
                        name="⏰ 開始時間",
                        value=start_time,
                        inline=True
                    )
            
            if end_time and end_time != '尚未結束' and end_time != '':
                try:
                    if 'T' in end_time:
                        formatted_end = end_time.replace('T', ' ').split('+')[0].split('.')[0]
                    else:
                        formatted_end = end_time
                    embed.add_field(
                        name="⏰ 結束時間",
                        value=formatted_end,
                        inline=True
                    )
                except:
                    embed.add_field(
                        name="⏰ 結束時間",
                        value=end_time,
                        inline=True
                    )
            
            # 解析影響路線
            affected_lines = []
            if 'Lines' in alert_data and alert_data['Lines']:
                for line in alert_data['Lines']:
                    line_name = line.get('LineName', line.get('Name', ''))
                    if line_name:
                        affected_lines.append(line_name)
            
            # 解析影響車站
            affected_stations = []
            if 'Stations' in alert_data and alert_data['Stations']:
                for station in alert_data['Stations']:
                    station_name = station.get('StationName', station.get('Name', ''))
                    if station_name:
                        affected_stations.append(station_name)
            
            # 添加影響路線
            if affected_lines:
                embed.add_field(
                    name="🚇 影響路線",
                    value=", ".join(affected_lines[:5]) + ("..." if len(affected_lines) > 5 else ""),
                    inline=False
                )
            
            # 添加影響車站
            if affected_stations:
                embed.add_field(
                    name="🚉 影響車站",
                    value=", ".join(affected_stations[:10]) + ("..." if len(affected_stations) > 10 else ""),
                    inline=False
                )
            
            # 添加頁尾
            embed.set_footer(
                text=f"資料來源: TDX運輸資料流通服務平臺 | 更新時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            return embed
            
        except Exception as e:
            logger.error(f"格式化{metro_system}事故資料時發生錯誤: {str(e)}")
            return None

    def format_rail_alert(self, alert_data: Dict[str, Any], rail_type: str = "tra") -> Optional[discord.Embed]:
        """將鐵路事故資料格式化為Discord嵌入訊息"""
        try:
            if rail_type == "tra":
                # 台鐵事故格式
                title = alert_data.get('Title', alert_data.get('AlertTitle', '未知事故'))
                description = alert_data.get('Description', alert_data.get('AlertDescription', '暫無詳細資訊'))
                start_time = alert_data.get('StartTime', alert_data.get('AlertStartTime', '未知時間'))
                end_time = alert_data.get('EndTime', alert_data.get('AlertEndTime', '尚未結束'))
                url_link = alert_data.get('URL', alert_data.get('AlertURL', ''))
                
                # 檢查是否為正常營運狀態
                if '正常' in title or 'Normal' in title:
                    embed = discord.Embed(
                        title="✅ 台鐵營運狀況",
                        description="目前台鐵營運正常，沒有事故通報。",
                        color=discord.Color.green()
                    )
                    embed.set_footer(
                        text=f"資料來源: TDX運輸資料流通服務平臺 | 查詢時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    return embed
                
                # 解析影響路線
                affected_lines = []
                if 'Lines' in alert_data and alert_data['Lines']:
                    for line in alert_data['Lines']:
                        line_name = line.get('LineName', line.get('Name', ''))
                        if line_name:
                            affected_lines.append(line_name)
                
                # 解析影響車站
                affected_stations = []
                if 'Stations' in alert_data and alert_data['Stations']:
                    for station in alert_data['Stations']:
                        station_name = station.get('StationName', station.get('Name', ''))
                        if station_name:
                            affected_stations.append(station_name)
                
                embed = discord.Embed(
                    title="🚆 台鐵事故通報",
                    description=f"**{title}**",
                    color=discord.Color.orange(),
                    url=url_link if url_link else None
                )
                
            else:
                # 高鐵事故格式
                title = alert_data.get('Title', alert_data.get('AlertTitle', '未知事故'))
                description = alert_data.get('Description', alert_data.get('AlertDescription', '暫無詳細資訊'))
                start_time = alert_data.get('StartTime', alert_data.get('AlertStartTime', '未知時間'))
                end_time = alert_data.get('EndTime', alert_data.get('AlertEndTime', '尚未結束'))
                url_link = alert_data.get('URL', alert_data.get('AlertURL', ''))
                
                # 檢查是否為正常營運狀態
                if '正常' in title or 'Normal' in title:
                    embed = discord.Embed(
                        title="✅ 高鐵營運狀況",
                        description="目前高鐵營運正常，沒有事故通報。",
                        color=discord.Color.green()
                    )
                    embed.set_footer(
                        text=f"資料來源: TDX運輸資料流通服務平臺 | 查詢時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    return embed
                
                embed = discord.Embed(
                    title="🚄 高鐵事故通報",
                    description=f"**{title}**",
                    color=discord.Color.red(),
                    url=url_link if url_link else None
                )
                
                affected_lines = []
                affected_stations = []
            
            # 添加詳細資訊
            if description and description != title and description != '暫無詳細資訊':
                embed.add_field(
                    name="📋 詳細說明",
                    value=description[:1000] + ("..." if len(description) > 1000 else ""),
                    inline=False
                )
            
            # 添加時間資訊
            if start_time and start_time != '未知時間':
                try:
                    # 解析時間格式
                    if 'T' in start_time:
                        formatted_start = start_time.replace('T', ' ').split('+')[0].split('.')[0]
                    else:
                        formatted_start = start_time
                    embed.add_field(
                        name="⏰ 開始時間",
                        value=formatted_start,
                        inline=True
                    )
                except:
                    embed.add_field(
                        name="⏰ 開始時間",
                        value=start_time,
                        inline=True
                    )
            
            if end_time and end_time != '尚未結束' and end_time != '':
                try:
                    if 'T' in end_time:
                        formatted_end = end_time.replace('T', ' ').split('+')[0].split('.')[0]
                    else:
                        formatted_end = end_time
                    embed.add_field(
                        name="⏰ 結束時間",
                        value=formatted_end,
                        inline=True
                    )
                except:
                    embed.add_field(
                        name="⏰ 結束時間",
                        value=end_time,
                        inline=True
                    )
            
            # 添加影響路線
            if affected_lines:
                embed.add_field(
                    name="🛤️ 影響路線",
                    value=", ".join(affected_lines[:5]) + ("..." if len(affected_lines) > 5 else ""),
                    inline=False
                )
            
            # 添加影響車站
            if affected_stations:
                embed.add_field(
                    name="🚉 影響車站",
                    value=", ".join(affected_stations[:10]) + ("..." if len(affected_stations) > 10 else ""),
                    inline=False
                )
            
            # 添加頁尾
            embed.set_footer(
                text=f"資料來源: TDX運輸資料流通服務平臺 | 更新時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            return embed
            
        except Exception as e:
            logger.error(f"格式化{rail_type.upper()}事故資料時發生錯誤: {str(e)}")
            return None

    @app_commands.command(name="鐵路事故", description="查詢台鐵或高鐵事故資訊")
    @app_commands.describe(鐵路類型="選擇要查詢的鐵路類型")
    @app_commands.choices(鐵路類型=[
        app_commands.Choice(name="台鐵", value="tra"),
        app_commands.Choice(name="高鐵", value="thsr")
    ])
    async def rail_alert(self, interaction: discord.Interaction, 鐵路類型: str = "tra"):
        """查詢台鐵或高鐵事故資訊"""
        await interaction.response.defer()
        
        try:
            # 獲取鐵路事故資料
            alerts = await self.fetch_rail_alerts(鐵路類型)
            
            if alerts is None:
                rail_name = "台鐵" if 鐵路類型 == "tra" else "高鐵"
                await interaction.followup.send(f"❌ 無法獲取{rail_name}事故資料，請稍後再試。")
                return
            
            if len(alerts) == 0:
                rail_name = "台鐵" if 鐵路類型 == "tra" else "高鐵"
                embed = discord.Embed(
                    title=f"✅ {rail_name}營運狀況",
                    description=f"目前{rail_name}沒有事故通報，營運正常。",
                    color=discord.Color.green()
                )
                embed.set_footer(
                    text=f"資料來源: TDX運輸資料流通服務平臺 | 查詢時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 檢查是否只有正常營運的通知
            normal_operation = True
            actual_alerts = []
            
            for alert in alerts:
                title = alert.get('Title', alert.get('AlertTitle', ''))
                if not ('正常' in title or 'Normal' in title):
                    normal_operation = False
                    actual_alerts.append(alert)
            
            # 如果只有正常營運通知，顯示正常狀態
            if normal_operation and len(actual_alerts) == 0:
                rail_name = "台鐵" if 鐵路類型 == "tra" else "高鐵"
                embed = discord.Embed(
                    title=f"✅ {rail_name}營運狀況",
                    description=f"目前{rail_name}營運正常，沒有事故通報。",
                    color=discord.Color.green()
                )
                embed.set_footer(
                    text=f"資料來源: TDX運輸資料流通服務平臺 | 查詢時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # 如果有實際的事故，處理事故資料
            alerts_to_show = actual_alerts if actual_alerts else alerts
            
            # 如果只有一筆事故，直接顯示
            if len(alerts_to_show) == 1:
                embed = self.format_rail_alert(alerts_to_show[0], 鐵路類型)
                if embed:
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("❌ 無法解析事故資料，請稍後再試。")
                return
            
            # 如果有多筆事故，顯示列表
            rail_name = "台鐵" if 鐵路類型 == "tra" else "高鐵"
            embed = discord.Embed(
                title=f"⚠️ {rail_name}事故通報列表",
                description=f"共發現 {len(alerts_to_show)} 筆事故通報",
                color=discord.Color.orange() if 鐵路類型 == "tra" else discord.Color.red()
            )
            
            # 顯示前5筆事故的簡要資訊
            for i, alert in enumerate(alerts_to_show[:5], 1):
                title = alert.get('Title', alert.get('AlertTitle', f'事故 #{i}'))
                start_time = alert.get('StartTime', alert.get('AlertStartTime', '未知時間'))
                
                # 格式化時間
                try:
                    if 'T' in start_time:
                        formatted_time = start_time.replace('T', ' ').split('+')[0].split('.')[0]
                    else:
                        formatted_time = start_time
                except:
                    formatted_time = start_time
                
                embed.add_field(
                    name=f"{i}. {title[:50]}{'...' if len(title) > 50 else ''}",
                    value=f"⏰ {formatted_time}",
                    inline=False
                )
            
            if len(alerts_to_show) > 5:
                embed.add_field(
                    name="",
                    value=f"*還有 {len(alerts_to_show) - 5} 筆事故通報未顯示*",
                    inline=False
                )
            
            embed.set_footer(
                text=f"資料來源: TDX運輸資料流通服務平臺 | 查詢時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"鐵路事故指令執行時發生錯誤: {str(e)}")
            await interaction.followup.send("❌ 執行指令時發生錯誤，請稍後再試。")

    @app_commands.command(name='捷運狀態', description='查詢各捷運系統運行狀態')
    @app_commands.describe(metro_system='選擇捷運系統')
    @app_commands.choices(metro_system=[
        app_commands.Choice(name='台北捷運', value='TRTC'),
        app_commands.Choice(name='高雄捷運', value='KRTC'),
        app_commands.Choice(name='桃園捷運', value='TYMC'),
        app_commands.Choice(name='高雄輕軌', value='KLRT'),
        app_commands.Choice(name='台中捷運', value='TMRT')
    ])
    async def metro_status(self, interaction: discord.Interaction, metro_system: app_commands.Choice[str]):
        """查詢捷運系統運行狀態"""
        await interaction.response.defer()
        
        try:
            logger.info(f"使用者 {interaction.user} 查詢捷運狀態: {metro_system.name}")
            
            # 獲取捷運狀態資料
            metro_data = await self.fetch_metro_alerts(metro_system.value)
            
            if not metro_data:
                embed = discord.Embed(
                    title="🚇 捷運狀態查詢",
                    description="❌ 目前無法取得捷運狀態資料，請稍後再試。",
                    color=0xFF0000
                )
                embed.add_field(name="系統", value=metro_system.name, inline=True)
                embed.add_field(name="狀態", value="資料取得失敗", inline=True)
                embed.set_footer(text="資料來源: 交通部TDX平台")
                await interaction.followup.send(embed=embed)
                return
            
            # 格式化資料
            embed = await self.format_metro_alert(metro_data, metro_system.value, metro_system.name)
            
            if embed is None:
                embed = discord.Embed(
                    title="🚇 捷運狀態查詢",
                    description="❌ 資料處理時發生錯誤。",
                    color=0xFF0000
                )
                embed.add_field(name="系統", value=metro_system.name, inline=True)
                embed.set_footer(text="資料來源: 交通部TDX平台")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"捷運狀態指令執行時發生錯誤: {str(e)}")
            await interaction.followup.send("❌ 執行指令時發生錯誤，請稍後再試。")

    async def fetch_metro_liveboard(self, metro_system: str = "TRTC") -> Optional[List[Dict[str, Any]]]:
        """從TDX平台取得捷運車站即時到離站電子看板資料"""
        try:
            logger.info(f"正在從TDX平台取得{metro_system}車站即時電子看板資料...")
            
            # 取得access token
            access_token = await self.get_tdx_access_token()
            if not access_token:
                logger.error("無法取得TDX access token")
                return None
            
            # 設定API端點 - 更新為用戶指定的數量
            api_endpoints = {
                'TRTC': 'https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/TRTC?%24top=117&%24format=JSON',
                'KRTC': 'https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/KRTC?%24top=77&%24format=JSON', 
                'KLRT': 'https://tdx.transportdata.tw/api/basic/v2/Rail/Metro/LiveBoard/KLRT?%24top=38&%24format=JSON'
            }
            
            url = api_endpoints.get(metro_system)
            if not url:
                logger.error(f"不支援的捷運系統: {metro_system}")
                return None
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'User-Agent': 'Discord-Bot-TDX-Client/1.0'
            }
            
            # 建立SSL連接
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"成功取得{metro_system}車站電子看板資料，共{len(data)}筆")
                        
                        # 調試：記錄第一筆資料的結構
                        if data and len(data) > 0:
                            first_station = data[0]
                            logger.debug(f"第一筆車站資料結構: {list(first_station.keys())}")
                            
                            # 檢查LiveBoards結構
                            live_boards = first_station.get('LiveBoards', [])
                            if live_boards and len(live_boards) > 0:
                                first_board = live_boards[0]
                                logger.debug(f"第一筆LiveBoard資料結構: {list(first_board.keys())}")
                                logger.debug(f"LiveBoard內容範例: {first_board}")
                            else:
                                logger.debug("該車站沒有LiveBoard資料")
                        
                        return data
                    else:
                        logger.error(f"TDX API請求失敗: HTTP {response.status}")
                        response_text = await response.text()
                        logger.error(f"錯誤回應: {response_text}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error("TDX API請求超時")
        except Exception as e:
            logger.error(f"取得捷運車站電子看板資料時發生錯誤: {str(e)}")
            import traceback
            logger.error(f"錯誤詳情: {traceback.format_exc()}")
        
        return None

    def format_metro_liveboard(self, liveboard_data: List[Dict[str, Any]], metro_system: str, system_name: str) -> Optional[discord.Embed]:
        """將捷運車站即時電子看板資料格式化為Discord嵌入訊息"""
        try:
            if not liveboard_data:
                embed = discord.Embed(
                    title="🚇 車站即時電子看板",
                    description="目前沒有即時電子看板資料",
                    color=0x95A5A6
                )
                embed.add_field(name="系統", value=system_name, inline=True)
                embed.set_footer(text="資料來源: 交通部TDX平台")
                return embed
            
            # 捷運系統顏色設定
            colors = {
                'TRTC': 0x0070BD,  # 台北捷運藍
                'KRTC': 0xFF6B35,  # 高雄捷運橘紅  
                'KLRT': 0x00A651   # 高雄輕軌綠
            }
            
            color = colors.get(metro_system, 0x3498DB)
            
            embed = discord.Embed(
                title="🚇 車站即時電子看板",
                description=f"📍 **{system_name}** 車站即時到離站資訊",
                color=color
            )
            
            # 處理資料（限制顯示前10筆以避免訊息過長）
            display_count = min(10, len(liveboard_data))
            
            for i, station_data in enumerate(liveboard_data[:display_count]):
                try:
                    # 取得車站資訊
                    station_name = station_data.get('StationName', {})
                    if isinstance(station_name, dict):
                        station_name_zh = station_name.get('Zh_tw', '未知車站')
                    else:
                        station_name_zh = str(station_name)
                    
                    # 取得路線資訊
                    line_info = station_data.get('LineID', '未知路線')
                    
                    # 取得列車資訊
                    trains_info = []
                    live_boards = station_data.get('LiveBoards', [])
                    
                    if live_boards:
                        for board in live_boards[:3]:  # 最多顯示3班列車
                            direction = board.get('Direction', '未知')
                            destination = board.get('DestinationStationName', {})
                            if isinstance(destination, dict):
                                dest_name = destination.get('Zh_tw', '未知目的地')
                            else:
                                dest_name = str(destination)
                            
                            # 取得到站時間
                            enter_time = board.get('EnterTime', '')
                            if enter_time:
                                trains_info.append(f"➤ 往{dest_name} ({enter_time})")
                            else:
                                trains_info.append(f"➤ 往{dest_name}")
                    
                    # 組合顯示資訊
                    if trains_info:
                        train_text = '\n'.join(trains_info)
                    else:
                        train_text = "暫無列車資訊"
                    
                    # 添加到embed (限制字數以避免過長)
                    field_name = f"🚉 {station_name_zh}"
                    if line_info != '未知路線':
                        field_name += f" ({line_info})"
                    
                    embed.add_field(
                        name=field_name,
                        value=train_text[:100] + ("..." if len(train_text) > 100 else ""),
                        inline=False
                    )
                    
                except Exception as field_error:
                    logger.warning(f"處理車站資料時發生錯誤: {str(field_error)}")
                    continue
            
            # 如果有更多資料，顯示提示
            if len(liveboard_data) > display_count:
                embed.add_field(
                    name="📊 資料統計",
                    value=f"顯示前 {display_count} 個車站，共 {len(liveboard_data)} 筆資料",
                    inline=False
                )
            
            # 設定頁腳
            embed.set_footer(text="資料來源: 交通部TDX平台 | 即時更新")
            
            return embed
            
        except Exception as e:
            logger.error(f"格式化捷運電子看板資料時發生錯誤: {str(e)}")
            return None

    @app_commands.command(name='即時電子看板', description='查詢捷運車站即時到離站電子看板')
    @app_commands.describe(metro_system='選擇捷運系統')
    @app_commands.choices(metro_system=[
        app_commands.Choice(name='台北捷運', value='TRTC'),
        app_commands.Choice(name='高雄捷運', value='KRTC'),
        app_commands.Choice(name='高雄輕軌', value='KLRT')
    ])
    async def metro_liveboard(self, interaction: discord.Interaction, metro_system: app_commands.Choice[str]):
        """查詢捷運車站即時電子看板"""
        await interaction.response.defer()
        
        try:
            logger.info(f"使用者 {interaction.user} 查詢捷運電子看板: {metro_system.name}")
            
            # 獲取即時電子看板資料
            liveboard_data = await self.fetch_metro_liveboard(metro_system.value)
            
            if not liveboard_data:
                embed = discord.Embed(
                    title="🚇 車站即時電子看板",
                    description="❌ 目前無法取得即時電子看板資料，請稍後再試。",
                    color=0xFF0000
                )
                embed.add_field(name="系統", value=metro_system.name, inline=True)
                embed.add_field(name="狀態", value="資料取得失敗", inline=True)
                embed.set_footer(text="資料來源: 交通部TDX平台")
                await interaction.followup.send(embed=embed)
                return
            
            # 使用翻頁視圖
            view = MetroLiveboardView(
                cog=self,
                user_id=interaction.user.id,
                liveboard_data=liveboard_data,
                metro_system=metro_system.value,
                system_name=metro_system.name
            )
            
            # 創建第一頁的嵌入訊息
            embed = view.create_page_embed()
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"即時電子看板指令執行時發生錯誤: {str(e)}")
            await interaction.followup.send("❌ 執行指令時發生錯誤，請稍後再試。")

    @app_commands.command(name='台鐵電子看板', description='查詢台鐵車站即時電子看板')
    @app_commands.describe(
        county='選擇縣市',
        station_name='選擇車站'
    )
    @app_commands.choices(county=[
        app_commands.Choice(name=county, value=county) for county in TW_LOCATIONS
    ])
    async def tra_liveboard(self, interaction: discord.Interaction, county: app_commands.Choice[str], station_name: str = None):
        """查詢台鐵車站即時電子看板"""
        await interaction.response.defer()
        
        try:
            logger.info(f"使用者 {interaction.user} 查詢台鐵電子看板: {county.value}")
            
            # 檢查縣市是否有台鐵車站
            if county.value not in TRA_STATIONS:
                embed = discord.Embed(
                    title="🚆 台鐵電子看板",
                    description=f"❌ {county.value} 目前沒有台鐵車站資料。",
                    color=0xFF0000
                )
                await interaction.followup.send(embed=embed)
                return
            
            stations = TRA_STATIONS[county.value]
            
            # 如果指定了車站名稱，查找該車站
            if station_name:
                target_station = None
                for station in stations:
                    if station['name'] == station_name or station_name in station['name']:
                        target_station = station
                        break
                
                if not target_station:
                    # 顯示該縣市可用的車站列表
                    station_list = "\n".join([f"• {station['name']}" for station in stations])
                    embed = discord.Embed(
                        title="🚆 車站未找到",
                        description=f"在 {county.value} 找不到車站 '{station_name}'",
                        color=0xFF9900
                    )
                    embed.add_field(
                        name=f"{county.value} 可用車站",
                        value=station_list,
                        inline=False
                    )
                    await interaction.followup.send(embed=embed)
                    return
                
                # 使用台鐵電子看板視圖
                view = TRALiveboardView(interaction, county.value, target_station['name'], target_station['id'])
                await view.send_with_view()
                
            else:
                # 顯示該縣市所有可用車站
                station_list = "\n".join([f"• {station['name']}" for station in stations])
                embed = discord.Embed(
                    title=f"🚆 {county.value} 台鐵車站",
                    description="請使用指令參數指定車站名稱",
                    color=0x0099FF
                )
                embed.add_field(
                    name="可用車站",
                    value=station_list,
                    inline=False
                )
                embed.set_footer(text="使用方式：/台鐵電子看板 county:縣市 station_name:車站名稱")
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            logger.error(f"台鐵電子看板指令執行時發生錯誤: {str(e)}")
            await interaction.followup.send("❌ 執行指令時發生錯誤，請稍後再試。")

    @app_commands.command(name='台鐵誤點查詢', description='查詢台鐵列車誤點資訊')
    @app_commands.describe(county='選擇縣市 (可選，不選擇則查詢全台)')
    @app_commands.choices(county=[
        app_commands.Choice(name=county, value=county) for county in TW_LOCATIONS
    ])
    async def tra_delay(self, interaction: discord.Interaction, county: app_commands.Choice[str] = None):
        """查詢台鐵列車誤點資訊"""
        await interaction.response.defer()
        
        try:
            county_name = county.value if county else None
            logger.info(f"使用者 {interaction.user} 查詢台鐵誤點資訊: {county_name or '全台'}")
            
            # 使用台鐵誤點視圖
            view = TRADelayView(interaction, county_name)
            await view.send_with_view()
                
        except Exception as e:
            logger.error(f"台鐵誤點查詢指令執行時發生錯誤: {str(e)}")
            await interaction.followup.send("❌ 執行指令時發生錯誤，請稍後再試。")



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

# 捷運即時電子看板翻頁視圖類
class MetroLiveboardView(View):
    """捷運即時電子看板翻頁視圖"""
    def __init__(self, cog, user_id: int, liveboard_data: List[Dict[str, Any]], metro_system: str, system_name: str):
        super().__init__(timeout=300)  # 5分鐘超時
        self.cog = cog
        self.user_id = user_id
        self.liveboard_data = liveboard_data
        self.metro_system = metro_system
        self.system_name = system_name
        self.current_page = 0
        self.stations_per_page = 10  # 每頁顯示10個車站
        self.total_pages = max(1, (len(liveboard_data) + self.stations_per_page - 1) // self.stations_per_page)
        
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
        
        # 刷新按鈕
        refresh_button = discord.ui.Button(
            label="🔄 刷新",
            style=discord.ButtonStyle.success
        )
        refresh_button.callback = self.refresh_data
        self.add_item(refresh_button)
    
    async def previous_page(self, interaction: discord.Interaction):
        """上一頁"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 只有原始命令使用者可以操作此按鈕", ephemeral=True)
            return
        
        if self.current_page > 0:
            self.current_page -= 1
            self._update_buttons()
            embed = self.create_page_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    async def next_page(self, interaction: discord.Interaction):
        """下一頁"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 只有原始命令使用者可以操作此按鈕", ephemeral=True)
            return
        
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._update_buttons()
            embed = self.create_page_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    async def refresh_data(self, interaction: discord.Interaction):
        """刷新資料"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 只有原始命令使用者可以操作此按鈕", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            # 重新獲取資料
            new_data = await self.cog.fetch_metro_liveboard(self.metro_system)
            if new_data:
                self.liveboard_data = new_data
                self.total_pages = max(1, (len(new_data) + self.stations_per_page - 1) // self.stations_per_page)
                
                # 如果當前頁超出範圍，調整到最後一頁
                if self.current_page >= self.total_pages:
                    self.current_page = max(0, self.total_pages - 1)
                
                self._update_buttons()
                embed = self.create_page_embed()
                embed.description += "\n🔄 **資料已刷新**"
                await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self)
            else:
                await interaction.followup.send("❌ 刷新資料失敗，請稍後再試", ephemeral=True)
        except Exception as e:
            logger.error(f"刷新捷運電子看板資料時發生錯誤: {str(e)}")
            await interaction.followup.send("❌ 刷新資料時發生錯誤", ephemeral=True)
    
    def create_page_embed(self) -> discord.Embed:
        """創建當前頁面的嵌入訊息"""
        # 捷運系統顏色設定
        colors = {
            'TRTC': 0x0070BD,  # 台北捷運藍
            'KRTC': 0xFF6B35,  # 高雄捷運橘紅  
            'KLRT': 0x00A651   # 高雄輕軌綠
        }
        
        color = colors.get(self.metro_system, 0x3498DB)
        
        embed = discord.Embed(
            title="🚇 車站即時電子看板",
            description=f"📍 **{self.system_name}** 車站即時到離站資訊",
            color=color
        )
        
        if not self.liveboard_data:
            embed.description = "目前沒有即時電子看板資料"
            embed.set_footer(text="資料來源: 交通部TDX平台")
            return embed
        
        # 計算當前頁面的資料範圍
        start_idx = self.current_page * self.stations_per_page
        end_idx = min(start_idx + self.stations_per_page, len(self.liveboard_data))
        current_page_data = self.liveboard_data[start_idx:end_idx]
        
        # 處理當前頁面的車站資料
        for station_data in current_page_data:
            try:
                # 取得車站資訊
                station_name = station_data.get('StationName', {})
                if isinstance(station_name, dict):
                    station_name_zh = station_name.get('Zh_tw', '未知車站')
                else:
                    station_name_zh = str(station_name)
                
                # 取得路線資訊
                line_info = station_data.get('LineID', '未知路線')
                
                # 🔧 修正：TDX LiveBoard API的資料結構
                # 每個車站記錄本身就是一個列車資訊，不是包含LiveBoards陣列
                trains_info = []
                
                try:
                    # 取得目的地資訊
                    destination = station_data.get('DestinationStationName', {})
                    if isinstance(destination, dict):
                        dest_name = destination.get('Zh_tw', destination.get('En', ''))
                    else:
                        dest_name = str(destination) if destination else ''
                    
                    # 取得班次標示
                    trip_head_sign = station_data.get('TripHeadSign', '')
                    
                    # 取得預估時間
                    estimate_time = station_data.get('EstimateTime', 0)
                    
                    # 取得服務狀態
                    service_status = station_data.get('ServiceStatus', 0)
                    
                    # 取得更新時間
                    update_time = station_data.get('UpdateTime', '')
                    src_update_time = station_data.get('SrcUpdateTime', '')
                    
                    # 組合列車資訊
                    if dest_name or trip_head_sign:
                        train_info_parts = []
                        
                        # 使用班次標示或目的地
                        if trip_head_sign:
                            train_info_parts.append(trip_head_sign)
                        elif dest_name:
                            train_info_parts.append(f"往{dest_name}")
                        
                        # 處理預估時間
                        if estimate_time > 0:
                            if estimate_time < 60:
                                train_info_parts.append(f"({estimate_time}秒)")
                            elif estimate_time < 120:  # 2分鐘內顯示分秒
                                minutes = estimate_time // 60
                                seconds = estimate_time % 60
                                train_info_parts.append(f"({minutes}分{seconds}秒)")
                            else:  # 超過2分鐘只顯示分鐘
                                minutes = estimate_time // 60
                                seconds = estimate_time % 60
                                if seconds > 0:
                                    train_info_parts.append(f"({minutes}分{seconds}秒)")
                                else:
                                    train_info_parts.append(f"({minutes}分鐘)")
                        elif estimate_time == 0:
                            # 檢查服務狀態
                            if service_status == 0:
                                train_info_parts.append("(即將進站)")
                            elif service_status == 1:
                                train_info_parts.append("(正在進站)")
                            else:
                                train_info_parts.append("(準備中)")
                        
                        # 添加服務狀態說明
                        status_text = ""
                        if service_status == 0:
                            status_text = "🟢"  # 正常
                        elif service_status == 1:
                            status_text = "🟡"  # 進站中
                        elif service_status == 2:
                            status_text = "🟠"  # 離站
                        else:
                            status_text = "⚪"  # 其他狀態
                        
                        if train_info_parts:
                            trains_info.append(f"{status_text} {' '.join(train_info_parts)}")
                    
                    # 如果沒有具體的列車資訊，檢查是否有更新時間
                    if not trains_info and (update_time or src_update_time):
                        trains_info.append("📡 資料已更新但無即將到站列車")
                        
                except Exception as train_error:
                    logger.warning(f"處理車站 {station_name_zh} 列車資料時發生錯誤: {str(train_error)}")
                
                # 組合顯示資訊
                if trains_info:
                    train_text = '\n'.join(trains_info)
                else:
                    # 根據時間提供更友善的提示
                    import datetime
                    current_hour = datetime.datetime.now().hour
                    if 1 <= current_hour <= 5:
                        train_text = "🌙 深夜時段，捷運暫停營運"
                    elif 0 <= current_hour <= 6 or 23 <= current_hour <= 23:
                        train_text = "⏰ 非營運時間或班次較少"
                    else:
                        train_text = "📭 暫無即將到站列車"
                
                # 添加到embed (限制字數以避免過長)
                field_name = f"🚉 {station_name_zh}"
                if line_info != '未知路線':
                    field_name += f" ({line_info})"
                
                embed.add_field(
                    name=field_name,
                    value=train_text[:100] + ("..." if len(train_text) > 100 else ""),
                    inline=False
                )
                
            except Exception as field_error:
                logger.warning(f"處理車站資料時發生錯誤: {str(field_error)}")
                continue
        
        # 添加頁面資訊
        if self.total_pages > 1:
            embed.add_field(
                name="📊 頁面資訊",
                value=f"第 {self.current_page + 1} 頁，共 {self.total_pages} 頁 | 總共 {len(self.liveboard_data)} 個車站",
                inline=False
            )
        else:
            embed.add_field(
                name="📊 資料統計",
                value=f"共 {len(self.liveboard_data)} 個車站",
                inline=False
            )
        
        # 設定頁腳
        embed.set_footer(text="資料來源: 交通部TDX平台 | 即時更新")
        
        return embed
    
    async def on_timeout(self):
        """處理超時"""
        # 禁用所有按鈕
        for item in self.children:
            item.disabled = True

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


# 台鐵電子看板翻頁視圖類
class TRALiveboardView(View):
    def __init__(self, interaction, county, station_name, station_id):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.cog = interaction.client.get_cog('InfoCommands')
        self.county = county
        self.station_name = station_name
        self.station_id = station_id
        self.current_page = 0
        self.per_page = 8
        self.trains = []
    
    async def send_with_view(self):
        embed = await self.get_liveboard_data()
        await self.interaction.edit_original_response(embed=embed, view=self)
    
    async def get_liveboard_data(self):
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
                access_token = await self.cog.get_tdx_access_token()
                
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json',
                    'User-Agent': 'DiscordBot/1.0'
                }
                
                url = f"https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard/Station/{self.station_id}?%24format=JSON"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.trains = data
                        return self.format_liveboard_data()
                    else:
                        embed = discord.Embed(
                            title="❌ 錯誤",
                            description="無法獲取台鐵到站資訊",
                            color=0xFF0000
                        )
                        return embed
        except Exception as e:
            embed = discord.Embed(
                title="❌ 錯誤",
                description=f"獲取台鐵到站資訊時發生錯誤：{str(e)}",
                color=0xFF0000
            )
            return embed
    
    def format_liveboard_data(self):
        total_pages = (len(self.trains) + self.per_page - 1) // self.per_page if self.trains else 1
        
        embed = discord.Embed(
            title=f"🚆 {self.station_name} 台鐵電子看板",
            color=0x0099FF,
            timestamp=datetime.datetime.now()
        )
        
        if not self.trains:
            embed.description = "目前沒有列車資訊"
            embed.set_footer(text="資料來源：TDX運輸資料流通服務")
            return embed
        
        start_idx = self.current_page * self.per_page
        end_idx = start_idx + self.per_page
        page_trains = self.trains[start_idx:end_idx]
        
        train_info = []
        current_time = datetime.datetime.now()
        
        for train in page_trains:
            train_no = train.get('TrainNo', 'N/A')
            train_type = train.get('TrainTypeName', {}).get('Zh_tw', 'N/A')
            direction = train.get('Direction', 0)
            direction_str = "順行(南下)" if direction == 0 else "逆行(北上)"
            
            # 到站時間
            scheduled_arrival = train.get('ScheduledArrivalTime', '')
            scheduled_departure = train.get('ScheduledDepartureTime', '')
            delay_time = train.get('DelayTime', 0)
            
            # 終點站
            end_station = train.get('EndingStationName', {}).get('Zh_tw', 'N/A')
            
            # 車廂資訊
            car_class = train.get('TrainClassificationName', {}).get('Zh_tw', '')
            
            # 計算進站剩餘時間
            time_until_arrival = ""
            arrival_status = ""
            
            if scheduled_arrival:
                try:
                    # 解析排定到站時間
                    today = current_time.date()
                    arrival_datetime = datetime.datetime.combine(today, datetime.datetime.strptime(scheduled_arrival, '%H:%M:%S').time())
                    
                    # 如果排定時間已過，可能是明天的班車
                    if arrival_datetime < current_time:
                        arrival_datetime += datetime.timedelta(days=1)
                    
                    # 考慮誤點時間
                    actual_arrival = arrival_datetime + datetime.timedelta(minutes=delay_time)
                    
                    # 計算剩餘時間
                    time_diff = actual_arrival - current_time
                    
                    if time_diff.total_seconds() <= 0:
                        arrival_status = "🚆 **列車進站中**"
                    elif time_diff.total_seconds() <= 120:  # 2分鐘內
                        arrival_status = "🔥 **即將進站**"
                        total_seconds = int(time_diff.total_seconds())
                        minutes = total_seconds // 60
                        seconds = total_seconds % 60
                        if minutes > 0:
                            time_until_arrival = f"⏰ 還有 {minutes} 分 {seconds} 秒"
                        else:
                            time_until_arrival = f"⏰ 還有 {seconds} 秒"
                    elif time_diff.total_seconds() <= 900:  # 15分鐘內
                        total_seconds = int(time_diff.total_seconds())
                        minutes = total_seconds // 60
                        seconds = total_seconds % 60
                        arrival_status = "🟡 **即將到達**"
                        time_until_arrival = f"⏰ 還有 {minutes} 分 {seconds} 秒"
                    else:
                        total_seconds = int(time_diff.total_seconds())
                        minutes = total_seconds // 60
                        arrival_status = "⏱️ **正常班車**"
                        time_until_arrival = f"⏰ 還有 {minutes} 分鐘"
                    
                    # 顯示排定時間
                    arrival_time = datetime.datetime.strptime(scheduled_arrival, '%H:%M:%S').strftime('%H:%M')
                    if delay_time > 0:
                        time_info = f"預定: {arrival_time} (誤點{delay_time}分)"
                    else:
                        time_info = f"預定: {arrival_time}"
                        
                except Exception as e:
                    time_info = f"預定: {scheduled_arrival}"
            
            if scheduled_departure:
                try:
                    departure_time = datetime.datetime.strptime(scheduled_departure, '%H:%M:%S').strftime('%H:%M')
                    if time_info:
                        time_info += f" | 開車: {departure_time}"
                    else:
                        time_info = f"開車: {departure_time}"
                except:
                    if time_info:
                        time_info += f" | 開車: {scheduled_departure}"
                    else:
                        time_info = f"開車: {scheduled_departure}"
            
            # 組裝列車詳細資訊
            train_detail = f"**{train_no}車次** ({train_type})\n"
            train_detail += f"🎯 終點: {end_station}\n"
            train_detail += f"📍 方向: {direction_str}\n"
            
            if car_class:
                train_detail += f"🚃 車種: {car_class}\n"
            
            # 優先顯示進站狀態
            if arrival_status:
                train_detail += f"{arrival_status}\n"
            
            if time_until_arrival:
                train_detail += f"{time_until_arrival}\n"
            
            if time_info:
                train_detail += f"📅 {time_info}"
            
            train_info.append(train_detail)
        
        if train_info:
            embed.description = "\n\n".join(train_info)
        
        embed.set_footer(text=f"資料來源：TDX運輸資料流通服務 | 第 {self.current_page + 1}/{total_pages} 頁")
        
        # 更新按鈕狀態
        self.update_buttons(total_pages)
        
        return embed
    
    def update_buttons(self, total_pages):
        # 更新上一頁按鈕
        self.children[0].disabled = (self.current_page == 0)
        # 更新下一頁按鈕
        self.children[2].disabled = (self.current_page >= total_pages - 1)
    
    @discord.ui.button(label="⬅️ 上一頁", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("你沒有權限操作這個按鈕！", ephemeral=True)
            return
        
        if self.current_page > 0:
            self.current_page -= 1
            embed = self.format_liveboard_data()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="🔄 重新整理", style=discord.ButtonStyle.primary)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("你沒有權限操作這個按鈕！", ephemeral=True)
            return
        
        await interaction.response.defer()
        embed = await self.get_liveboard_data()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label="➡️ 下一頁", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("你沒有權限操作這個按鈕！", ephemeral=True)
            return
        
        total_pages = (len(self.trains) + self.per_page - 1) // self.per_page if self.trains else 1
        if self.current_page < total_pages - 1:
            self.current_page += 1
            embed = self.format_liveboard_data()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()


# 台鐵誤點查詢翻頁視圖類
class TRADelayView(View):
    def __init__(self, interaction, county):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.cog = interaction.client.get_cog('InfoCommands')
        self.county = county
        self.current_page = 0
        self.per_page = 8
        self.delays = []
    
    async def send_with_view(self):
        embed = await self.get_delay_data()
        await self.interaction.edit_original_response(embed=embed, view=self)
    
    async def get_delay_data(self):
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
                access_token = await self.cog.get_tdx_access_token()
                
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json',
                    'User-Agent': 'DiscordBot/1.0'
                }
                
                # 如果指定縣市，篩選該縣市的車站
                if self.county and self.county in TRA_STATIONS:
                    station_ids = [station['id'] for station in TRA_STATIONS[self.county]]
                    station_filter = "(" + " or ".join([f"OriginStopTime/StationID eq '{sid}' or DestinationStopTime/StationID eq '{sid}'" for sid in station_ids]) + ")"
                    url = f"https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveTrainDelay?%24filter={station_filter}&%24format=JSON"
                else:
                    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveTrainDelay?%24format=JSON"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        # 只保留有誤點的列車
                        self.delays = [train for train in data if train.get('DelayTime', 0) > 0]
                        # 按誤點時間排序（由高到低）
                        self.delays.sort(key=lambda x: x.get('DelayTime', 0), reverse=True)
                        return self.format_delay_data()
                    else:
                        embed = discord.Embed(
                            title="❌ 錯誤",
                            description="無法獲取台鐵誤點資訊",
                            color=0xFF0000
                        )
                        return embed
        except Exception as e:
            embed = discord.Embed(
                title="❌ 錯誤",
                description=f"獲取台鐵誤點資訊時發生錯誤：{str(e)}",
                color=0xFF0000
            )
            return embed
    
    def format_delay_data(self):
        total_pages = (len(self.delays) + self.per_page - 1) // self.per_page if self.delays else 1
        
        title = f"🚆 台鐵誤點資訊"
        if self.county:
            title += f" - {self.county}"
        
        embed = discord.Embed(
            title=title,
            color=0xFF9900,
            timestamp=datetime.datetime.now()
        )
        
        if not self.delays:
            embed.description = "目前沒有誤點列車 ✅"
            embed.color = 0x00FF00
            embed.set_footer(text="資料來源：TDX運輸資料流通服務")
            return embed
        
        start_idx = self.current_page * self.per_page
        end_idx = start_idx + self.per_page
        page_delays = self.delays[start_idx:end_idx]
        
        delay_info = []
        for train in page_delays:
            train_no = train.get('TrainNo', 'N/A')
            train_type = train.get('TrainTypeName', {}).get('Zh_tw', 'N/A')
            delay_time = train.get('DelayTime', 0)
            
            # 起點和終點
            origin_station = train.get('OriginStopTime', {}).get('StationName', {}).get('Zh_tw', 'N/A')
            dest_station = train.get('DestinationStopTime', {}).get('StationName', {}).get('Zh_tw', 'N/A')
            
            # 更新時間
            update_time = train.get('UpdateTime', '')
            if update_time:
                try:
                    dt = datetime.datetime.fromisoformat(update_time.replace('Z', '+00:00'))
                    update_str = dt.strftime('%H:%M')
                except:
                    update_str = ''
            else:
                update_str = ''
            
            delay_detail = f"**{train_no}車次** ({train_type})\n"
            delay_detail += f"🚨 誤點: **{delay_time}分鐘**\n"
            delay_detail += f"📍 {origin_station} → {dest_station}"
            if update_str:
                delay_detail += f"\n🕐 更新時間: {update_str}"
            
            delay_info.append(delay_detail)
        
        if delay_info:
            embed.description = "\n\n".join(delay_info)
        
        embed.set_footer(text=f"資料來源：TDX運輸資料流通服務 | 第 {self.current_page + 1}/{total_pages} 頁")
        
        # 更新按鈕狀態
        self.update_buttons(total_pages)
        
        return embed
    
    def update_buttons(self, total_pages):
        # 更新上一頁按鈕
        self.children[0].disabled = (self.current_page == 0)
        # 更新下一頁按鈕
        self.children[2].disabled = (self.current_page >= total_pages - 1)
    
    @discord.ui.button(label="⬅️ 上一頁", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("你沒有權限操作這個按鈕！", ephemeral=True)
            return
        
        if self.current_page > 0:
            self.current_page -= 1
            embed = self.format_delay_data()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="🔄 重新整理", style=discord.ButtonStyle.primary)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("你沒有權限操作這個按鈕！", ephemeral=True)
            return
        
        await interaction.response.defer()
        embed = await self.get_delay_data()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label="➡️ 下一頁", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("你沒有權限操作這個按鈕！", ephemeral=True)
            return
        
        total_pages = (len(self.delays) + self.per_page - 1) // self.per_page if self.delays else 1
        if self.current_page < total_pages - 1:
            self.current_page += 1
            embed = self.format_delay_data()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

async def setup(bot):
    await bot.add_cog(InfoCommands(bot))
