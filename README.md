# 🤖 Discord 氣象地震交通機器人

一個功能完整的 Discord 機器人，提供台灣地區的地震資訊、天氣預報、氣象站觀測資料、水利防災影像以及公路監視器查詢服務。

## API 使用限制與配額

### TDX API 限制
- **請求頻率**: 每秒最多 60 次請求
- **每日配額**: 無限制 (需註冊)
- **建議**: 實作適當的請求間隔避免 429 錯誤

### 中央氣象署 API 限制
- **請求頻率**: 每分鐘 100 次請求
- **每日配額**: 10,000 次請求
- **自動重試**: 程式已內建重試機制

### 監視器影像更新頻率
- **國道監視器**: 每 30 秒更新
- **公路監視器**: 每 1-2 分鐘更新
- **水利防災影像**: 每 5-10 分鐘更新

## 🔧 技術細節

### 🚀 批次檔修復指南

#### 常見批次檔問題
**問題**: 執行 `.bat` 檔案時出現錯誤代碼 9009 或「找不到 python 命令」

**原因分析**:
- 原有批次檔使用 `call venv\Scripts\activate.bat` 後執行 `python`
- 在 Windows 批次檔中，環境變數變更不會保持到後續命令
- 硬編碼的專案路徑導致路徑錯誤

**修復方案** (已應用到所有批次檔):
```batch
@echo off
chcp 65001 >nul
cd /d "%~dp0"  REM 動態路徑定位

REM 直接使用虛擬環境 Python
if exist "venv\Scripts\python.exe" (
    echo 使用虛擬環境 Python...
    "venv\Scripts\python.exe" bot.py
) else (
    echo 使用系統 Python...
    python bot.py
)
```

**已修復的批次檔列表**:
- ✅ `scripts/auto_restart_bot.bat` - 自動重啟腳本
- ✅ `scripts/auto_restart_bot_fixed.bat` - 自動重啟腳本 (修復版)
- ✅ `start_bot_simple.bat` - 簡易啟動腳本
- ✅ `quick_check.bat` - 快速狀態檢查
- ✅ `sync_commands.bat` - 指令同步腳本
- ✅ `test_config.bat` - 配置測試腳本
- ✅ `test_bot_simple.bat` - 機器人測試腳本
- ✅ 以及 `test_files/` 和 `scripts/` 中的其他 20+ 個批次檔

**使用建議**:
```bash
# 推薦: 使用自動重啟腳本
scripts\auto_restart_bot.bat

# 快速啟動 (開發用)
start_bot_simple.bat

# 系統狀態檢查
quick_check.bat
```

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

#### 8. 批次檔無法啟動機器人 (已修正)
**症狀**: 執行 `.bat` 檔案出現錯誤代碼 9009 或找不到 python 命令
**解決方案**: ✅ 已修正
- 所有批次檔已更新為直接使用虛擬環境中的 Python
- 自動偵測並使用 `venv\Scripts\python.exe`
- 移除硬編碼路徑，改用動態路徑 `%~dp0`
- 現在可正常使用 `auto_restart_bot.bat` 等啟動腳本

#### 9. 聊天 AI 功能異常
**症狀**: `/聊天` 指令無回應或回應錯誤
**解決方案**:
- 確認 `GOOGLE_API_KEY` 已正確設定在 `.env` 檔案中
- 檢查 Gemini API 配額是否已用完
- 機器人現已升級到 Gemini 2.0 Flash 模型

### 🛠️ 除錯指令
```bash
# 檢查 Python 環境
python --version

# 測試 Discord.py 安裝
python -c "import discord; print(discord.__version__)"

# 使用修復後的批次檔啟動 (推薦)
scripts\auto_restart_bot.bat

# 執行內建測試
python tests/simple_function_test.py

# 檢查虛擬環境狀態
scripts\test_venv.bat
```

### 📞 取得協助
如果問題仍未解決：
1. 查看 `bot.log` 檔案中的錯誤訊息
2. 檢查是否有相關的 [GitHub Issues](../../issues)
3. 創建新的 Issue 並附上錯誤訊息和環境資訊

