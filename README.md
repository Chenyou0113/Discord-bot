# Discord AI 助手機器人

這是一個整合了 Google Gemini AI 的 Discord 機器人，提供智慧對話和實用功能。

## 功能特點

- 🤖 AI 智慧對話（使用 Google Gemini）
- 💬 自然語言處理
- 🎲 娛樂功能（擲骰子、隨機選擇）
- ⚡ 實用工具（清理訊息、顯示時間）
- 🔔 回應提及（Mention）
- 📝 自動回覆常見問候

## 安裝步驟

1. 確保已安裝 Python 3.8 或更新版本
2. 安裝所需套件：
   ```bash
   pip install -r requirements.txt
   ```
3. 在專案根目錄建立 `.env` 檔案並設定：
   ```
   DISCORD_TOKEN=你的Discord機器人Token
   GOOGLE_API_KEY=你的Google API金鑰
   ```

## 使用說明

基本指令：
- `!hello` - 打招呼
- `!ping` - 檢查延遲
- `!chat [訊息]` - 與 AI 對話
- `!ai [問題]` - 詢問 AI
- `!commands` - 顯示所有指令

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
