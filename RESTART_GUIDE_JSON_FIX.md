# 機器人重啟指南 - 載入 JSON 解析修復

## 🎯 目的
重新啟動 Discord 機器人以載入 JSON 解析問題的修復代碼

## ✅ 修復狀態確認
- JSON 解析修復已完成並通過測試 ✅
- 雙重解析機制已實作在所有雷達圖方法中 ✅
- 驗證腳本 `verify_json_fix.py` 測試成功 ✅

## 🚀 重啟步驟

### 1. 確認舊進程已停止
```powershell
tasklist | findstr python
# 應該沒有或很少 python.exe 進程
```

### 2. 重新啟動機器人
```powershell
python bot.py
```

或使用批次檔：
```powershell
start_weather_bot.bat
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