## 🔄 更新日誌

### 🆕 最新更新 (2025年8月)

#### 🔧 批次檔修復 (v6.1)
- **✅ 虛擬環境啟動修復**: 修正所有 `.bat` 檔案的虛擬環境啟動問題
- **解決問題**: 修正錯誤代碼 9009 (找不到 python 命令)
- **修復方法**: 直接使用 `venv\Scripts\python.exe` 取代 `call activate` 方式
- **涵蓋範圍**: 修復 20+ 個批次檔，包含自動重啟、測試、配置腳本
- **路徑修正**: 統一使用 `%~dp0` 動態路徑，移除硬編碼路徑
- **啟動穩定性**: 自動重啟監控系統現已完全穩定運作

#### 🤖 AI 聊天系統優化
- **Gemini 2.0 Flash**: 升級到最新的 Gemini 2.0 Flash Experimental 模型
- **聊天功能**: 支援自然語言對話，智能回應用戶詢問
- **指令整合**: 60 個斜線指令完全同步，覆蓋所有功能模組
- **系統穩定性**: 13 個 Cogs 模組全部成功載入，無衝突

#### 🔄 自動重啟系統
- **監控機制**: 實時監控機器人狀態，異常時自動重啟
- **批次檔修復**: `auto_restart_bot.bat` 和 `auto_restart_bot_fixed.bat` 已修復
- **錯誤處理**: 提供詳細的錯誤代碼分析和解決建議
- **用戶體驗**: 支援手動確認重啟，避免無限迴圈

#### 🚆 台鐵電子看板修正
- **✅ 宜蘭縣車站ID修正**: 更新宜蘭縣22個車站ID從27xx系列更新為7xxx系列
- **解決問題**: 修正宜蘭縣台鐵電子看板「目前沒有列車資訊」錯誤
- **驗證完成**: 宜蘭車站現可正常顯示即時列車資訊
- **全面測試**: 已完成全台18個縣市台鐵電子看板功能驗證

#### 🚄 捷運與鐵路系統
- **捷運即時看板**: 新增台北捷運、高雄捷運、高雄輕軌即時電子看板查詢
- **鐵路事故查詢**: 支援台鐵、高鐵事故資訊查詢
- **捷運狀態監控**: 查詢各捷運系統運行狀態

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

### 🚆 台鐵電子看板 (已修正)
- **即時列車資訊**: 查詢全台各車站的即時到離站電子看板
- **全縣市支援**: 涵蓋18個縣市、300+ 個台鐵車站
- **誤點資訊**: 顯示列車誤點時間和預估到站時間
- **翻頁瀏覽**: 支援多頁列車資訊瀏覽
- **車站篩選**: 支援縣市和車站名稱快速篩選
- **✅ 宜蘭縣修正**: 已更新宜蘭縣22個車站ID (7xxx系列)，解決「目前沒有列車資訊」問題

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
| `/reservoir_info` | 查詢水庫資訊 | `reservoir_id`: 水庫代碼 (可選) |
| `/water_level` | 查詢即時水位資訊 | 無 |

### 交通監控類
| 指令 | 描述 | 參數 |
|------|------|------|
| `/台鐵電子看板` | 查詢台鐵車站即時電子看板 | `county`: 縣市 (18個選項)<br>`station_name`: 車站名稱 (可選) |
| `/台鐵誤點查詢` | 查詢台鐵列車誤點資訊 | `county`: 縣市 (可選，不選擇則查詢全台) |
| `/鐵路事故` | 查詢台鐵或高鐵事故資訊 | `鐵路類型`: "台鐵" 或 "高鐵" |
| `/捷運狀態` | 查詢各捷運系統運行狀態 | `metro_system`: 台北/高雄/桃園/台中捷運或高雄輕軌 |
| `/即時電子看板` | 查詢捷運車站即時電子看板 | `metro_system`: 台北捷運/高雄捷運/高雄輕軌 |

