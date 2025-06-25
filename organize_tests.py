#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試檔案整理腳本
將散落在各處的測試檔案移動到 tests 資料夾中
"""

import os
import shutil
from pathlib import Path

def organize_test_files():
    """整理測試檔案"""
    base_dir = Path("c:/Users/xiaoy/Desktop/Discord bot")
    tests_dir = base_dir / "tests"
    
    # 確保 tests 目錄存在
    tests_dir.mkdir(exist_ok=True)
    
    # 需要移動的測試檔案列表（在根目錄的）
    test_files_to_move = [
        # 核心測試檔案
        "test_bot_loading.py",
        "simple_function_test.py", 
        "final_verification.py",
        "test_weather_station_pagination.py",
        
        # 氣象站相關測試
        "test_weather_station.py",
        "quick_weather_test.py",
        "simple_cwa_test.py",
        
        # 地震功能測試
        "test_simple_format.py",
        "test_complete_bot_api_fix.py",
        "final_earthquake_test.py",
        "test_earthquake_command_fix.py",
        "test_earthquake_format_fix.py",
        "test_final_earthquake_complete.py",
        
        # API 測試
        "test_api_fix.py",
        "test_api_fix_verification.py",
        "test_api_logic_fix.py",
        "test_complete_api_fix.py",
        "test_fixed_api.py",
        "test_no_auth_api.py",
        "test_simple_api_fix.py",
        "check_weather_api.py",
        "test_cwa_api.py",
        
        # 格式化測試
        "test_format_direct.py",
        "test_format_function.py", 
        "test_format_standalone.py",
        
        # 搜尋功能測試
        "test_auto_search.py",
        "test_search_function.py",
        "test_search_integration.py",
        
        # 驗證腳本
        "verify_api_fix_final.py",
        "verify_auto_search.py", 
        "verify_fix.py",
        "verify_gemini_fix.py",
        "verify_search_setup.py",
        
        # 其他測試
        "test_bot_startup.py",
        "test_bot_startup_simple.py",
        "test_complete_flow.py",
        "test_enhance_problem.py",
        "test_setup.py",
        "comprehensive_test.py",
        "final_complete_test.py",
        "final_complete_verification.py",
        "final_earthquake_fix_verification.py",
        "quick_check.py"
    ]
    
    moved_files = []
    not_found_files = []
    
    print("🗂️  開始整理測試檔案...")
    print("=" * 50)
    
    for filename in test_files_to_move:
        source_path = base_dir / filename
        if source_path.exists():
            target_path = tests_dir / filename
            try:
                shutil.move(str(source_path), str(target_path))
                moved_files.append(filename)
                print(f"✅ 移動: {filename}")
            except Exception as e:
                print(f"❌ 移動失敗: {filename} - {str(e)}")
        else:
            not_found_files.append(filename)
    
    print(f"\n📊 移動統計:")
    print(f"  成功移動: {len(moved_files)} 個檔案")
    print(f"  未找到: {len(not_found_files)} 個檔案")
    
    if not_found_files:
        print(f"\n📝 未找到的檔案:")
        for filename in not_found_files:
            print(f"  - {filename}")
    
    # 建立 tests 目錄的 README
    readme_content = """# 測試檔案目錄

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
"""
    
    readme_path = tests_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"\n📄 已建立 {readme_path}")
    print("\n✨ 測試檔案整理完成！")
    
    return len(moved_files)

if __name__ == "__main__":
    moved_count = organize_test_files()
    print(f"\n🎉 成功整理了 {moved_count} 個測試檔案！")
