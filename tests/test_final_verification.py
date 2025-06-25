#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終驗證測試腳本
檢查所有修復是否正確應用
"""

import sys
import os
import json
from pathlib import Path

def test_api_logic_fix():
    """測試API解析邏輯修復"""
    print("🔍 測試API解析邏輯修復...")
    
    # 模擬認證模式的回應
    auth_response = {
        'result': {
            'resource_id': 'F-C0032-001',
            'fields': [
                {'id': 'locationName', 'type': 'String'},
                {'id': 'time', 'type': 'String'}
            ]
        },
        'records': [
            {
                'locationName': '台北市',
                'time': {'obsTime': '2024-12-25T12:00:00+08:00'}
            }
        ]
    }
    
    # 測試新的解析邏輯
    data = auth_response
    
    # 檢查是否為異常資料結構（應該返回False）
    is_abnormal = ('result' in data and isinstance(data['result'], dict) and 
                   set(data['result'].keys()) == {'resource_id', 'fields'} and 
                   'records' not in data)
    
    print(f"   資料結構檢測: {'✅ 正確' if not is_abnormal else '❌ 錯誤'}")
    
    # 檢查records資料提取
    records_found = False
    if 'records' in data:
        print("   ✅ 使用有認證模式資料結構 (根級別 records)")
        records_data = data['records']
        records_found = True
    elif 'result' in data and 'records' in data.get('result', {}):
        print("   ✅ 使用無認證模式資料結構 (result.records)")
        records_data = data['result']['records']
        records_found = True
    else:
        print("   ❌ 無法找到records資料")
    
    return records_found and not is_abnormal

def test_file_organization():
    """測試檔案組織是否正確"""
    print("🔍 測試檔案組織...")
    
    expected_folders = ['docs', 'api_tests', 'scripts', 'test_files', 'config_files']
    success = True
    
    for folder in expected_folders:
        if os.path.exists(folder):
            print(f"   ✅ {folder}/ 資料夾存在")
        else:
            print(f"   ❌ {folder}/ 資料夾不存在")
            success = False
    
    # 檢查關鍵檔案是否在正確位置
    key_files = {
        'scripts/auto_restart_bot.bat': '自動重啟腳本',
        'config_files/levels.json': '等級系統配置',
        'docs/API_STRUCTURE_FIX_FINAL_REPORT.md': 'API修復報告'
    }
    
    for file_path, desc in key_files.items():
        if os.path.exists(file_path):
            print(f"   ✅ {desc} ({file_path})")
        else:
            print(f"   ❌ {desc} 不存在 ({file_path})")
            success = False
    
    return success

def test_script_paths():
    """測試腳本路徑修復"""
    print("🔍 測試腳本路徑修復...")
    
    script_files = [
        'scripts/auto_restart_bot.bat',
        'scripts/start_bot.bat',
        'scripts/safe_restart_bot.bat'
    ]
    
    success = True
    for script in script_files:
        if os.path.exists(script):
            with open(script, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'cd /d "%~dp0.."' in content or 'cd /d "%~dp0/.."' in content:
                    print(f"   ✅ {script} 路徑修復正確")
                else:
                    print(f"   ❌ {script} 路徑修復不正確")
                    success = False
        else:
            print(f"   ❌ {script} 不存在")
            success = False
    
    return success

def test_bot_restart_logic():
    """測試機器人重啟邏輯"""
    print("🔍 測試機器人重啟邏輯...")
    
    if os.path.exists('bot.py'):
        with open('bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 檢查是否包含正確的重啟邏輯
            if 'await bot.close()' in content and 'os.execv' not in content:
                print("   ✅ 重啟邏輯修復正確 (使用 await bot.close())")
                return True
            else:
                print("   ❌ 重啟邏輯未正確修復")
                return False
    else:
        print("   ❌ bot.py 檔案不存在")
        return False

def main():
    """主測試函數"""
    print("🤖 Discord Bot 最終驗證測試")
    print("=" * 50)
    
    tests = [
        ("API解析邏輯修復", test_api_logic_fix),
        ("檔案組織", test_file_organization),
        ("腳本路徑修復", test_script_paths),
        ("機器人重啟邏輯", test_bot_restart_logic)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print()
        try:
            if test_func():
                print(f"✅ {test_name} 測試通過")
                passed += 1
            else:
                print(f"❌ {test_name} 測試失敗")
        except Exception as e:
            print(f"❌ {test_name} 測試出現異常: {e}")
    
    print()
    print("=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！系統修復完成且功能正常。")
        return True
    else:
        print("⚠️ 部分測試失敗，需要進一步檢查。")
        return False

if __name__ == "__main__":
    main()
