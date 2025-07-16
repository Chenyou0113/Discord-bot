#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Bot 測試啟動器
提供快速存取各種測試功能的介面
"""

import os
import sys
import subprocess
from pathlib import Path

def show_menu():
    """顯示測試選單"""
    print("🤖 Discord Bot 測試選單")
    print("=" * 50)
    print("基本測試:")
    print("  1. Bot 載入測試")
    print("  2. 基本功能測試") 
    print("  3. 最終驗證測試")
    print()
    print("功能專項測試:")
    print("  4. 翻頁功能測試")
    print("  5. 氣象站功能測試")
    print("  6. 地震功能測試")
    print("  7. API 連線測試")
    print()
    print("快速測試:")
    print("  8. 快速氣象測試")
    print("  9. 快速檢查")
    print()
    print("其他:")
    print("  0. 退出")
    print("=" * 50)

def run_test(test_file):
    """執行指定的測試檔案"""
    tests_dir = Path("tests")
    test_path = tests_dir / test_file
    
    if not test_path.exists():
        print(f"❌ 找不到測試檔案: {test_file}")
        return False
    
    print(f"🚀 執行測試: {test_file}")
    print("-" * 30)
    
    try:
        # 執行測試檔案
        result = subprocess.run(
            [sys.executable, str(test_path)],
            cwd=Path.cwd(),
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n✅ 測試完成: {test_file}")
        else:
            print(f"\n❌ 測試失敗: {test_file}")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 執行測試時發生錯誤: {str(e)}")
        return False

def main():
    """主程式"""
    # 檢查 tests 目錄是否存在
    if not Path("tests").exists():
        print("❌ 找不到 tests 目錄，請先執行 organize_tests.py")
        return
    
    test_mapping = {
        "1": "test_bot_loading.py",
        "2": "simple_function_test.py", 
        "3": "final_verification.py",
        "4": "test_weather_station_pagination.py",
        "5": "test_weather_station.py",
        "6": "final_earthquake_test.py",
        "7": "check_weather_api.py",
        "8": "quick_weather_test.py",
        "9": "quick_check.py"
    }
    
    while True:
        show_menu()
        choice = input("請選擇測試項目 (0-9): ").strip()
        
        if choice == "0":
            print("👋 再見！")
            break
        elif choice in test_mapping:
            print()
            success = run_test(test_mapping[choice])
            
            # 等待用戶按鍵
            input("\n按 Enter 鍵繼續...")
            print("\n" * 2)  # 清空一些空間
        else:
            print("❌ 無效的選擇，請輸入 0-9")
            input("按 Enter 鍵繼續...")
            print("\n" * 2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 測試已中斷，再見！")
