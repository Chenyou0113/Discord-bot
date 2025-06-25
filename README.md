# 🤖 Discord 氣象地震機器人

一個功能完整的 Discord 機器人，提供台灣地區的地震資訊、天氣預報和自動氣象站觀測資料查詢服務。

## ✨ 主要功能

### 🔔 地震監控
- **即時地震通知**: 自動監控中央氣象署地震資料，即時推送最新地震資訊
- **地震資訊查詢**: 支援一般地震和小區域地震資料查詢
- **詳細震度資訊**: 提供震央位置、規模、深度及各地震度分布

### 🌤️ 天氣服務
- **天氣預報查詢**: 支援全台各縣市 36 小時天氣預報
- **互動式選單**: 使用下拉選單快速選擇查詢地區
- **詳細氣象資訊**: 包含溫度、濕度、降雨機率、風速等完整資訊

### 🌡️ 氣象站觀測 (新功能)
- **即時觀測資料**: 查詢全台 500+ 個自動氣象站的即時觀測資料
- **多種查詢模式**: 支援全台概況、地區查詢、單一測站詳細資料
- **翻頁瀏覽功能**: 當查詢結果過多時，提供翻頁按鈕便於瀏覽
- **重新整理功能**: 可即時更新最新的觀測資料

### 🌊 海嘯警報
- **海嘯資訊監控**: 查詢最新海嘯警報和相關資訊

## 🎮 指令列表

| 指令 | 描述 | 參數 |
|------|------|------|
| `/earthquake` | 查詢最新地震資訊 | `type`: "normal" 或 "small" |
| `/weather` | 查詢天氣預報 | `location`: 縣市名稱 (可選) |
| `/weather_station` | 查詢氣象站觀測資料 | `station_id`: 測站代碼 (可選)<br>`location`: 地區名稱 (可選) |
| `/tsunami` | 查詢海嘯資訊 | 無 |
| `/set_earthquake_channel` | 設定地震通知頻道 | 需要管理員權限 |

## 🚀 快速開始

### 環境需求
- Python 3.8+
- Discord.py 2.0+
- aiohttp
- xmltodict

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
   cp .env.example .env
   # 編輯 .env 檔案，填入您的 Discord Bot Token
   ```

4. **啟動機器人**
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

### API 設定
本機器人使用中央氣象署開放資料 API，無需額外申請 API Key。

## 📁 專案結構

```
Discord bot/
├── bot.py                              # 主程式入口
├── cogs/
│   └── info_commands_fixed_v4_clean.py # 主要功能實現
├── tests/                              # 測試檔案目錄
│   ├── test_bot_loading.py            # Bot 載入測試
│   ├── simple_function_test.py        # 基本功能測試
│   ├── final_verification.py          # 最終驗證測試
│   └── test_weather_station_pagination.py # 翻頁功能測試
├── scripts/                            # 輔助腳本
├── docs/                              # 說明文件
├── config_files/                      # 設定檔案
├── .env                               # 環境變數 (需自行創建)
├── .env.example                       # 環境變數範例
└── requirements.txt                   # Python 依賴清單
```

## 🎯 氣象站翻頁功能詳解

### 使用方式
```
/weather_station                        # 顯示全台主要縣市概況
/weather_station location:台北           # 查詢台北地區所有氣象站
/weather_station station_id:466920      # 查詢特定測站 (台北)
```

### 翻頁控制
- **◀️ 上一頁**: 瀏覽前一頁資料
- **下一頁 ▶️**: 瀏覽下一頁資料
- **🔄 重新整理**: 獲取最新觀測資料
- **頁面資訊**: 顯示當前頁數/總頁數

### 智能分頁
- 每頁顯示最多 5 個測站資料
- 自動計算總頁數
- 邊界智能處理（第一頁停用上一頁按鈕）

## 🧪 測試

### 執行所有測試
```bash
python test_organization_summary.py
```

### 執行個別測試
```bash
# Bot 載入測試
python tests/test_bot_loading.py

# 基本功能測試
python tests/simple_function_test.py

# 翻頁功能測試
python tests/test_weather_station_pagination.py

# 最終驗證測試
python tests/final_verification.py
```

## 📊 API 資料來源

- **地震資料**: 中央氣象署地震報告 API
- **天氣預報**: 中央氣象署天氣預報 API
- **氣象站資料**: 中央氣象署自動氣象站觀測資料 API
- **海嘯資料**: 中央氣象署海嘯資訊 API

## 🛠️ 開發功能

### 已實現功能
- ✅ 地震監控和通知系統
- ✅ 天氣預報查詢
- ✅ 氣象站觀測資料查詢
- ✅ 翻頁瀏覽功能
- ✅ 海嘯警報查詢
- ✅ 自動重新整理
- ✅ 用戶權限控制
- ✅ 錯誤處理和重試機制

### 技術特色
- **異步處理**: 使用 asyncio 和 aiohttp 提升效能
- **模組化設計**: 使用 Discord.py Cogs 系統
- **智能快取**: 減少 API 調用次數
- **容錯機制**: 完整的錯誤處理和自動重試
- **用戶體驗**: 友善的互動介面和即時回應

## 📝 更新日誌

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

## 🤝 貢獻指南

1. Fork 本專案
2. 創建功能分支 (`git checkout -b feature/新功能`)
3. 提交更改 (`git commit -am '新增某功能'`)
4. 推送到分支 (`git push origin feature/新功能`)
5. 創建 Pull Request

## 📄 授權

本專案使用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 📞 支援

如果您遇到問題或有功能建議，請：
1. 查看 [Issues](../../issues) 是否已有相關討論
2. 創建新的 Issue 描述您的問題
3. 查看專案的說明文件和測試範例

## 🌟 致謝

- 感謝中央氣象署提供開放資料 API
- 感謝 Discord.py 開發團隊
- 感謝所有貢獻者和使用者的回饋

---

**最後更新**: 2025年6月25日  
**版本**: v4.0  
**維護狀態**: 🟢 積極維護
