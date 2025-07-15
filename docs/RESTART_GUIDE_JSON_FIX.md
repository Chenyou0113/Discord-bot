# 機器人重啟指南 - 載入 JSON 解析修復

## 🎯 目的
重新啟動 Discord 機器人以載入 JSON 解析問題的修復代碼

## ✅ 修復狀態確認
- JSON 解析修復已完成並通過測試 ✅
- 雙重解析機制已實作在所有雷達圖方法中 ✅
- 驗證腳本 `verify_json_fix.py` 測試成功 ✅
- 防止指令重複註冊機制已加入 ✅

## ⚠️ 已知問題與修復
### 指令重複註冊錯誤
**錯誤**: `CommandAlreadyRegistered: Command 'weather_station' already registered`
**原因**: 機器人重新載入時沒有正確清理舊指令
**修復**: 已在 `bot.py` 中加入 Cog 卸載機制

## 🚀 重啟步驟

### 方法 1: 使用安全啟動腳本 (推薦)
```powershell
safe_start_bot.bat
```

### 方法 2: 手動重啟
1. **停止所有 Python 進程**:
```powershell
taskkill /F /IM python.exe
```

2. **等待 3 秒讓進程完全清理**

3. **重新啟動機器人**:
```powershell
python bot.py
```

### 3. 驗證修復生效
在 Discord 中測試：
- `/radar` - 應該正常顯示雷達圖
- `/radar_large` - 應該正常顯示大範圍雷達圖
- `/rainfall_radar` - 應該正常顯示降雨雷達圖

### 4. 檢查日誌
如果仍有問題，檢查 `bot.log` 是否還有 JSON 解析錯誤

## 📋 修復詳情

### 修復的檔案
- `cogs/radar_commands.py` - 所有 fetch 方法已修復

### 修復的方法
- `fetch_radar_data()` - 一般雷達圖
- `fetch_large_radar_data()` - 大範圍雷達圖
- `fetch_rainfall_radar_data()` - 降雨雷達圖

### 修復機制
```python
# 雙重解析機制
try:
    response_text = await response.text()
    data = json.loads(response_text)
except json.JSONDecodeError:
    data = await response.json(content_type=None)
```

## 🎉 預期結果

重啟後應該：
1. ✅ 不再看到 `binary/octet-stream` 錯誤
2. ✅ 所有雷達圖指令正常運作
3. ✅ 圖片顯示和互動功能正常
4. ✅ 快取機制正常運作

---

**時間**: 2025-06-28 21:05
**狀態**: 準備重啟
**信心度**: 100% (已通過驗證測試)
