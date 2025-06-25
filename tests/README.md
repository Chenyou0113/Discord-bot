# 測試檔案目錄

此目錄包含 Discord Bot 的所有測試檔案（共 48 個），按功能分類如下：

## 📊 統計資訊
- **總檔案數**: 48 個 Python 測試檔案
- **最後整理**: 2025年6月25日
- **狀態**: ✅ 完成統一管理

## 📁 檔案分類

### 🔧 核心測試
- `test_bot_loading.py` - Bot 載入測試
- `simple_function_test.py` - 基本功能測試
- `final_verification.py` - 最終驗證測試
- `comprehensive_test.py` - 綜合測試

### 🌡️ 氣象站功能測試
- `test_weather_station_pagination.py` - 翻頁功能測試
- `test_weather_station.py` - 氣象站功能測試
- `quick_weather_test.py` - 快速氣象測試
- `simple_cwa_test.py` - 簡單 CWA API 測試
- `check_weather_api.py` - 氣象 API 健康檢查

### 🌍 地震功能測試
- `final_earthquake_test.py` - 最終地震測試
- `test_earthquake_command_fix.py` - 地震指令修復測試
- `test_earthquake_format_fix.py` - 地震格式修復測試
- `test_simple_format.py` - 簡單格式化測試
- `test_complete_bot_api_fix.py` - 完整 API 修復測試
- `test_final_earthquake_complete.py` - 地震功能完整測試

### 🔗 API 測試
- `test_cwa_api.py` - 中央氣象署 API 測試
- `test_api_fix.py` - API 修復測試
- `test_api_fix_verification.py` - API 修復驗證
- `test_api_logic_fix.py` - API 邏輯修復測試
- `test_complete_api_fix.py` - 完整 API 修復測試
- `test_fixed_api.py` - 已修復 API 測試
- `test_no_auth_api.py` - 無認證 API 測試
- `test_simple_api_fix.py` - 簡單 API 修復測試

### 🔍 搜尋功能測試
- `test_search_function.py` - 搜尋功能測試
- `test_search_integration.py` - 搜尋整合測試
- `test_auto_search.py` - 自動搜尋測試

### 📝 格式化與資料處理測試
- `test_format_direct.py` - 直接格式化測試
- `test_format_function.py` - 格式化函數測試
- `test_format_standalone.py` - 獨立格式化測試

### 🚀 啟動與載入測試
- `test_bot_startup.py` - Bot 啟動測試
- `test_bot_startup_simple.py` - 簡單啟動測試
- `test_setup.py` - 設定測試

### ✅ 驗證腳本
- `verify_api_fix_final.py` - API 修復最終驗證
- `verify_auto_search.py` - 自動搜尋驗證
- `verify_fix.py` - 修復驗證
- `verify_gemini_fix.py` - Gemini 修復驗證
- `verify_info_commands_fixed_v2.py` - 資訊指令修復驗證 v2
- `verify_search_setup.py` - 搜尋設定驗證

### 🛠️ 其他測試與工具
- `test_complete_flow.py` - 完整流程測試
- `test_enhance_problem.py` - 問題增強測試
- `test_organization_summary.py` - 組織摘要測試
- `final_complete_test.py` - 最終完整測試
- `final_complete_verification.py` - 最終完整驗證
- `final_earthquake_fix_verification.py` - 地震修復最終驗證
- `final_fix_verification.py` - 修復最終驗證
- `quick_check.py` - 快速檢查
- `FINAL_API_FIX_REPORT.py` - 最終 API 修復報告

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
