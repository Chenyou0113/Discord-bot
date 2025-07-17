# 🤖 Discord 氣象地震交通機器人

一個功能完整的 Discord 機器人，提供台灣地區的地震資訊、天氣預報、氣象站觀測資料、水利防災影像以及公路監視器查詢服務。

## 🔧 故障排除

### 常見問題與解決方案

#### 1. 機器人無法顯示圖片或嵌入內容
**症狀**: 機器人回應指令但只顯示純文字，沒有圖片
**解決方案**:
- 檢查機器人是否具有「嵌入連結 (Embed Links)」權限
- 確認「附加檔案 (Attach Files)」權限已開啟
- 詳細權限設定請參考 `discord_permission_setup_guide.txt`

#### 2. 斜線指令無法使用
**症狀**: 無法看到或使用斜線指令
**解決方案**:
- 確認機器人具有「使用斜線指令 (Use Application Commands)」權限
- 重新邀請機器人並確保權限正確
- 等待 Discord 同步斜線指令 (通常需要 1-5 分鐘)

#### 3. 啟動時出現 Token 錯誤
**症狀**: `錯誤: 找不到 DISCORD_TOKEN 環境變數`
**解決方案**:
```bash
# 確認 .env 檔案存在並包含正確的 Token
echo DISCORD_TOKEN=你的機器人Token > .env
```

#### 4. API 請求失敗或超時
**症狀**: 查詢功能回應「查詢失敗」或超時
**解決方案**:
- 檢查網路連線
- 確認防火牆沒有阻擋機器人
- 稍後重試，可能是 API 伺服器繁忙

#### 5. Python 模組導入錯誤
**症狀**: `ModuleNotFoundError` 或導入失敗
**解決方案**:
```bash
# 重新安裝依賴套件
pip install -r requirements.txt

# 如果使用虛擬環境
pip install --upgrade -r requirements.txt
```

#### 6. 監視器圖片載入失敗
**症狀**: 監視器查詢顯示「圖片載入失敗」
**解決方案**:
- 切換資料來源 (使用 `data_source` 參數)
- 嘗試其他監視器點位
- 檢查目標監視器是否正常運作

### 🛠️ 除錯指令
```bash
# 檢查 Python 環境
python --version

# 測試 Discord.py 安裝
python -c "import discord; print(discord.__version__)"

# 執行內建測試
python tests/simple_function_test.py
```

### 📞 取得協助
如果問題仍未解決：
1. 查看 `bot.log` 檔案中的錯誤訊息
2. 檢查是否有相關的 [GitHub Issues](../../issues)
3. 創建新的 Issue 並附上錯誤訊息和環境資訊

## 🔄 更新日誌

### 🔔 地震監控
- **即時地震通知**: 自動監控中央氣象署地震資料，即時推送最新地震資訊
- **地震資訊查詢**: 支援一般地震和小區域地震資料查詢
- **詳細震度資訊**: 提供震央位置、規模、深度及各地震度分布

### 🌤️ 天氣服務
- **天氣預報查詢**: 支援全台各縣市 36 小時天氣預報
- **互動式選單**: 使用下拉選單快速選擇查詢地區
- **詳細氣象資訊**: 包含溫度、濕度、降雨機率、風速等完整資訊

### 🌡️ 氣象站觀測
- **即時觀測資料**: 查詢全台 500+ 個自動氣象站的即時觀測資料
- **多種查詢模式**: 支援全台概況、地區查詢、單一測站詳細資料
- **翻頁瀏覽功能**: 當查詢結果過多時，提供翻頁按鈕便於瀏覽
- **重新整理功能**: 可即時更新最新的觀測資料

### 💧 水利防災影像 (新功能)
- **監控影像查詢**: 查詢全台 170+ 個水利防災監控點影像
- **地區搜尋**: 支援縣市名稱或監控站名稱搜尋
- **即時影像顯示**: 提供即時的河川、水位監控影像
- **詳細位置資訊**: 顯示監控點位置、河川名稱、運作狀態等

