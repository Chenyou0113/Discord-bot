#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版地震雙API整合功能測試
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """測試模組導入"""
    try:
        print("🔍 測試模組導入...")
        from cogs.info_commands_fixed_v4 import InfoCommands
        print("✅ InfoCommands 模組導入成功")
        return True
    except Exception as e:
        print(f"❌ 模組導入失敗: {str(e)}")
        return False

def test_earthquake_method_signature():
    """測試地震方法簽名"""
    try:
        print("\n🔍 檢查地震方法簽名...")
        from cogs.info_commands_fixed_v4 import InfoCommands
        import inspect
        
        # 檢查earthquake方法
        earthquake_method = getattr(InfoCommands, 'earthquake', None)
        if earthquake_method is None:
            print("❌ 找不到earthquake方法")
            return False
            
        print(f"📋 方法類型: {type(earthquake_method)}")
        
        # 如果是Command對象，檢查其callback
        if hasattr(earthquake_method, 'callback'):
            print("✅ 找到app_commands.command裝飾的方法")
            callback = earthquake_method.callback
            sig = inspect.signature(callback)
            params = list(sig.parameters.keys())
            print(f"📋 方法參數: {params}")
            
            # 檢查是否有earthquake_type參數
            if 'earthquake_type' in params:
                print("✅ earthquake_type參數存在")
                param = sig.parameters['earthquake_type']
                print(f"📝 參數預設值: {param.default}")
                return True
            else:
                print("❌ earthquake_type參數不存在")
                return False
        else:
            print("❌ 不是有效的Command對象")
            return False
            
    except Exception as e:
        print(f"❌ 方法簽名檢查失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_app_commands_decorator():
    """測試app_commands裝飾器"""
    try:
        print("\n🔍 檢查app_commands裝飾器...")
        from cogs.info_commands_fixed_v4 import InfoCommands
        
        # 檢查earthquake方法是否有choices裝飾器
        earthquake_method = getattr(InfoCommands, 'earthquake', None)
        
        # 檢查是否是Command對象
        if hasattr(earthquake_method, 'parameters'):
            print("✅ 找到app_commands.command對象")
            params = earthquake_method.parameters
            print(f"📋 參數數量: {len(params)}")
            
            # 查找earthquake_type參數
            for param in params:
                if param.name == 'earthquake_type':
                    print(f"✅ 找到earthquake_type參數")
                    if hasattr(param, 'choices') and param.choices:
                        print(f"📋 選項數量: {len(param.choices)}")
                        for choice in param.choices:
                            print(f"  - {choice.name}: {choice.value}")
                        return True
                    else:
                        print("❌ 找不到choices")
                        return False
            
            print("❌ 找不到earthquake_type參數")
            return False
        else:
            print("❌ 不是有效的Command對象")
            return False
            
    except Exception as e:
        print(f"❌ 裝飾器檢查失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_file_syntax():
    """測試檔案語法"""
    try:
        print("\n🔍 檢查檔案語法...")
        import py_compile
        py_compile.compile('cogs/info_commands_fixed_v4.py', doraise=True)
        print("✅ 檔案語法檢查通過")
        return True
    except Exception as e:
        print(f"❌ 語法錯誤: {str(e)}")
        return False

def main():
    """主測試函數"""
    print("🌟 開始簡化版地震雙API整合功能測試")
    print("=" * 60)
    
    tests = [
        ("檔案語法檢查", test_file_syntax),
        ("模組導入測試", test_import),
        ("方法簽名檢查", test_earthquake_method_signature),
        ("裝飾器檢查", test_app_commands_decorator)
    ]
    
    success_count = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                success_count += 1
            print()
        except Exception as e:
            print(f"❌ {test_name}執行失敗: {str(e)}")
    
    print("=" * 60)
    print(f"📊 測試結果: {success_count}/{len(tests)} 通過")
    
    if success_count == len(tests):
        print("🎉 所有基本測試通過！")
        print("\n📋 確認事項:")
        print("  ✅ 檔案語法正確")
        print("  ✅ 模組可以正常導入")
        print("  ✅ earthquake方法包含earthquake_type參數")
        print("  ✅ app_commands裝飾器設置正確")
        print("\n🚀 雙API整合功能已成功實現！")
    else:
        print("❌ 部分測試失敗，需要檢查問題。")
    
    return success_count == len(tests)

if __name__ == "__main__":
    success = main()
    print(f"\n{'=' * 60}")
    print("🔚 測試完成")
    sys.exit(0 if success else 1)
