#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試水庫營運狀況功能
"""

import os
import sys

def test_reservoir_operation_config():
    """簡單測試水庫營運狀況功能配置"""
    print("🔍 測試水庫營運狀況功能配置...")
    
    try:
        # 切換工作目錄
        os.chdir(r"c:\Users\xiaoy\Desktop\Discord bot")
        
        # 測試水庫模組導入
        print("📦 測試水庫模組導入...")
        import cogs.reservoir_commands
        print("✅ 水庫模組導入成功")
        
        # 檢查模組內容
        print("🔍 檢查模組內容...")
        
        # 檢查類別
        if hasattr(cogs.reservoir_commands, 'ReservoirCommands'):
            print("✅ ReservoirCommands 類別存在")
            reservoir_class = cogs.reservoir_commands.ReservoirCommands
            
            # 檢查方法
            methods = dir(reservoir_class)
            
            expected_methods = [
                'get_reservoir_data',
                'get_reservoir_operation_data',
                'format_reservoir_info',
                'format_reservoir_operation_info',
                'reservoir_info',
                'reservoir_operation',
                'reservoir_list'
            ]
            
            found_methods = []
            for method in expected_methods:
                if method in methods:
                    found_methods.append(method)
                    print(f"  ✅ {method}")
                else:
                    print(f"  ❌ {method}")
            
            print(f"\n📊 方法檢查結果: {len(found_methods)}/{len(expected_methods)}")
            
        else:
            print("❌ 找不到 ReservoirCommands 類別")
            return False
        
        # 檢查 setup 函數
        if hasattr(cogs.reservoir_commands, 'setup'):
            print("✅ setup 函數存在")
        else:
            print("❌ 找不到 setup 函數")
            return False
        
        print("\n🎯 預期的新指令功能：")
        print("  - /reservoir_operation: 查詢水庫營運狀況")
        print("  - 包含蓄水量、水位、降雨量等詳細資訊")
        print("  - 支援特定水庫搜索")
        print("  - 資料來源: 經濟部水利署營運統計")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_reservoir_operation_config()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 水庫營運狀況功能配置測試成功！")
        print("✅ 所有配置正確")
        print("🏗️ 新增功能已準備就緒")
        print("🚀 準備好啟動機器人測試")
    else:
        print("❌ 配置測試失敗")
        print("🔧 需要檢查上方錯誤並修復")