#### 資料來源選項
- `merged` (預設): 自動合併 TDX + 官方 XML 資料
- `tdx`: 僅 TDX 運輸資料流通服務平臺
- `highway_bureau` / `freeway`: 僅交通部官方 XML 資料

### AI 聊天類
| 指令 | 描述 | 參數 |
|------|------|------|
| `/聊天` | 與 AI 進行自然語言對話 | `message`: 要發送的訊息 |
| `/目前模型` | 查看當前使用的 AI 模型 | 無 |
| `/設定模型` | 設定 AI 模型 | `model`: 模型名稱 |
| `/清除對話` | 清除對話歷史 | 無 |

### 搜尋查詢類
| 指令 | 描述 | 參數 |
|------|------|------|
| `/搜尋` | 網路搜尋功能 | `query`: 搜尋關鍵字 |
| `/搜尋總結` | 搜尋結果總結 | `query`: 搜尋關鍵字 |
| `/搜尋設定` | 搜尋功能設定 | 各種設定參數 |

### 空氣品質類
| 指令 | 描述 | 參數 |
|------|------|------|
| `/空氣品質` | 查詢空氣品質 | `location`: 地區名稱 |
| `/縣市空氣品質` | 縣市空氣品質查詢 | `county`: 縣市名稱 |
| `/空氣品質測站` | 測站空氣品質 | `station`: 測站名稱 |

### 雷達氣象類
| 指令 | 描述 | 參數 |
|------|------|------|
| `/雷達圖` | 查詢氣象雷達圖 | 無 |
| `/大範圍雷達圖` | 大範圍雷達圖 | 無 |
| `/降雨雷達圖` | 降雨雷達圖 | 無 |
| `/溫度` | 溫度分布圖 | 無 |

### 管理類
| 指令 | 描述 | 權限要求 |
|------|------|----------|
| `/設定地震頻道` | 設定地震通知頻道 | 管理員權限 |
| `/清除啟動頻道` | 清除機器人啟動通知頻道 | 管理員權限 |
| `/設定啟動頻道` | 設定機器人啟動通知頻道 | 管理員權限 |
| `/狀態` | 查看機器人系統狀態 | 無 |
| `/延遲測試` | 測試機器人回應延遲 | 無 |

