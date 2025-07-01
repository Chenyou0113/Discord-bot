#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試 reservoir_commands 模組
"""

import sys
import os

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_reservoir_commands():
    """測試 reservoir_commands 模組"""
    print("=" * 50)
    print("測試 reservoir_commands 模組")
    print("=" * 50)
    
    try:
        # 檢查檔案
        file_path = 'cogs/reservoir_commands.py'
        if os.path.exists(file_path):
            print(f"✅ 檔案存在: {file_path}")
        else:
            print(f"❌ 檔案不存在: {file_path}")
            return
        
        # 嘗試導入
        print("\n正在導入 reservoir_commands...")
        from cogs import reservoir_commands
        print("✅ 導入成功")
        
        # 檢查類別
        if hasattr(reservoir_commands, 'ReservoirCommands'):
            print("✅ 找到 ReservoirCommands 類別")
        else:
            print("❌ 沒有找到 ReservoirCommands 類別")
            return
        
        # 檢查 setup 函數
        if hasattr(reservoir_commands, 'setup'):
            print("✅ 找到 setup 函數")
        else:
            print("❌ 沒有找到 setup 函數")
            return
        
        # 檢查指令 - 更準確的方式
        reservoir_class = reservoir_commands.ReservoirCommands
        commands = []
        app_commands = []
        
        for attr_name in dir(reservoir_class):
            if attr_name.startswith('_'):
                continue
                
            attr = getattr(reservoir_class, attr_name)
            
            # 檢查是否為 app_command
            if hasattr(attr, '__wrapped__') or hasattr(attr, 'name'):
                if hasattr(attr, 'name'):
                    app_commands.append(attr.name)
                    print(f"  找到 app_command: {attr.name}")
            
            # 檢查是否為傳統指令
            if hasattr(attr, 'name') and hasattr(attr, 'callback'):
                commands.append(attr.name)
        
        print(f"✅ 找到 {len(app_commands)} 個 app_commands:")
        for cmd in app_commands:
            print(f"  - {cmd}")
        
        print(f"✅ 找到 {len(commands)} 個傳統指令:")
        for cmd in commands:
            print(f"  - {cmd}")
        
        # 直接檢查方法名稱
        print(f"\n🔍 方法檢查:")
        methods = ['water_level', 'water_cameras', 'water_disaster_cameras', 
                  'national_highway_cameras', 'general_road_cameras']
        for method_name in methods:
            if hasattr(reservoir_class, method_name):
                method = getattr(reservoir_class, method_name)
                print(f"  ✅ {method_name}: {type(method)}")
                if hasattr(method, 'name'):
                    print(f"    指令名稱: {method.name}")
            else:
                print(f"  ❌ {method_name}: 不存在")
        
        print("\n✅ reservoir_commands 模組測試通過")
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reservoir_commands()
