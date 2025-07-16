#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的測試啟動器
快速執行主要測試
"""

import os
import sys
import subprocess

def main():
    """執行主要測試"""
    print("🧪 Discord Bot 測試執行器")
    print("=" * 50)
    
    # 主要測試檔案列表
    main_tests = [
        ("Bot 載入測試", "test_bot_loading.py"),
        ("基本功能測試", "simple_function_test.py"),
        ("最終驗證測試", "final_verification.py"),
        ("氣象站翻頁測試", "test_weather_station_pagination.py")
    ]
    
    # 確保在正確的目錄
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    if not os.path.exists("tests"):
        print("❌ 找不到 tests 目錄！")
        return
    
    passed = 0
    total = len(main_tests)
    
    for test_name, test_file in main_tests:
        print(f"\n🚀 執行 {test_name}...")
        print("-" * 40)
        test_path = os.path.join("tests", test_file)
        if not os.path.exists(test_path):
            print(f"❌ 找不到測試檔案: {test_file}")
            continue
        
        try:
            result = subprocess.run([sys.executable, test_path], 
                                  capture_output=True, 
                                  text=True,
                                  cwd=script_dir)  # 設定工作目錄
            
            if result.returncode == 0:
                print(f"✅ {test_name} - 通過")
                passed += 1
            else:
                print(f"❌ {test_name} - 失敗")
                if result.stderr:
                    print(f"錯誤訊息: {result.stderr.strip()[:200]}...")
        except Exception as e:
            print(f"❌ 執行 {test_name} 時發生錯誤: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！Discord Bot 功能正常！")
    else:
        print("⚠️  部分測試失敗，請檢查相關功能")

if __name__ == "__main__":
    main()