### 系統功能類
| 指令 | 描述 | 權限要求 |
|------|------|----------|
| `/等級` | 查看用戶等級 | 無 |
| `/排名` | 查看等級排名 | 無 |
| `/排行榜` | 顯示等級排行榜 | 無 |

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
   
   **重要**: 在 `.env` 檔案中設定必要的 API 密鑰：
   ```env
   # 必需的 API 密鑰
   DISCORD_TOKEN=您的機器人Token
   CWA_API_KEY=您的中央氣象署API密鑰
   TDX_CLIENT_ID=您的TDX客戶端ID
   TDX_CLIENT_SECRET=您的TDX客戶端密鑰
   
   # 可選的 API 密鑰
   AQI_API_KEY=您的環保署AQI_API密鑰
   GOOGLE_API_KEY=您的Google_API金鑰
   ```
   
   > 📝 **如何取得 Discord Bot Token**:
   > 1. 前往 [Discord Developer Portal](https://discord.com/developers/applications)
   > 2. 創建新應用程式 → Bot → 複製 Token
   > 3. 將 Token 填入 `.env` 檔案中
   
   > 🌦️ **如何取得 CWA API 密鑰**:
   > 1. 前往 [中央氣象署開放資料平臺](https://opendata.cwa.gov.tw/)
   > 2. 註冊帳號並登入
   > 3. 前往「會員中心」→「API金鑰管理」
   > 4. 申請新的 API 金鑰
   > 5. 將密鑰填入 `.env` 檔案中
   
   > 🚗 **如何取得 TDX API 憑證**:
   > 1. 前往 [TDX 運輸資料流通服務平臺](https://tdx.transportdata.tw/)
   > 2. 註冊帳號並登入
   > 3. 前往「應用程式管理」→ 創建新應用程式
   > 4. 取得 Client ID 和 Client Secret
   > 5. 將憑證填入 `.env` 檔案中
   
   **快速設定工具**: 執行 `python setup_all_apis.py` 來協助設定所有 API 密鑰

4. **啟動機器人**
   ```bash
   # 方法1: 直接啟動 (開發用)
   python bot.py
   
   # 方法2: 使用自動重啟腳本 (推薦)
   scripts\auto_restart_bot.bat
   
   # 方法3: 使用簡易啟動腳本
   start_bot_simple.bat
   ```
   
   > 💡 **推薦使用自動重啟腳本**: `scripts\auto_restart_bot.bat` 會自動監控機器人狀態，異常時自動重啟

## 🎯 功能使用範例

### 台鐵電子看板查詢
```
/台鐵電子看板 county:宜蘭縣                    # 查詢宜蘭縣所有車站 (已修正)
/台鐵電子看板 county:臺北市 station_name:台北    # 查詢台北車站即時看板
/台鐵誤點查詢                               # 查詢全台誤點列車
/台鐵誤點查詢 county:新北市                   # 查詢新北市誤點列車
/鐵路事故 鐵路類型:台鐵                       # 查詢台鐵事故資訊
/捷運狀態 metro_system:台北捷運                # 查詢台北捷運狀態
/即時電子看板 metro_system:台北捷運            # 查詢台北捷運電子看板
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

## 📊 系統狀態

### 🤖 當前機器人狀態
- **連線狀態**: ✅ 已連線到 Discord Gateway
- **運行伺服器數量**: 12 個 Discord 伺服器
- **載入模組**: 13 個 Cogs 模組 (100% 成功載入)
- **同步指令**: 60 個斜線指令 (已完全同步)
- **AI 模型**: Gemini 2.0 Flash Experimental
- **自動重啟**: ✅ 監控中 (每 5 分鐘檢查地震資料)

### 📋 已載入的功能模組
1. **AdminCommands** - 管理員指令
2. **BasicCommands** - 基本功能指令  
3. **InfoCommands** - 地震、天氣、交通資訊
4. **LevelSystem** - 用戶等級系統
5. **MonitorSystem** - 系統監控
6. **VoiceSystem** - 語音系統
7. **ChatCommands** - AI 聊天功能
8. **SearchCommands** - 搜尋功能
9. **WeatherCommands** - 天氣查詢
10. **AirQualityCommands** - 空氣品質
11. **RadarCommands** - 雷達圖查詢
12. **TemperatureCommands** - 溫度查詢
13. **ReservoirCommands** - 水庫資訊

### 🔄 API 監控狀態
- **中央氣象署 API**: ✅ 正常 (每 5 分鐘自動更新地震資料)
- **TDX 運輸 API**: ✅ 正常
- **Google Gemini API**: ✅ 正常 (AI 聊天功能已啟用)
- **SSL 連線**: ✅ 已設定自訂 SSL 上下文

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

## 🛠️ 開發功能

### ✅ 已實現功能
- ✅ 地震監控和通知系統
- ✅ 天氣預報查詢
- ✅ 氣象站觀測資料查詢
- ✅ 翻頁瀏覽功能
- ✅ 海嘯警報查詢
- ✅ **國道監視器雙來源整合** (升級版)
- ✅ 水庫水情查詢
- ✅ 自動重新整理
- ✅ 用戶權限控制
- ✅ 錯誤處理和重試機制

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

**最後更新**: 2025年8月2日  
**版本**: v6.1  
**維護狀態**: 🟢 積極維護  
**功能狀態**: ✅ 所有核心功能正常運作  
**機器人狀態**: 🤖 已連線並在 12 個伺服器中運行  
**系統整合**: ✅ 13 個 Cogs 模組完全載入 (60 個斜線指令)  
**最新修正**: 🔧 批次檔虛擬環境啟動問題已解決 (錯誤代碼 9009)  
**AI 整合**: 🤖 Gemini 2.0 Flash AI 聊天系統已啟用  
**啟動系統**: � 自動重啟監控系統正常運作  
**文檔狀態**: 📚 完整更新 (包含批次檔修復指南、故障排除、開發指南)
