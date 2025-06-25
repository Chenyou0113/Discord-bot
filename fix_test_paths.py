#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復測試檔案中的 import 路徑
將所有測試檔案的路徑參考修正為正確的相對路徑
"""

import os
import re

def fix_import_paths():
    """修復所有測試檔案中的 import 路徑"""
    tests_dir = r"c:\Users\xiaoy\Desktop\Discord bot\tests"
    
    # 需要修復的檔案列表
    test_files = [
        "test_bot_loading.py",
        "simple_function_test.py", 
        "test_weather_station_pagination.py",
        "final_verification.py",
        "quick_weather_test.py",
        "simple_cwa_test.py"
    ]
    
    for filename in test_files:
        filepath = os.path.join(tests_dir, filename)
        if os.path.exists(filepath):
            print(f"修復 {filename}...")
            fix_single_file(filepath)
        else:
            print(f"找不到檔案: {filename}")

def fix_single_file(filepath):
    """修復單一檔案的路徑"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修復路徑設定部分
        old_path_setup = """# 添加專案根目錄到 sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)"""
        
        new_path_setup = """# 添加專案根目錄到 sys.path (從 tests 目錄往上一層)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)"""
        
        # 替換路徑設定
        if old_path_setup in content:
            content = content.replace(old_path_setup, new_path_setup)
            print(f"  ✅ 修復了路徑設定")
        
        # 寫回檔案
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"  ✅ {os.path.basename(filepath)} 修復完成")
        
    except Exception as e:
        print(f"  ❌ 修復 {os.path.basename(filepath)} 時發生錯誤: {str(e)}")

if __name__ == "__main__":
    print("🔧 開始修復測試檔案路徑...")
    print("=" * 50)
    fix_import_paths()
    print("=" * 50)
    print("✨ 路徑修復完成！")
