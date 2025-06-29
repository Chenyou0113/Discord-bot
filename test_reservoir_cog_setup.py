#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證 reservoir_commands Cog 的 setup 函數是否正確
"""

import sys
import os
import asyncio
import importlib.util

def test_cog_setup():
    """測試 Cog 設置函數"""
    print("=== 測試 reservoir_commands Cog setup 函數 ===")
    
    try:
        # 設置路徑
        cog_path = r"c:\Users\xiaoy\Desktop\Discord bot\cogs\reservoir_commands.py"
        
        # 檢查檔案是否存在
        if not os.path.exists(cog_path):
            print("❌ Cog 檔案不存在")
            return False
            
        # 載入模組
        spec = importlib.util.spec_from_file_location("reservoir_commands", cog_path)
        if spec is None:
            print("❌ 無法建立模組規格")
            return False
            
        module = importlib.util.module_from_spec(spec)
        if module is None:
            print("❌ 無法建立模組")
            return False
            
        # 執行模組
        spec.loader.exec_module(module)
        
        # 檢查是否有 setup 函數
        if hasattr(module, 'setup'):
            print("✅ setup 函數存在")
            
            # 檢查 setup 函數是否為協程函數
            import inspect
            if inspect.iscoroutinefunction(module.setup):
                print("✅ setup 函數是正確的協程函數")
            else:
                print("❌ setup 函數不是協程函數")
                return False
                
        else:
            print("❌ setup 函數不存在")
            return False
            
        # 檢查是否有 ReservoirCommands 類別
        if hasattr(module, 'ReservoirCommands'):
            print("✅ ReservoirCommands 類別存在")
        else:
            print("❌ ReservoirCommands 類別不存在")
            return False
            
        print("✅ Cog 設置測試通過！")
        return True
        
    except SyntaxError as e:
        print(f"❌ 語法錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")
        return False

def test_command_definitions():
    """測試指令定義"""
    print("\n=== 測試指令定義 ===")
    
    try:
        # 讀取檔案內容
        cog_path = r"c:\Users\xiaoy\Desktop\Discord bot\cogs\reservoir_commands.py"
        with open(cog_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 檢查預期的指令
        expected_commands = [
            "@app_commands.command",
            "async def reservoir",
            "async def reservoir_operation", 
            "async def reservoir_info",
            "async def water_cameras",
            "async def reservoir_list"
        ]
        
        for cmd in expected_commands:
            if cmd in content:
                print(f"✅ 找到: {cmd}")
            else:
                print(f"❌ 遺失: {cmd}")
                
        print("✅ 指令定義檢查完成")
        
    except Exception as e:
        print(f"❌ 檢查指令定義時發生錯誤: {e}")

if __name__ == "__main__":
    success = test_cog_setup()
    test_command_definitions()
    
    if success:
        print("\n🎉 所有測試通過！reservoir_commands Cog 已準備就緒。")
    else:
        print("\n❌ 測試失敗，請檢查錯誤訊息。")
