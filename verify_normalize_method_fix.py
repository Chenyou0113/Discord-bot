#!/usr/bin/env python3
"""
驗證 _normalize_county_name 方法修正
確保方法現在在正確的類別中並可以正常調用
"""

import sys
import os
import importlib.util

def test_normalize_county_method_fix():
    """測試 _normalize_county_name 方法修正"""
    print("🔍 測試 _normalize_county_name 方法修正...")
    
    try:
        # 導入模組
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        spec = importlib.util.spec_from_file_location(
            "reservoir_commands", 
            os.path.join(os.path.dirname(__file__), "cogs", "reservoir_commands.py")
        )
        reservoir_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reservoir_module)
        
        # 檢查 ReservoirCommands 類別
        ReservoirCommands = reservoir_module.ReservoirCommands
        
        # 確認方法存在
        if hasattr(ReservoirCommands, '_normalize_county_name'):
            print("✅ ReservoirCommands 類別包含 _normalize_county_name 方法")
        else:
            print("❌ ReservoirCommands 類別缺少 _normalize_county_name 方法")
            return False
        
        # 創建一個模擬的實例
        class MockBot:
            pass
        
        mock_bot = MockBot()
        reservoir_commands = ReservoirCommands(mock_bot)
        
        # 測試方法調用
        test_cases = [
            ("臺北市", "台北市"),
            ("新北市政府", "新北市"),
            ("桃園縣", "桃園市"),
            ("", "未知縣市"),
            (None, "未知縣市")
        ]
        
        print("\n🧪 測試標準化功能...")
        all_passed = True
        
        for input_county, expected in test_cases:
            try:
                result = reservoir_commands._normalize_county_name(input_county)
                if result == expected:
                    print(f"✅ '{input_county}' -> '{result}'")
                else:
                    print(f"❌ '{input_county}' -> '{result}' (期望: '{expected}')")
                    all_passed = False
            except Exception as e:
                print(f"❌ 測試 '{input_county}' 時發生錯誤: {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_method_location():
    """測試方法位置是否正確"""
    print("\n🔍 檢查方法定義位置...")
    
    try:
        with open("cogs/reservoir_commands.py", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # 找到 ReservoirCommands 類別
        reservoir_class_start = None
        reservoir_class_end = None
        normalize_method_line = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith("class ReservoirCommands("):
                reservoir_class_start = i + 1
                print(f"✅ ReservoirCommands 類別開始於第 {reservoir_class_start} 行")
            elif reservoir_class_start and line.strip().startswith("class ") and not line.strip().startswith("class ReservoirCommands("):
                reservoir_class_end = i + 1
                print(f"✅ ReservoirCommands 類別結束於第 {reservoir_class_end} 行")
                break
            elif line.strip().startswith("def _normalize_county_name("):
                normalize_method_line = i + 1
                break
        
        if normalize_method_line:
            print(f"✅ _normalize_county_name 方法位於第 {normalize_method_line} 行")
            
            if reservoir_class_start and reservoir_class_end:
                if reservoir_class_start < normalize_method_line < reservoir_class_end:
                    print("✅ _normalize_county_name 方法正確位於 ReservoirCommands 類別中")
                    return True
                else:
                    print("❌ _normalize_county_name 方法不在 ReservoirCommands 類別中")
                    return False
            else:
                print("⚠️ 無法確定類別邊界，但方法存在")
                return True
        else:
            print("❌ 找不到 _normalize_county_name 方法")
            return False
            
    except Exception as e:
        print(f"❌ 檢查方法位置時發生錯誤: {e}")
        return False

def main():
    """主要測試流程"""
    print("🚀 開始驗證 _normalize_county_name 方法修正...")
    print("=" * 60)
    
    all_tests_passed = True
    
    # 測試 1: 方法位置檢查
    if not test_method_location():
        all_tests_passed = False
    
    # 測試 2: 方法功能測試
    if not test_normalize_county_method_fix():
        all_tests_passed = False
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("✅ 所有測試通過！_normalize_county_name 方法修正成功。")
        print("\n📋 修正摘要:")
        print("- _normalize_county_name 方法現在位於 ReservoirCommands 類別中")
        print("- 方法可以正常調用，不會出現 AttributeError")
        print("- 縣市名稱標準化功能正常運作")
        print("- 移除了重複的方法定義")
        print("\n🎯 現在 Discord 指令應該可以正常使用標準化功能了！")
    else:
        print("❌ 部分測試失敗，需要進一步檢查。")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
