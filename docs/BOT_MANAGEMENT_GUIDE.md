# Discord Bot 安全啟動與管理指南

## 🎯 問題解決

### ❌ 問題：使用重啟指令時機器人關機
**原因：** 重啟腳本使用了 `taskkill /f /im python.exe`，這會強制關閉所有 Python 進程
**解決方案：** 使用新的自動重啟腳本 `auto_restart_bot.bat` 或 `auto_restart_bot.ps1`

### ✅ 新功能：Discord 重啟指令支援
現在可以在 Discord 中使用以下指令安全重啟機器人：
- `!reboot` 或 `!rb` - 基本重啟指令
- `/restart` - 管理員專用斜線指令
- `/emergency_restart` - 緊急重啟指令

**重要：** 需要配合自動重啟腳本使用才能實現真正的重啟

## 🚀 推薦的啟動方法

### 方法 1：使用自動重啟腳本 (最新推薦)
```bat
auto_restart_bot.bat
```
或 PowerShell 版本：
```powershell
.\auto_restart_bot.ps1
```
**特色：** 自動監控並重啟機器人，支援 Discord 重啟指令

### 方法 2：使用專用啟動腳本
```bat
start_bot_with_auto_search.bat
```
或 PowerShell 版本：
```powershell
.\start_bot_with_auto_search.ps1
```

### 方法 3：手動啟動
```bash
cd "c:\Users\xiaoy\Desktop\Discord bot"
python bot.py
```

### 方法 4：使用安全重啟腳本
```bat
safe_restart_bot.bat
```
或 PowerShell 版本：
```powershell
.\safe_restart_bot.ps1
```

## 🛡️ 安全啟動腳本特色

### ✅ 安全特性
- **不會強制終止進程** - 避免意外關閉其他程式
- **環境檢查** - 自動檢查必要文件和環境變數
- **虛擬環境支援** - 自動啟用虛擬環境（如果存在）
- **錯誤處理** - 提供詳細的錯誤說明和解決建議

### ✅ 用戶友好特性
- **清晰的狀態指示** - 使用表情符號和顏色標示
- **使用說明** - 顯示自動搜尋功能的使用方法
- **控制提示** - 說明如何安全停止 Bot

## 📋 啟動步驟

### 1. 選擇啟動方法
- **新用戶推薦：** `start_bot_with_auto_search.bat`
- **進階用戶：** `start_bot_with_auto_search.ps1`
- **需要重啟：** `safe_restart_bot.ps1 -Force`

### 2. 執行腳本
雙擊腳本文件或在 PowerShell 中執行

### 3. 確認啟動
等待看到以下訊息：
```
🚀 正在啟動 Discord Bot...
```

### 4. 啟用自動搜尋功能
在 Discord 中使用管理員帳號輸入：
```
/auto_search enable:True
```

## 🛑 如何安全停止 Bot

### 方法 1：使用 Ctrl+C (推薦)
在 Bot 執行的命令列視窗中按 `Ctrl+C`

### 方法 2：關閉命令列視窗
直接關閉執行 Bot 的命令列視窗

### 方法 3：使用 Discord 指令 (如果已實現)
```
/shutdown
```

## ⚠️ 避免的操作

### ❌ 不要使用的方法
- **任務管理員強制結束** - 可能導致資料遺失
- **`taskkill /f /im python.exe`** - 會關閉所有 Python 程式
- **強制重啟電腦** - 可能損壞文件

## 🔧 故障排除

### 問題：Bot 無法啟動
**檢查清單：**
1. ✅ Discord Token 是否正確
2. ✅ .env 文件是否存在
3. ✅ 網路連線是否正常
4. ✅ Python 環境是否正確

### 問題：自動搜尋不工作
**檢查清單：**
1. ✅ 管理員是否啟用了功能：`/auto_search enable:True`
2. ✅ 用戶是否使用了正確的觸發詞：「搜尋」、「搜索」、「查找」
3. ✅ 用戶是否達到冷卻時間或每日限制
4. ✅ Bot 是否有足夠的權限

### 問題：Bot 頻繁斷線
**可能原因：**
- Token 過期
- 網路不穩定
- API 配額超限
- 程式碼錯誤

## 📊 腳本比較

| 腳本名稱 | 類型 | 安全性 | 功能 | 自動重啟 | 推薦度 |
|---------|------|--------|------|---------|--------|
| `auto_restart_bot.bat` | 批次檔 | 高 | 自動重啟監控 | ✅ | ⭐⭐⭐⭐⭐ |
| `auto_restart_bot.ps1` | PowerShell | 高 | 進階重啟監控 | ✅ | ⭐⭐⭐⭐⭐ |
| `start_bot_with_auto_search.bat` | 批次檔 | 高 | 基本啟動 | ❌ | ⭐⭐⭐⭐ |
| `start_bot_with_auto_search.ps1` | PowerShell | 高 | 進階功能 | ❌ | ⭐⭐⭐⭐ |
| `safe_restart_bot.ps1` | PowerShell | 高 | 重啟功能 | ❌ | ⭐⭐⭐ |
| `restart_with_auto_search.bat` | 批次檔 | 中 | 簡單重啟 | ❌ | ⭐⭐ |

## 🎯 最佳實踐

### 📝 建議
1. **使用專用啟動腳本** - 不要手動管理進程
2. **定期檢查日誌** - 監控 Bot 運行狀態
3. **備份設定文件** - 定期備份 .env 和其他配置
4. **測試環境** - 在本地測試後再部署

### 🔐 安全建議
1. **保護 Token** - 不要在公開場所分享
2. **限制權限** - 只給 Bot 必要的權限
3. **監控使用** - 定期檢查 API 使用情況
4. **更新依賴** - 保持套件版本最新

## 📞 支援

如果遇到問題：
1. 查看此指南的故障排除部分
2. 檢查 Bot 日誌檔案
3. 使用驗證腳本：`verify_auto_search.py`
4. 聯繫開發者或管理員

---

**🎊 現在您可以安全地啟動和管理您的 Discord Bot 了！**
