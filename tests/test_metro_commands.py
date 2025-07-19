#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試捷運指令的腳本
"""

import sys
import os
import importlib.util
import inspect

def test_metro_commands():
    """測試捷運指令是否正確添加"""
    try:
        # 載入info_commands模組
        module_path = os.path.join(os.getcwd(), 'cogs', 'info_commands_fixed_v4_clean.py')
        spec = importlib.util.spec_from_file_location("info_commands", module_path)
        module = importlib.util.module_from_spec(spec)
        
        # 檢查模組是否可以正常導入
        spec.loader.exec_module(module)
        
        print("✅ info_commands_fixed_v4_clean.py 模組載入成功")
        
        # 檢查是否有InfoCommands類別
        if hasattr(module, 'InfoCommands'):
            info_class = getattr(module, 'InfoCommands')
            print("✅ InfoCommands 類別存在")
            
            # 檢查新增的方法
            methods_to_check = [
                'get_tdx_access_token',
                'fetch_rail_alerts', 
                'format_rail_alert',
                'fetch_metro_alerts',
                'format_metro_alert',
                'rail_alert',
                'metro_status'
            ]
            
            for method_name in methods_to_check:
                if hasattr(info_class, method_name):
                    method = getattr(info_class, method_name)
                    print(f"✅ 方法 {method_name} 存在")
                    
                    # 檢查是否是 app_commands.command
                    if hasattr(method, '__wrapped__'):
                        print(f"  📝 {method_name} 有裝飾器")
                    
                    # 檢查方法簽名
                    sig = inspect.signature(method)
                    print(f"  📋 {method_name} 參數: {list(sig.parameters.keys())}")
                else:
                    print(f"❌ 方法 {method_name} 不存在")
            
            print("\n🔍 檢查指令裝飾器:")
            # 檢查類別中所有的app_commands
            for name, method in inspect.getmembers(info_class, predicate=inspect.isfunction):
                if hasattr(method, '__wrapped__') or name in ['rail_alert', 'metro_status']:
                    print(f"  🎯 發現指令方法: {name}")
        else:
            print("❌ InfoCommands 類別不存在")
            
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 開始測試捷運指令...")
    test_metro_commands()
    print("\n🏁 測試完成")
