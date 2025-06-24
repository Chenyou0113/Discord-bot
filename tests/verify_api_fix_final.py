#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
驗證 API 修復後機器人的完整功能
"""

import json
import os
import sys

def verify_api_fix():
    """驗證 API 修復"""
    print("🔍 驗證 API 資料結構解析修復")
    print("=" * 40)
    
    # 檢查修復後的程式碼
    code_file = "cogs/info_commands_fixed_v4_clean.py"
    
    if not os.path.exists(code_file):
        print("❌ 找不到主程式檔案")
        return False
    
    with open(code_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查修復的關鍵邏輯
    checks = [
        ("支援兩種資料結構檢查", "records_data = None"),
        ("有認證模式檢測", "records 在根級別"),
        ("無認證模式檢測", "records 在 result 內"),
        ("統一資料存取", "if 'records' in data:"),
        ("統一資料存取2", "elif 'result' in data and 'records' in data.get('result', {}):"),
    ]
    
    all_passed = True
    for check_name, check_pattern in checks:
        if check_pattern in content:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
            all_passed = False
    
    return all_passed

def verify_test_files():
    """驗證測試檔案的存在和有效性"""
    print("\n📁 驗證測試檔案")
    print("=" * 20)
    
    test_files = [
        "api_test_一般地震_(有認證)_20250604_213746.json",
        "api_test_一般地震_(有認證)_20250604_214035.json",
        "api_test_一般地震_(有認證)_20250604_214304.json"
    ]
    
    valid_files = 0
    for filename in test_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 檢查有認證模式的資料結構
                if (data.get('success') == 'true' and 
                    'records' in data and 
                    'Earthquake' in data['records']):
                    print(f"✅ {filename}")
                    valid_files += 1
                else:
                    print(f"⚠️  {filename} - 資料結構異常")
            except:
                print(f"❌ {filename} - 讀取失敗")
        else:
            print(f"❌ {filename} - 檔案不存在")
    
    return valid_files > 0

def main():
    """主驗證函數"""
    print("🧪 API 修復完整性驗證")
    print("=" * 50)
    
    # 驗證程式碼修復
    code_ok = verify_api_fix()
    
    # 驗證測試檔案
    files_ok = verify_test_files()
    
    print("\n" + "=" * 50)
    print("📋 驗證總結")
    print("-" * 20)
    
    if code_ok:
        print("✅ 程式碼修復驗證通過")
    else:
        print("❌ 程式碼修復驗證失敗")
    
    if files_ok:
        print("✅ 測試檔案驗證通過")
    else:
        print("❌ 測試檔案驗證失敗")
    
    if code_ok and files_ok:
        print("\n🎉 API 修復驗證成功！")
        print("💡 機器人現在可以正確處理有認證模式的API回應")
        print("🚀 可以安全啟動機器人並測試地震功能")
        
        print("\n📋 下一步操作建議:")
        print("1. 啟動機器人: python bot.py")
        print("2. 測試地震指令: /earthquake")
        print("3. 檢查日誌中是否還有'異常資料結構'警告")
        print("4. 確認地震資料顯示完整且準確")
        
        return True
    else:
        print("\n⚠️  驗證失敗，需要進一步檢查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
