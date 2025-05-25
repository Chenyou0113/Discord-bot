# Discord AI 助手機器人

這是一個整合了 Google Gemini AI 的 Discord 機器人，提供智慧對話和多種實用功能。

## 功能特點

- 🤖 AI 智慧對話（使用 Google Gemini）
- 🌋 地震資訊查詢和自動通報
- 🌤️ 天氣預報和警報通知
- 💧 水庫水情查詢
- 🏆 用戶等級系統
- 🔍 伺服器監控功能
- 🛠️ 管理員指令集

## 目錄結構
- `bot.py`: 主程式檔案
- `cogs/`: 各功能模組
  - `info_commands_fixed_v4.py`: 資訊指令模組 (地震、天氣、水情等)
  - `admin_commands_fixed.py`: 管理員指令模組
  - `chat_commands.py`: AI 聊天功能模組
  - `basic_commands.py`: 基本指令模組
  - `level_system.py`: 用戶等級系統模組
  - `monitor_system.py`: 系統監控模組
  - `voice_system.py`: 語音功能模組
- `start_bot.bat`: 啟動腳本
- `stop_bot.bat`: 停止腳本
- `archive/`: 舊版本腳本備份
- `tests/`: 測試檔案

## 安裝步驟

1. 確保已安裝 Python 3.9 或更新版本
2. 安裝所需套件：
   ```bash
   pip install -r requirements.txt
   ```
3. 在專案根目錄建立 `.env` 檔案並設定：
   ```
   DISCORD_TOKEN=你的Discord機器人Token
   GOOGLE_API_KEY=你的Google API金鑰
   ```
4. 執行 `start_bot.bat` 啟動機器人

## 使用說明

斜線指令：
- `/chat [訊息]` - 與 AI 對話
- `/weather` - 查詢天氣預報
- `/earthquake` - 查詢最新地震資訊
- `/earthquake_small` - 查詢小區域地震資訊
- `/reservoir` - 查詢水庫水情
- `/water_info` - 查詢水情資訊
- `/clear_chat` - 清除對話歷史

管理員指令：
- `!reboot` 或 `!rb` - 重啟機器人
- `!resync` 或 `!rs` - 同步斜線指令
- `!fix_commands` 或 `!fc` - 修復「未知整合」問題

## 注意事項
- 此機器人需要 Discord Bot 的 "Message Content Intent" 權限
- 請確保 Google API 金鑰有權限使用 Gemini 模型
- 最新版本的機器人支援 2025 年的地震資料格式

實用工具：
- `!roll [數字]` - 擲骰子
- `!random [選項1] [選項2]...` - 隨機選擇
- `!time` - 顯示現在時間
- `!clean [數量]` - 清理訊息

## 注意事項

- 請確保機器人擁有適當的權限
- 定期更新 API 金鑰
- 不要分享或上傳 .env 檔案

## 授權條款

MIT License