### 🛣️ 公路監視器查詢 (整合版)
- **國道監視器**: 整合 TDX 與高速公路局 XML 資料，雙重資料來源保障
- **公路監視器**: 整合 TDX 與公路總局 XML 資料，涵蓋全台 2300+ 監視器
- **多資料來源選擇**: 支援自動合併、單一來源或混合查詢模式
- **智能縣市篩選**: 基於地名關鍵字和官方縣市對照表的精確篩選
- **道路類型篩選**: 支援台1線至台88線等25個主要省道查詢
- **即時路況影像**: 提供即時的道路交通狀況影像和快照

### 🏞️ 水庫水情查詢
- **水庫資訊**: 查詢全台主要水庫的蓄水量、水位等資訊
- **即時水情**: 提供最新的水庫營運狀態

### 🌊 海嘯警報
- **海嘯資訊監控**: 查詢最新海嘯警報和相關資訊

## 🎮 指令列表

### 氣象地震類
| 指令 | 描述 | 參數 |
|------|------|------|
| `/earthquake` | 查詢最新地震資訊 | `type`: "normal" 或 "small" |
| `/weather` | 查詢天氣預報 | `location`: 縣市名稱 (可選) |
| `/weather_station` | 查詢氣象站觀測資料 | `station_id`: 測站代碼 (可選)<br>`location`: 地區名稱 (可選) |
| `/tsunami` | 查詢海嘯資訊 | 無 |

### 水利防災類
| 指令 | 描述 | 參數 |
|------|------|------|
| `/water_cameras` | 查詢水利防災監控影像 | `location`: 地區名稱 (可選) |
| `/reservoir_info` | 查詢水庫資訊 | `reservoir_id`: 水庫代碼 (可選) |
| `/water_level` | 查詢即時水位資訊 | 無 |

### 交通監控類
| 指令 | 描述 | 參數 |
|------|------|------|
| `/national_highway_cameras` | 查詢國道監視器影像 (整合TDX+高速公路局) | `highway_number`: 國道號碼 (如：1、3、5)<br>`location`: 地點 (可選)<br>`direction`: 方向 (可選)<br>`city`: 縣市 (可選)<br>`data_source`: 資料來源 (可選) |
| `/highway_cameras` | 查詢公路監視器 (整合TDX+公路總局) | `county`: 縣市 (19個選項)<br>`road_type`: 道路類型 (25個台線選項)<br>`data_source`: 資料來源 (可選) |

#### 資料來源選項
- `merged` (預設): 自動合併 TDX + 官方 XML 資料
- `tdx`: 僅 TDX 運輸資料流通服務平臺
- `highway_bureau` / `freeway`: 僅交通部官方 XML 資料

### 管理類
| 指令 | 描述 | 權限要求 |
|------|------|----------|
| `/set_earthquake_channel` | 設定地震通知頻道 | 管理員權限 |

## 🚀 快速開始

### 環境需求
- Python 3.8+
- Discord 機器人 Token
- 網路連接

### 機器人權限設定
在邀請機器人到您的伺服器時，請確保授予以下權限：
- ✅ **檢視頻道** (View Channels)
- ✅ **發送訊息** (Send Messages)  
- ⭐ **嵌入連結** (Embed Links) - **重要！** 顯示圖片和嵌入式內容必需
- ✅ **使用斜線指令** (Use Application Commands)
- ✅ **附加檔案** (Attach Files) - 建議開啟
- ✅ **讀取訊息記錄** (Read Message History) - 建議開啟

> 💡 **提示**: 如果機器人無法顯示圖片，請檢查「嵌入連結」權限是否已開啟
> 
> 詳細權限設定指南請參考：[discord_permission_setup_guide.txt](discord_permission_setup_guide.txt)
- Discord.py 2.3+
- aiohttp
- xmltodict
- ssl (用於 HTTPS 連線)

### 安裝步驟

1. **克隆專案**
   ```bash
   git clone [repository-url]
   cd Discord-bot
   ```

