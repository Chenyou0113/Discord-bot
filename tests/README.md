# 測試檔案目錄

此目錄包含 Discord Bot 的所有測試檔案，按功能分類如下：

## 📁 檔案分類

### 核心測試
- `test_bot_loading.py` - Bot 載入測試
- `simple_function_test.py` - 基本功能測試
- `final_verification.py` - 最終驗證測試

### 氣象站功能測試
- `test_weather_station_pagination.py` - 翻頁功能測試
- `test_weather_station.py` - 氣象站功能測試
- `quick_weather_test.py` - 快速氣象測試
- `simple_cwa_test.py` - 簡單 CWA API 測試

### 地震功能測試
- `test_simple_format.py` - 格式化測試
- `test_complete_bot_api_fix.py` - 完整 API 修復測試
- `final_earthquake_test.py` - 最終地震測試
- `test_earthquake_*.py` - 各種地震功能測試

### API 測試
- `test_*_api*.py` - 各種 API 相關測試
- `check_weather_api.py` - 氣象 API 檢查

### 驗證腳本
- `verify_*.py` - 各種功能驗證腳本

## 🚀 使用方式

在 Discord bot 根目錄執行：
```bash
# 基本功能測試
python tests/simple_function_test.py

# Bot 載入測試
python tests/test_bot_loading.py

# 最終驗證
python tests/final_verification.py

# 翻頁功能測試
python tests/test_weather_station_pagination.py
```

---
整理時間: 2025年6月24日