2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **設定環境變數**
   ```bash
   # 複製範例環境變數檔案
   cp .env.example .env
   
   # 編輯 .env 檔案，填入您的 Discord Bot Token
   # Windows 用戶可以直接複製檔案：
   # copy .env.example .env
   ```
   
   **重要**: 在 `.env` 檔案中設定您的 Discord Bot Token：
   ```env
   DISCORD_TOKEN=您的機器人Token
   GOOGLE_API_KEY=您的Google_API金鑰（可選）
   ```
   
   > 📝 **如何取得 Discord Bot Token**:
   > 1. 前往 [Discord Developer Portal](https://discord.com/developers/applications)
   > 2. 創建新應用程式 → Bot → 複製 Token
   > 3. 將 Token 填入 `.env` 檔案中

4. **啟動機器人**
   ```bash
   python bot.py
   ```

## 🎯 功能使用範例

### 水利防災影像查詢
```
/water_cameras                          # 查看全台監控點分布
/water_cameras location:台北             # 查看台北地區監控影像
/water_cameras location:台南溪頂寮大橋    # 查看特定監控點影像
```

### 公路監視器查詢 (整合版)
```
# 預設合併模式 - 使用兩個資料來源
/highway_cameras county:台北 road_type:台1線

# 指定單一資料來源
/highway_cameras county:新北 road_type:台62線 data_source:highway_bureau
/highway_cameras county:桃園 data_source:tdx

# 國道監視器查詢
/national_highway_cameras highway_number:1 city:台中
/national_highway_cameras highway_number:3 data_source:freeway
```

### 氣象站查詢
```
/weather_station                        # 顯示全台主要縣市概況
/weather_station location:台北           # 查詢台北地區所有氣象站
/weather_station station_id:466920      # 查詢特定測站 (台北)4. **啟動機器人**
   ```bash
   python bot.py
   ```

## 🔧 配置說明

### Discord Bot 設定
1. 前往 [Discord Developer Portal](https://discord.com/developers/applications)
2. 創建新的應用程式和機器人
3. 取得 Bot Token 並設定在 `.env` 檔案中
4. 確保機器人具有以下權限：
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Read Message History
   - Attach Files

### API 設定
本機器人使用以下官方開放資料 API，無需額外申請 API Key：
- 中央氣象署開放資料 API
- 經濟部水利署防災資訊 API
- **TDX 運輸資料流通服務平臺 API** (需註冊取得 Client ID/Secret)
- **交通部高速公路局 CCTV XML API**
- **交通部公路總局 CCTV XML API**

#### TDX API 設定
1. 前往 [TDX 運輸資料流通服務平臺](https://tdx.transportdata.tw/)
2. 註冊帳號並申請應用程式
3. 取得 Client ID 和 Client Secret
4. 在程式中設定相關憑證 (已預設為範例值)

## 📁 專案結構

```
Discord bot/
├── bot.py                              # 主程式入口
├── cogs/
│   ├── info_commands_fixed_v4_clean.py # 氣象地震功能
│   └── reservoir_commands.py          # 水利交通功能
├── tests/                              # 測試檔案目錄
│   ├── test_bot_loading.py            # Bot 載入測試
│   ├── simple_function_test.py        # 基本功能測試
│   ├── final_verification.py          # 最終驗證測試
│   ├── test_weather_station_pagination.py # 翻頁功能測試
│   ├── test_water_cameras_fix.py      # 水利影像修復測試
│   └── final_core_functionality_test.py # 核心功能測試
├── scripts/                            # 輔助腳本
├── docs/                              # 說明文件
├── config_files/                      # 設定檔案
├── .env                               # 環境變數 (需自行創建)
├── .env.example                       # 環境變數範例
└── requirements.txt                   # Python 依賴清單
```

## 🎯 道路監視器整合系統詳解

### 🔄 雙資料來源整合
機器人採用先進的多資料來源整合技術：

#### � 資料來源對照表
| 來源 | 國道監視器 | 公路監視器 | 資料量 | 更新頻率 | 特色 |
|------|------------|------------|--------|----------|------|
| **TDX API** | ✅ 國道系統 | ✅ 省道系統 | ~100筆樣本 | 即時 | 資料欄位完整，API 穩定 |
| **高速公路局 XML** | ✅ 國道專用 | ❌ | 1000+ 筆 | 每小時 | 涵蓋全國道系統 |
| **公路總局 XML** | ❌ | ✅ 省道專用 | 2260+ 筆 | 每日 | 涵蓋全台省道快速公路 |

#### 🎛️ 查詢模式選擇
1. **智能合併模式** (`merged` - 預設)
   - 自動整合多個資料來源
   - 去除重複監視器
   - 提供最完整的監視器覆蓋

2. **TDX 專用模式** (`tdx`)
   - 使用運輸資料流通服務平臺
   - 資料即時性最佳
   - 適合需要最新資料的查詢

3. **官方 XML 模式** (`highway_bureau`/`freeway`)
   - 使用交通部官方 XML 資料
   - 監視器數量最多
   - 涵蓋範圍最廣

### 🏛️ 縣市篩選系統
採用官方業管機關代碼 (AuthorityCode) 對照表：

#### 縣市對照表
- **直轄市**: TPE(台北), NWT(新北), TYC(桃園), TCN(台中), TNN(台南), KHH(高雄)
- **縣市**: KEE(基隆), HSC(新竹市), HST(新竹縣), MIA(苗栗), 等...
- **分局對應**: 
  - THB-1R (基隆/台北/新北)
  - THB-2R (桃園/新竹)
  - THB-3R (苗栗/台中/彰化/南投)
  - THB-4R (雲林/嘉義/台南)
  - THB-5R (高雄/屏東)
  - THB-EO (宜蘭/花蓮/台東)

#### 智能關鍵字搜尋
每個縣市包含：
- 主要地名和行政區
- 交流道和重要地標
- 區域性名稱變體
- 例：台北 → ['台北', '北市', '臺北', '大安', '信義', '松山', '天母', '關渡']

### 🛣️ 道路類型支援
支援 25 個主要台線 (符合 Discord Choices 限制)：
- **縱貫線**: 台1線, 台3線, 台9線
- **橫貫線**: 台8線, 台18線, 台20線  
- **快速道路**: 台61線, 台62線, 台64線, 台66線, 台68線, 台88線
- **重要省道**: 台2線, 台4線, 台5線, 台7線, 台11線, 台14線, 台15線, 台17線, 台19線, 台21線, 台24線, 台26線

## 🧪 測試系統

### 執行完整測試套件
```bash
# 核心功能測試
python final_core_functionality_test.py

# 水利影像修復測試  
python test_water_cameras_fix.py

# 道路分類測試
python diagnose_highway_classification.py
```

### 測試涵蓋範圍
- ✅ 水利防災影像 KeyError 修復驗證
- ✅ 道路分類準確性測試 (準確率 100%)
- ✅ API 連線狀態檢查
- ✅ 資料格式化完整性驗證
- ✅ 翻頁功能測試
- ✅ Bot 載入和權限測試

## 📊 API 資料來源

### 氣象地震類
- **地震資料**: 中央氣象署地震報告 API
- **天氣預報**: 中央氣象署天氣預報 API  
- **氣象站資料**: 中央氣象署自動氣象站觀測資料 API
- **海嘯資料**: 中央氣象署海嘯資訊 API

### 水利防災類
- **水利防災影像**: 經濟部水利署防災資訊 API (171個監控點)
- **水庫資訊**: 經濟部水利署水庫即時水情 API
- **水位資料**: 水利署水位觀測 API

### 交通監控類
- **公路監視器**: 整合 TDX 與公路總局 XML 資料 (2,300+ 監視器)
- **國道監視器**: 整合 TDX 與高速公路局 XML 資料 (1,000+ 監視器)
- **即時路況**: 公路總局路況資訊 API

## 🛠️ 開發功能

### ✅ 已實現功能
- ✅ 地震監控和通知系統
- ✅ 天氣預報查詢
- ✅ 氣象站觀測資料查詢
- ✅ 翻頁瀏覽功能
- ✅ 海嘯警報查詢
- ✅ **水利防災影像查詢** (新功能)
- ✅ **整合版公路監視器查詢** (升級版)
  - ✅ **雙資料來源整合** (TDX + 官方XML)
  - ✅ **智能縣市篩選系統**
  - ✅ **25個主要道路類型支援**
  - ✅ **多查詢模式選擇**
- ✅ **國道監視器雙來源整合** (升級版)
- ✅ 水庫水情查詢
- ✅ 自動重新整理
- ✅ 用戶權限控制
- ✅ 錯誤處理和重試機制

### 🔧 最新修復
- ✅ **公路監視器雙資料來源整合** (2025-07-11)
  - ✅ TDX API + 公路總局 XML API 整合
  - ✅ 官方縣市對照表 (AuthorityCode) 實作
  - ✅ 智能關鍵字搜尋系統
  - ✅ 三種查詢模式 (合併/TDX/官方XML)
- ✅ **國道監視器雙資料來源整合** (2025-07-11)
  - ✅ TDX API + 高速公路局 XML API 整合
  - ✅ 完整國道系統覆蓋 (1000+ 監視器)
- ✅ **Discord Choices 限制修復** (2025-07-08)
  - ✅ 道路類型選項精簡至 25 個
  - ✅ 符合 Discord API 規範
- ✅ **水利防災影像 KeyError 修復** (2025-06-29)
- ✅ **國道與快速公路分類優化** (2025-06-29)
- ✅ **監視器查詢指令分離** (2025-06-29)
- ✅ **format_water_image_info 回傳欄位完整化** (2025-06-29)

### 🎯 技術特色
- **異步處理**: 使用 asyncio 和 aiohttp 提升效能
- **模組化設計**: 使用 Discord.py Cogs 系統
- **智能快取**: 減少 API 調用次數
- **容錯機制**: 完整的錯誤處理和自動重試
- **用戶體驗**: 友善的互動介面和即時回應
- **多資料來源整合**: TDX + 官方 XML 雙重保障
- **智能篩選系統**: 官方縣市對照表 + 關鍵字搜尋
- **彈性查詢模式**: 支援合併、單一來源、混合查詢
- **防快取機制**: 監視器圖片 URL 時間戳處理
- **XML 命名空間處理**: 正確解析複雜 XML 結構

## 📝 更新日誌

### v6.0 (2025-07-11) 🎉 重大整合更新
- ✨ **公路監視器雙資料來源整合**
  - 整合 TDX API (運輸資料流通服務平臺) + 公路總局 XML API
  - 監視器數量從 ~50 增加到 2,300+ 個
  - 支援自動合併、TDX專用、官方XML專用三種查詢模式
  - 實作官方業管機關代碼 (AuthorityCode) 縣市對照表
  - 智能關鍵字搜尋系統，每縣市包含地名、行政區、地標關鍵字
- ✨ **國道監視器雙資料來源整合**
  - 整合 TDX API + 高速公路局 XML API  
  - 完整覆蓋全國道系統 (1,000+ 監視器)
  - 支援多資料來源切換查詢
- 🔧 **Discord API 規範優化**
  - 道路類型選項精簡至 25 個主要台線
  - 符合 Discord Choices 限制規範
  - 保留最重要的縱貫線、橫貫線、快速道路
- 🔧 **技術架構改進**
  - XML 命名空間正確處理
  - 防快取時間戳機制
  - 統一資料格式標準化
  - 完整錯誤處理和重試機制

### v5.0 (2025-06-30) 🎉 重大更新
- ✨ **新增水利防災影像查詢功能**
  - 支援全台 171 個水利防災監控點查詢
  - 地區搜尋和特定監控站查詢
  - 即時河川、水位監控影像顯示
- ✨ **新增公路監視器查詢系統**
  - 國道監視器專用查詢 (`/national_highway_cameras`)
  - 快速公路/省道監視器查詢 (`/general_road_cameras`)
  - 智能道路分類系統，準確率 100%
- 🔧 **修復水利防災影像 KeyError 問題**
  - 完善 `format_water_image_info` 函數回傳結構
  - 新增 county、district、address、station_id、source 欄位
- 🔧 **優化道路分類演算法**
  - 快速公路優先判斷，避免誤分類為國道
  - 台62、台64 等快速公路正確分類
- ✨ **新增水庫水情查詢功能**
  - 支援全台主要水庫即時水情查詢
  - 蓄水量、水位等詳細資訊顯示
- 📁 **完善測試系統**
  - 新增核心功能驗證測試
  - 水利影像修復專用測試
  - 道路分類準確性測試

### v4.0 (2025-06-25)
- ✨ 新增氣象站觀測資料查詢功能
- ✨ 實現翻頁瀏覽系統
- 🔧 修復地震功能的資料結構問題
- 📁 重新整理測試檔案結構
- 📖 完善說明文件

### v3.x
- 修復地震 API 相關問題
- 改善天氣預報功能
- 新增海嘯警報功能

## 🔒 安全性與效能

### 安全性考量
- ✅ **環境變數保護**: 敏感資訊 (如 Token) 存放在 `.env` 檔案中
- ✅ **權限最小化**: 機器人僅要求必要的 Discord 權限
- ✅ **輸入驗證**: 所有用戶輸入都經過驗證和清理
- ✅ **錯誤處理**: 避免洩露系統內部資訊
- ⚠️ **管理員權限**: 部分管理功能需要適當的權限檢查

### 效能最佳化
- ⚡ **非同步處理**: 使用 `asyncio` 和 `aiohttp` 提升回應速度
- 📦 **資料快取**: 減少重複 API 請求，提升查詢效率
- 🔄 **連線池管理**: 有效管理 HTTP 連線資源
- ⏱️ **超時設定**: 避免長時間等待造成的阻塞
- 📊 **批次處理**: 大量資料採用分頁顯示

### 監控與日誌
機器人會自動記錄以下資訊到 `bot.log`：
- 指令使用統計
- API 請求狀態
- 錯誤和警告訊息
- 系統啟動和關閉事件

## 🤝 貢獻指南

### 開發環境設置
1. Fork 本專案
2. 克隆您的 Fork
   ```bash
   git clone https://github.com/YOUR_USERNAME/Discord-bot.git
   cd Discord-bot
   ```
3. 創建虛擬環境 (建議)
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```
4. 安裝開發依賴
   ```bash
   pip install -r requirements.txt
   ```

### 開發流程
1. 創建功能分支
   ```bash
   git checkout -b feature/新功能名稱
   ```
2. 進行開發並測試
   ```bash
   # 執行測試確保功能正常
   python tests/simple_function_test.py
   python tests/final_verification.py
   ```
3. 提交更改
   ```bash
   git add .
   git commit -m "新增: 簡短描述新功能"
   ```
4. 推送到您的 Fork
   ```bash
   git push origin feature/新功能名稱
   ```
5. 創建 Pull Request

### 程式碼規範
- 使用 4 個空格縮排
- 函數和變數名使用蛇式命名法 (snake_case)
- 類別名使用帕斯卡命名法 (PascalCase)
- 加入適當的註解和文檔字串
- 遵循 PEP 8 程式碼風格指南

### 測試規範
在提交 PR 前，請確保：
- [ ] 所有現有測試通過
- [ ] 新功能包含相應的測試
- [ ] 測試覆蓋率維持在合理水準
- [ ] 手動測試新功能在 Discord 中正常運作

### 提交訊息格式
使用以下格式撰寫提交訊息：
```
類型: 簡短描述 (不超過 50 字元)

詳細描述 (如果需要)
- 說明更改的原因
- 描述解決的問題
- 列出相關的 Issue 編號
```

類型包括：
- `新增`: 新功能
- `修復`: Bug 修復
- `更新`: 現有功能改進
- `重構`: 程式碼重構
- `文檔`: 文檔更新
- `測試`: 測試相關更改

### 新增功能建議
如果您想新增功能，建議先：
1. 開啟 Issue 討論功能需求
2. 確認功能符合專案目標
3. 考慮 API 限制和效能影響
4. 設計用戶友善的指令介面

## 📄 授權

本專案使用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 📞 支援

如果您遇到問題或有功能建議，請：
1. 查看 [Issues](../../issues) 是否已有相關討論
2. 創建新的 Issue 描述您的問題
3. 查看專案的說明文件和測試範例

## 🌟 致謝

- 感謝中央氣象署提供開放資料 API
- 感謝經濟部水利署提供水利防災資訊 API
- 感謝交通部高速公路局提供路況監視器 API
- 感謝 Discord.py 開發團隊
- 感謝所有貢獻者和使用者的回饋

---

**最後更新**: 2025年7月11日  
**版本**: v6.0  
**維護狀態**: 🟢 積極維護  
**功能狀態**: ✅ 所有核心功能正常運作  
**重大更新**: 🎉 公路監視器雙資料來源整合完成  
**文檔狀態**: 📚 完整更新 (包含故障排除、開發指南、安全性說明)
